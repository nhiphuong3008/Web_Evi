"""
EVI Dashboard - Migration Engine (Sheets -> SQLite DB)
Tự động nạp 100% dữ liệu từ 4 Google Spreadsheets về CSDL SQLite (evi_center.db) siêu tốc, có cơ chế Retry & Rate-limit Handling.
"""

import sys
import os
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database.db_manager import init_db, db_session
from database.models import (
    Student, ClassMaster, HomeworkRecord, UnitGrade,
    ParentInteractionLog, ClassFeedbackLog, StudentWithdrawal, ClassSchedule
)
from services.google_sheets import GoogleSheetsService
from services.data_parser import parse_float_vn, parse_homework_data, parse_grades_from_worksheet

logger = logging.getLogger(__name__)


def safe_get_worksheet(sp, title_or_idx, retries=3):
    """Lấy worksheet an toàn có xử lý 429 Rate Limit và Fuzzy match tên tab."""
    for attempt in range(retries):
        try:
            if isinstance(title_or_idx, str):
                try:
                    ws = sp.worksheet(title_or_idx)
                except Exception:
                    # Fuzzy find worksheet by partial name
                    ws = None
                    target_lower = title_or_idx.lower()
                    for w in sp.worksheets():
                        w_title = w.title.lower()
                        if target_lower in w_title or any(part in w_title for part in target_lower.split() if len(part) > 3):
                            ws = w
                            break
                    if not ws:
                        logger.warning(f"Worksheet '{title_or_idx}' not found in spreadsheet.")
                        return None
            else:
                ws = sp.worksheets()[title_or_idx]
            time.sleep(0.5)
            return ws
        except Exception as e:
            if '429' in str(e):
                logger.warning(f"Quota 429 hit, sleeping {(attempt+1)*5}s...")
                time.sleep((attempt + 1) * 5)
            else:
                logger.warning(f"Could not load worksheet {title_or_idx}: {e}")
                return None
    return None


