import sys
import os
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from database.db_manager import init_db, db_session
from database.models import (
    Student, ClassMaster, HomeworkRecord, UnitGrade,
    ParentInteractionLog, ClassFeedbackLog, StudentWithdrawal
)
from services.google_sheets import GoogleSheetsService
from services.data_parser import parse_float_vn, parse_homework_data, parse_grades_from_worksheet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_get_worksheet(sp, title_or_idx, retries=3):
    for attempt in range(retries):
        try:
            if isinstance(title_or_idx, str):
                ws = sp.worksheet(title_or_idx)
            else:
                ws = sp.worksheets()[title_or_idx]
            time.sleep(0.5)
            return ws
        except Exception as e:
            if '429' in str(e):
                logger.warning(f"Quota 429 hit, sleeping {(attempt+1)*5}s...")
                time.sleep((attempt + 1) * 5)
            else:
                raise e
    return None

def run_robust_migration():
    cfg = config.get_config()
    init_db()
    session = db_session()

    # Clear existing data cleanly
    session.query(Student).delete()
    session.query(ClassMaster).delete()
    session.query(HomeworkRecord).delete()
    session.query(UnitGrade).delete()
    session.query(ParentInteractionLog).delete()
    session.query(ClassFeedbackLog).delete()
    session.query(StudentWithdrawal).delete()
    session.commit()

    service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not service.connect():
        logger.error("Failed to connect to Google Sheets Service")
        return

    s1 = service.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    time.sleep(1)
    s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
    time.sleep(1)
    s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)
    time.sleep(1)
    s4 = service.client.open_by_key(cfg.GOOGLE_SHEETS_NEW_GRADES_ID)
    time.sleep(1)

    student_code_map = {}
    student_name_map = {}

    # STEP 1: Master Students from Sheet 1 'DATA HS FULL PHÍ'
    logger.info("📌 STEP 1: Nạp Master Học Sinh từ Sheet 1...")
    ws_master = safe_get_worksheet(s1, 'DATA HS FULL PHÍ')
    master_rows = ws_master.get_all_values()

    for r in master_rows[2:]:
        if len(r) > 1 and r[1].strip() and r[1].strip().startswith('EVI'):
            code = r[1].strip().upper()
            name = r[2].strip()
            en_name = r[3].strip() if len(r) > 3 else ''
            cname = r[4].strip() if len(r) > 4 else ''
            dob = r[5].strip() if len(r) > 5 else ''
            schedule = r[7].strip() if len(r) > 7 else ''
            room = r[8].strip() if len(r) > 8 else ''
            gv = r[9].strip() if len(r) > 9 else ''
            cm = r[10].strip() if len(r) > 10 else ''
            parent = r[12].strip() if len(r) > 12 else ''
            phone = r[13].strip() if len(r) > 13 else ''
            addr = r[14].strip() if len(r) > 14 else ''

            if code not in student_code_map:
                st_obj = Student(
                    code=code,
                    full_name=name,
                    english_name=en_name,
                    class_name=cname,
                    dob=dob,
                    schedule=schedule,
                    room=room,
                    teacher=gv,
                    cm_staff=cm,
                    parent_name=parent,
                    phone=phone,
                    address=addr,
                    status='Đang học'
                )
                session.add(st_obj)
                student_code_map[code] = st_obj

            student_name_map[name.lower()] = code
            if en_name:
                student_name_map[f"{name.lower()}_{en_name.lower()}"] = code

    session.commit()
    logger.info(f"✅ Đã nạp {len(student_code_map)} học sinh Master!")

    def add_class(st, new_cname):
        if not new_cname: return
        curr = [c.strip() for c in (st.class_name or '').split(',') if c.strip()]
        for nc in new_cname.split(','):
            nc_clean = nc.strip()
            if nc_clean and nc_clean not in curr and nc_clean not in ('Bảo lưu', 'Đã nghỉ'):
                curr.append(nc_clean)
        st.class_name = ", ".join(curr)

    # STEP 2: Merge classes from 'Điểm danh'
    logger.info("📌 STEP 2: Hợp nhất Lớp học từ 'Điểm danh'...")
    ws_dd = safe_get_worksheet(s1, 'Điểm danh')
    if ws_dd:
        rows = ws_dd.get_all_values()
        for r in rows[1:]:
            if len(r) > 1 and r[1].strip():
                code = r[1].strip().upper()
                name = r[2].strip()
                cname = r[4].strip() if len(r) > 4 else ''
                matched_code = code if code in student_code_map else student_name_map.get(name.lower())
                if matched_code and matched_code in student_code_map:
                    add_class(student_code_map[matched_code], cname)
    session.commit()

    # STEP 3: Homework Records
    logger.info("📌 STEP 3: Nạp Bài Về Nhà (BTVN)...")
    ws_hw = safe_get_worksheet(s2, 'Nhập KQ BVN')
    if ws_hw:
        raw_btvn = ws_hw.get_all_values()
        parsed_hw = parse_homework_data(raw_btvn)
        hw_count = 0
        for h in parsed_hw:
            code = h.get('code', '').strip().upper()
            name = h.get('name', '').strip()
            matched_code = code if code in student_code_map else student_name_map.get(name.lower())

            hw_obj = HomeworkRecord(
                student_code=matched_code,
                student_name=name,
                english_name=h.get('english_name', ''),
                class_name=h.get('phone_class', ''),
                phone=h.get('phone', ''),
                schedule=h.get('schedule', ''),
                submission_date=h.get('date', ''),
                status=h.get('status', 'Chưa nộp BTVN'),
                score=h.get('score', ''),
                score_num=h.get('score_num', 0.0),
                total_questions=h.get('total_questions', '')
            )
            session.add(hw_obj)
            hw_count += 1
        session.commit()
        logger.info(f"✅ Đã lưu {hw_count} bản ghi BTVN!")

    # STEP 4: Unit Grades from Sheet 4 ('Nhập điểm (Import results)')
    logger.info("📌 STEP 4: Nạp 4,400+ Bảng Điểm & Nhận Xét Bài Test...")
    ws_imp = safe_get_worksheet(s4, 'Nhập điểm (Import results)')
    grade_count = 0
    if ws_imp:
        imp_rows = ws_imp.get_all_values()
        for r in imp_rows[2:]:
            if len(r) > 1 and r[1].strip() and r[1].strip().startswith('EVI'):
                st_code = r[1].strip().upper()
                name = r[2].strip() if len(r) > 2 else ''
                en_name = r[3].strip() if len(r) > 3 else ''
                cname = r[4].strip() if len(r) > 4 else ''
                gv = r[5].strip() if len(r) > 5 else ''
                test_name = r[6].strip() if len(r) > 6 else ''
                tot_sc = parse_float_vn(r[7]) if len(r) > 7 else None
                lis_sc = parse_float_vn(r[8]) if len(r) > 8 and r[8].strip() else None
                rw_sc = parse_float_vn(r[9]) if len(r) > 9 and r[9].strip() else None
                spk_sc = parse_float_vn(r[10]) if len(r) > 10 and r[10].strip() else None
                comment = r[11].strip() if len(r) > 11 else ''

                matched_code = st_code if st_code in student_code_map else student_name_map.get(name.lower())

                ug_obj = UnitGrade(
                    student_code=matched_code,
                    student_name=name or (student_code_map[matched_code].full_name if matched_code in student_code_map else ''),
                    english_name=en_name,
                    class_name=cname,
                    course=gv,
                    test_name=test_name or 'Bài kiểm tra',
                    listening=lis_sc,
                    listening_max=10.0,
                    reading_writing=rw_sc,
                    reading_writing_max=10.0 if rw_sc and rw_sc <= 10.0 else 12.0,
                    speaking=spk_sc,
                    speaking_max=10.0,
                    total_score=tot_sc,
                    max_score=10.0,
                    comment=comment
                )
                session.add(ug_obj)
                grade_count += 1
    session.commit()
    logger.info(f"✅ Đã lưu {grade_count} bản ghi Điểm thi!")

    # STEP 5: Parent Interactions & Class Manager History
    logger.info("📌 STEP 5: Nạp Lịch Sử Chăm Sóc & Tương Tác CM...")
    care_count = 0
    # 5a. Sheet 1 'Nhật ký tương tác lớp Thục Anh'
    ws_nk1 = safe_get_worksheet(s1, 'Nhật ký tương tác lớp Thục Anh')
    if ws_nk1:
        for r in ws_nk1.get_all_values()[1:]:
            if len(r) > 1 and r[1].strip():
                code = r[0].strip().upper()
                name = r[1].strip()
                en_name = r[2].strip() if len(r) > 2 else ''
                cname = r[3].strip() if len(r) > 3 else ''
                staff = r[5].strip() if len(r) > 5 else 'Thục Anh'
                note = r[12].strip() if len(r) > 12 and r[12].strip() else (r[8].strip() if len(r) > 8 else '')
                matched_code = code if code in student_code_map else student_name_map.get(name.lower())

                if note:
                    log_obj = ParentInteractionLog(
                        student_code=matched_code,
                        student_name=name,
                        english_name=en_name,
                        class_name=cname,
                        staff_name=staff,
                        note=note
                    )
                    session.add(log_obj)
                    care_count += 1

    # 5b. Sheet 1 '(Amber) Daily checking'
    ws_amb = safe_get_worksheet(s1, '(Amber) Daily checking')
    if ws_amb:
        for r in ws_amb.get_all_values()[1:]:
            if len(r) > 3 and r[2].strip():
                name = r[2].strip()
                en_name = r[3].strip() if len(r) > 3 else ''
                academic_note = r[4].strip() if len(r) > 4 else ''
                care_note = r[5].strip() if len(r) > 5 else ''
                combined_note = f"Tình hình học tập: {academic_note}" + (f" | Lịch sử chăm sóc PH: {care_note}" if care_note else "")
                matched_code = student_name_map.get(name.lower())

                if combined_note.strip():
                    log_obj = ParentInteractionLog(
                        student_code=matched_code,
                        student_name=name,
                        english_name=en_name,
                        staff_name='Amber',
                        note=combined_note
                    )
                    session.add(log_obj)
                    care_count += 1

    # 5c. Sheet 1 '(Naomi) Daily Checking'
    ws_nao = safe_get_worksheet(s1, '(Naomi) Daily Checking')
    if ws_nao:
        for r in ws_nao.get_all_values()[1:]:
            if len(r) > 3 and r[2].strip():
                name = r[2].strip()
                en_name = r[3].strip() if len(r) > 3 else ''
                academic_note = r[4].strip() if len(r) > 4 else ''
                care_note = r[5].strip() if len(r) > 5 else ''
                combined_note = f"Tình hình học tập: {academic_note}" + (f" | Lịch sử chăm sóc PH: {care_note}" if care_note else "")
                matched_code = student_name_map.get(name.lower())

                if combined_note.strip():
                    log_obj = ParentInteractionLog(
                        student_code=matched_code,
                        student_name=name,
                        english_name=en_name,
                        staff_name='Naomi',
                        note=combined_note
                    )
                    session.add(log_obj)
                    care_count += 1

    session.commit()
    logger.info(f"✅ Đã lưu {care_count} bản ghi Lịch sử Chăm sóc CM!")

    print("\n" + "=" * 60)
    print(" 🎉 MIGRATION HOÀN THÀNH 100% VÀO CSDL SQLITE!")
    print(f"   • Học sinh Master (students): {session.query(Student).count()}")
    print(f"   • Nhật ký BTVN (homework_records): {session.query(HomeworkRecord).count()}")
    print(f"   • Điểm thi các Unit (unit_grades): {session.query(UnitGrade).count()}")
    print(f"   • Lịch sử Chăm sóc CM (parent_interaction_logs): {session.query(ParentInteractionLog).count()}")
    print("=" * 60)

if __name__ == '__main__':
    run_robust_migration()