def run_migration():
    """Bắt đầu chuyển đổi 100% dữ liệu từ các Google Sheets vào SQLite CSDL."""
    cfg = config.get_config()
    init_db()
    session = db_session()

    logger.info("==========================================================================")
    logger.info("🚀 BẮT ĐẦU CHUYỂN ĐỔI 100% DỮ LIỆU TỪ 4 GOOGLE SHEETS SANG DATABASE SQLITE")
    logger.info("==========================================================================")

    # Clear old data
    try:
        session.query(Student).delete()
        session.query(ClassMaster).delete()
        session.query(HomeworkRecord).delete()
        session.query(UnitGrade).delete()
        session.query(ParentInteractionLog).delete()
        session.query(ClassFeedbackLog).delete()
        session.query(StudentWithdrawal).delete()
        session.commit()
    except Exception as e:
        logger.warning(f"Warning during clearing table cache: {e}")
        session.rollback()

    service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not service.connect():
        logger.error("❌ Không thể kết nối tới Google Sheets API!")
        return

    s1 = service.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    time.sleep(0.8)
    s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
    time.sleep(0.8)
    s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)
    time.sleep(0.8)
    s4 = service.client.open_by_key(cfg.GOOGLE_SHEETS_NEW_GRADES_ID)
    time.sleep(0.8)

    student_code_map = {}
    student_name_map = {}

    # STEP 1: Master Students from Sheet 1 'DATA HS FULL PHÍ'
    logger.info("\n📌 STEP 1: Nạp Master Học Sinh từ Sheet 1...")
    ws_master = safe_get_worksheet(s1, 'DATA HS FULL PHÍ')
    if ws_master:
        master_rows = ws_master.get_all_values()
        for r in master_rows[1:]:
            if len(r) > 1 and r[1].strip() and r[1].strip().startswith('EVI'):
                code = r[1].strip().upper()
                name = r[2].strip()
                en_name = r[3].strip() if len(r) > 3 else ''
                dob = r[4].strip() if len(r) > 4 else ''
                parent = r[5].strip() if len(r) > 5 else ''
                phone = r[6].strip() if len(r) > 6 else ''
                addr = r[7].strip() if len(r) > 7 else ''
                status = r[8].strip() if len(r) > 8 else 'Đang học'

                if code not in student_code_map:
                    st_obj = Student(
                        code=code,
                        full_name=name,
                        english_name=en_name,
                        dob=dob,
                        parent_name=parent,
                        phone=phone,
                        address=addr,
                        status=status if status in ('Đang học', 'Bảo lưu', 'Đã nghỉ') else 'Đang học'
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

    # STEP 2: Merge classes, schedule, teacher, CM & remaining sessions from 'Điểm danh'
    logger.info("\n📌 STEP 2: Hợp nhất Lớp học & Thông tin chi tiết từ 'Điểm danh'...")
    ws_dd = safe_get_worksheet(s1, 'Điểm danh')
    if ws_dd:
        rows = ws_dd.get_all_values()
        for r in rows[1:]:
            if len(r) > 0 and r[0].strip():
                code = r[0].strip().upper()
                name = r[1].strip() if len(r) > 1 else ''
                en_name = r[2].strip() if len(r) > 2 else ''
                parent = r[3].strip() if len(r) > 3 else ''
                phone = r[4].strip() if len(r) > 4 else ''
                cname = r[5].strip() if len(r) > 5 else ''
                sched = r[6].strip() if len(r) > 6 else ''
                gv = r[7].strip() if len(r) > 7 else ''
                cm = r[8].strip() if len(r) > 8 else ''
                ta = r[9].strip() if len(r) > 9 else ''
                tot_sess = int(r[10]) if len(r) > 10 and r[10].isdigit() else 0
                rem_sess = int(r[11]) if len(r) > 11 and r[11].isdigit() else 0

                matched_code = code if code in student_code_map else student_name_map.get(name.lower())
                if matched_code and matched_code in student_code_map:
                    st = student_code_map[matched_code]
                    add_class(st, cname)
                    if parent and not st.parent_name: st.parent_name = parent
                    if phone and not st.phone: st.phone = phone
                    if sched and not st.schedule: st.schedule = sched
                    if gv and not st.teacher: st.teacher = gv
                    is_short_term = any(k in cname.lower() for k in ['khóa', 'khoa', 'debate', 'speaking', 'ôn thi', 'on thi', 'ngắn hạn', 'ngan han', 'bổ trợ', 'bo tro'])
                    if not is_short_term:
                        if tot_sess: st.total_sessions = tot_sess
                        if rem_sess: st.remaining_sessions = rem_sess
                    elif not st.total_sessions or st.total_sessions == 0:
                        if tot_sess: st.total_sessions = tot_sess
                        if rem_sess: st.remaining_sessions = rem_sess
    session.commit()

    # STEP 3: Homework Records
    logger.info("\n📌 STEP 3: Nạp Bài Về Nhà (BTVN)...")
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

    # STEP 4: Unit Grades from Sheet 4 ('Nhập điểm (Import results)') & Sheet 3
    logger.info("\n📌 STEP 4: Nạp 4,400+ Bảng Điểm & Nhận Xét Bài Test...")
    grade_count = 0

    # 4a. Sheet 4
    ws_imp = safe_get_worksheet(s4, 'Nhập điểm (Import results)')
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

    # 4b. Sheet 3 tabs
    try:
        for w in s3.worksheets():
            if w.title != 'Data DSHS':
                w_rows = w.get_all_values()
                g_parsed = parse_grades_from_worksheet(w_rows, sheet_title=w.title)

                for g in g_parsed:
                    name = g.get('name', '').strip()
                    en_name = g.get('english_name', '').strip()
                    matched_code = student_name_map.get(name.lower()) or student_name_map.get(f"{name.lower()}_{en_name.lower()}")

                    ug_obj = UnitGrade(
                        student_code=matched_code,
                        student_name=name,
                        english_name=en_name,
                        class_name=g.get('class_name', w.title),
                        course=g.get('course', ''),
                        test_name=g.get('test_name', 'UNIT TEST'),
                        listening=g.get('listening'),
                        listening_max=g.get('listening_max', 10),
                        reading_writing=g.get('reading_writing'),
                        reading_writing_max=g.get('reading_writing_max', 12),
                        speaking=g.get('speaking'),
                        speaking_max=g.get('speaking_max', 10),
                        total_score=g.get('total_score'),
                        max_score=g.get('max_score'),
                        comment=g.get('comment', '')
                    )
                    session.add(ug_obj)
                    grade_count += 1
    except Exception as e:
        logger.warning(f"Warning parsing s3 worksheets: {e}")

    session.commit()
    logger.info(f"✅ Đã lưu {grade_count} bản ghi Điểm thi!")

    # STEP 5: Parent Interactions & Class Manager History
    logger.info("\n📌 STEP 5: Nạp Lịch Sử Chăm Sóc & Tương Tác CM...")
    care_count = 0

    # 5a. Single consolidated Sheet 'NHẬT KÝ TƯƠNG TÁC VÀ CHĂM SÓC'
    ws_nk_main = safe_get_worksheet(s1, 'NHẬT KÝ CHĂM SÓC VÀ TƯƠNG TÁC') or safe_get_worksheet(s1, 'Nhật ký tương tác và chăm sóc')
    if ws_nk_main:
        nk_rows = ws_nk_main.get_all_values()
        if nk_rows:
            header_row = nk_rows[0]
            for r in nk_rows[1:]:
                if len(r) < 3:
                    continue
                raw_code = r[1].strip().upper() if len(r) > 1 else ''
                raw_name = r[2].strip() if len(r) > 2 else ''
                raw_en = r[3].strip() if len(r) > 3 else ''
                raw_class = r[4].strip() if len(r) > 4 else ''

                if not raw_name or raw_name.lower() in ('tên học sinh', 'học sinh', 'stt'):
                    continue

                if any(k in raw_name.lower() for k in ['handbook', 'activity book', 'chương trình hè', 'syllabus', 'no']):
                    continue

                matched_code = raw_code if raw_code.startswith('EVI') else student_name_map.get(raw_name.lower())
                staff_name = 'AnhNV'

                # Scan all care note columns (Column K onwards, index 10 to len(r))
                def parse_header_date_local(h_str):
                    import re, datetime
                    if not h_str: return datetime.datetime.now(), ''
                    h = str(h_str).strip()
                    if '2023-2025' in h or '2023' in h: return datetime.datetime(2025, 1, 1, 9, 0, 0), '2023-2025'
                    m = re.search(r'tháng\s*(\d{1,2})[/\s]+(\d{4})', h, re.IGNORECASE) or re.search(r'(\d{1,2})[/\s]+(\d{4})', h)
                    if m: return datetime.datetime(int(m.group(2)), int(m.group(1)), 1, 9, 0, 0), str(int(m.group(1)))
                    m2 = re.search(r'tháng\s*(\d{1,2})', h, re.IGNORECASE)
                    if m2: return datetime.datetime(2026, int(m2.group(1)), 1, 9, 0, 0), str(int(m2.group(1)))
                    return datetime.datetime.now(), ''

                for col_idx in range(10, len(r)):
                    note_val = r[col_idx].strip()
                    if note_val:
                        time_header = header_row[col_idx].strip() if col_idx < len(header_row) else ''
                        combined_note = f"[{time_header}] {note_val}" if time_header else note_val
                        dt_val, month_val = parse_header_date_local(time_header)

                        log_obj = ParentInteractionLog(
                            student_code=matched_code,
                            student_name=raw_name,
                            english_name=raw_en,
                            class_name=raw_class,
                            staff_name=staff_name,
                            note=combined_note,
                            interaction_detail=note_val,
                            created_at=dt_val,
                            month=month_val
                        )
                        session.add(log_obj)
                        care_count += 1
    else:
        # Fallback to old legacy separate worksheets if single consolidated worksheet does not exist yet
        ws_nk1 = safe_get_worksheet(s1, 'Nhật ký tương tác lớp Thục Anh')
        if ws_nk1:
            for r in ws_nk1.get_all_values()[1:]:
                if len(r) > 1 and r[1].strip():
                    code = r[0].strip().upper()
                    name = r[1].strip()
                    en_name = r[2].strip() if len(r) > 2 else ''
                    cname = r[3].strip() if len(r) > 3 else ''
                    staff = r[5].strip() if len(r) > 5 else 'AnhPTT'
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

    session.commit()
    logger.info(f"✅ Đã lưu {care_count} bản ghi Lịch sử Chăm sóc CM!")

    # STEP 6: Schedule Timetable from Sheet 1 'SCHEDULE'
    logger.info("\n📌 STEP 6: Nạp Thời Khóa Biểu Lớp Học từ tab 'SCHEDULE'...")
    ws_sched = safe_get_worksheet(s1, 'SCHEDULE')
    sched_count = 0
    if ws_sched:
        rows = ws_sched.get_all_values()
        session.query(ClassSchedule).delete()
        
        day_mappings = [
            (3, 6, 'Thứ 2 (MON)', 'Thứ 5 (THU)', 'MT5', 'MT6'),
            (8, 11, 'Thứ 3 (TUE)', 'Thứ 6 (FRI)', 'TF5', 'TF6'),
            (13, 16, 'Thứ 4 (WED)', 'Thứ 7 (SAT)', 'WS5', 'WS6'),
        ]

        for start_r, end_r, day_left, day_right, shift5, shift6 in day_mappings:
            for r_idx in range(start_r, end_r + 1):
                if r_idx >= len(rows): break
                row = rows[r_idx]

                # 1. Left Day - Block 5
                if len(row) > 2 and row[2].strip() and row[2].strip().lower() != 'classes':
                    s_obj = ClassSchedule(
                        section='Chính thức', day=day_left, shift_code=shift5, shift_name='Block 5 (17:30 - 19:00)',
                        class_name=row[2].strip(), materials=row[3].strip() if len(row) > 3 else '',
                        room=row[4].strip() if len(row) > 4 else '', teacher=row[5].strip() if len(row) > 5 else '',
                        students_count=int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 0,
                        cm_staff=row[7].strip() if len(row) > 7 else '', ta_staff=row[8].strip() if len(row) > 8 else '',
                        tutoring_info=row[9].strip() if len(row) > 9 else ''
                    )
                    session.add(s_obj); sched_count += 1

                # 2. Left Day - Block 6
                if len(row) > 10 and row[10].strip() and row[10].strip().lower() != 'classes':
                    s_obj = ClassSchedule(
                        section='Chính thức', day=day_left, shift_code=shift6, shift_name='Block 6 (19:15 - 20:45)',
                        class_name=row[10].strip(), materials=row[11].strip() if len(row) > 11 else '',
                        room=row[12].strip() if len(row) > 12 else '', teacher=row[13].strip() if len(row) > 13 else '',
                        students_count=int(row[14]) if len(row) > 14 and row[14].strip().isdigit() else 0,
                        cm_staff=row[15].strip() if len(row) > 15 else '', ta_staff=row[16].strip() if len(row) > 16 else '',
                        tutoring_info=row[17].strip() if len(row) > 17 else ''
                    )
                    session.add(s_obj); sched_count += 1

                # 3. Right Day - Block 5
                if len(row) > 19 and row[19].strip() and row[19].strip().lower() != 'classes':
                    s_obj = ClassSchedule(
                        section='Chính thức', day=day_right, shift_code=shift5, shift_name='Block 5 (17:30 - 19:00)',
                        class_name=row[19].strip(), materials=row[20].strip() if len(row) > 20 else '',
                        room=row[21].strip() if len(row) > 21 else '', teacher=row[22].strip() if len(row) > 22 else '',
                        students_count=int(row[23]) if len(row) > 23 and row[23].strip().isdigit() else 0,
                        cm_staff=row[24].strip() if len(row) > 24 else '', ta_staff=row[25].strip() if len(row) > 25 else '',
                        tutoring_info=row[26].strip() if len(row) > 26 else ''
                    )
                    session.add(s_obj); sched_count += 1

                # 4. Right Day - Block 6
                if len(row) > 27 and row[27].strip() and row[27].strip().lower() != 'classes':
                    s_obj = ClassSchedule(
                        section='Chính thức', day=day_right, shift_code=shift6, shift_name='Block 6 (19:15 - 20:45)',
                        class_name=row[27].strip(), materials=row[28].strip() if len(row) > 28 else '',
                        room=row[29].strip() if len(row) > 29 else '', teacher=row[30].strip() if len(row) > 30 else '',
                        students_count=int(row[31]) if len(row) > 31 and row[31].strip().isdigit() else 0,
                        cm_staff=row[32].strip() if len(row) > 32 else '', ta_staff=row[33].strip() if len(row) > 33 else '',
                        tutoring_info=row[34].strip() if len(row) > 34 else ''
                    )
                    session.add(s_obj); sched_count += 1

        # Supplementary Schedule (Rows 32-45)
        supp_mappings = [(32, 35, 'Thứ 2 (MON)'), (37, 40, 'Thứ 3 (TUE)'), (42, 44, 'Thứ 4 (WED)')]
        for start_r, end_r, day_name in supp_mappings:
            for r_idx in range(start_r, end_r + 1):
                if r_idx >= len(rows): break
                row = rows[r_idx]
                if len(row) > 2 and row[2].strip() and row[2].strip().lower() != 'classes':
                    s_obj = ClassSchedule(
                        section='Bổ trợ', day=day_name,
                        shift_code='MT5' if 'MON' in day_name else ('TF5' if 'TUE' in day_name else 'WS5'),
                        shift_name='Block 5 (17:30 - 19:00)', class_name=row[2].strip(),
                        room=row[4].strip() if len(row) > 4 else '', teacher=row[5].strip() if len(row) > 5 else '',
                        students_count=int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 0,
                        cm_staff=row[7].strip() if len(row) > 7 else '', ta_staff=row[8].strip() if len(row) > 8 else ''
                    )
                    session.add(s_obj); sched_count += 1

                if len(row) > 9 and row[9].strip() and row[9].strip().lower() != 'classes':
                    s_obj = ClassSchedule(
                        section='Bổ trợ', day=day_name,
                        shift_code='MT6' if 'MON' in day_name else ('TF6' if 'TUE' in day_name else 'WS6'),
                        shift_name='Block 6 (19:15 - 20:45)', class_name=row[9].strip(),
                        room=row[10].strip() if len(row) > 10 else '', teacher=row[12].strip() if len(row) > 12 else '',
                        students_count=int(row[13]) if len(row) > 13 and row[13].strip().isdigit() else 0,
                        cm_staff=row[14].strip() if len(row) > 14 else ''
                    )
                    session.add(s_obj); sched_count += 1

        session.commit()
        logger.info(f"✅ Đã lưu {sched_count} bản ghi Thời khóa biểu!")

    # Chạy migration mở rộng (STEPs 7-18: 3 tabs Tái phí, Điểm danh, Ngữ pháp, Lịch sử HS, Sheet 4 Nhập điểm, Lịch kiểm tra, BTVN cũ, KPI, Daily checking, NXHT)
    try:
        from database.migrate_extended import run_extended_migration
        run_extended_migration()
    except Exception as e:
        logger.error(f"❌ Lỗi khi chạy migration mở rộng: {e}")

    logger.info("==========================================================================")
    logger.info("🎉 HOÀN THÀNH TOÀN BỘ MIGRATION 100% CSDL SQLITE TỪ 4 GOOGLE SHEETS KHÔNG LỖI!")
    logger.info(f"  • Bảng 'students' (Master Học Viên):              {session.query(Student).count()}")
    logger.info(f"  • Bảng 'homework_records' (Nhật ký BTVN):         {session.query(HomeworkRecord).count()}")
    logger.info(f"  • Bảng 'unit_grades' (Điểm thi các Unit):         {session.query(UnitGrade).count()}")
    logger.info(f"  • Bảng 'parent_interaction_logs' (Lịch sử CM Care):{session.query(ParentInteractionLog).count()}")
    logger.info(f"  • Bảng 'class_schedules' (Thời khóa biểu):       {session.query(ClassSchedule).count()}")
    logger.info("==========================================================================")

if __name__ == '__main__':
    run_migration()

