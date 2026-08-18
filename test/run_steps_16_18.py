"""
Chạy lại STEPs 16-18 của Extended Migration (bị lỗi do thiếu cột students).
"""
import sys, os, time, logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from database.db_manager import init_db, db_session
from database.models import (
    Student, ParentInteractionLog, ClassFeedbackLog
)
from services.google_sheets import GoogleSheetsService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def safe_get_worksheet(sp, title, retries=3):
    for attempt in range(retries):
        try:
            ws = sp.worksheet(title)
            time.sleep(0.8)
            return ws
        except Exception as e:
            if '429' in str(e):
                time.sleep((attempt + 1) * 8)
            else:
                logger.error(f"Error getting worksheet '{title}': {e}")
                return None
    return None


def run_steps_16_18():
    cfg = config.get_config()
    init_db()
    session = db_session()

    service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not service.connect():
        logger.error("❌ Không thể kết nối tới Google Sheets API!")
        return

    s1 = service.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    time.sleep(1.5)
    s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
    time.sleep(1.5)

    # =========================================================================
    # STEP 16: Bổ sung parent_interaction_logs (3 tabs Daily Checking, Sheet 1)
    # =========================================================================
    logger.info("\n📌 STEP 16: Bổ sung parent_interaction_logs (3 tabs)...")
    pi_count = 0

    # Tab: Nhật ký tương tác lớp Thục Anh
    ws_ta = safe_get_worksheet(s1, 'Nhật ký tương tác lớp Thục Anh')
    if ws_ta:
        rows = ws_ta.get_all_values()
        time.sleep(1.5)
        header = rows[0] if rows else []
        month_cols = []
        for ci in range(10, len(header)):
            val = header[ci].strip()
            if val and ('Tương tác' in val or 'Tháng' in val):
                month_cols.append((ci, val))

        for r in rows[2:]:
            code = r[1].strip() if len(r) > 1 else ''
            if not code or not code.startswith('EVI'):
                continue
            code = code.upper()
            name = r[2].strip() if len(r) > 2 else ''
            en_name = r[3].strip() if len(r) > 3 else ''
            cls = r[4].strip() if len(r) > 4 else ''

            old_note = r[10].strip() if len(r) > 10 else ''
            if old_note:
                session.add(ParentInteractionLog(
                    student_code=code, student_name=name, english_name=en_name,
                    class_name=cls, staff_name='Thục Anh',
                    month='Tương tác cũ', note=old_note
                ))
                pi_count += 1

            for ci, month_label in month_cols:
                val = r[ci].strip() if ci < len(r) else ''
                if val:
                    session.add(ParentInteractionLog(
                        student_code=code, student_name=name, english_name=en_name,
                        class_name=cls, staff_name='Thục Anh',
                        month=month_label, note=val
                    ))
                    pi_count += 1

    # Tab: (Naomi) Daily Checking
    ws_naomi = safe_get_worksheet(s1, '(Naomi) Daily Checking')
    if ws_naomi:
        rows = ws_naomi.get_all_values()
        time.sleep(1.5)
        header = rows[1] if len(rows) > 1 else []
        month_cols = []
        for ci in range(10, len(header)):
            val = header[ci].strip()
            if val and 'Tương tác' in val:
                month_cols.append((ci, val))

        for r in rows[2:]:
            code = r[0].strip() if len(r) > 0 else ''
            if not code or not code.startswith('EVI'):
                continue
            code = code.upper()
            name = r[1].strip() if len(r) > 1 else ''
            en_name = r[2].strip() if len(r) > 2 else ''
            cls = r[5].strip() if len(r) > 5 else ''

            academic = r[8].strip() if len(r) > 8 else ''
            parent_att = r[9].strip() if len(r) > 9 else ''

            if academic or parent_att:
                student = session.query(Student).filter_by(code=code).first()
                if student:
                    if academic:
                        student.academic_level = academic
                    if parent_att:
                        student.parent_attitude = parent_att

            for ci, month_label in month_cols:
                val = r[ci].strip() if ci < len(r) else ''
                if val:
                    session.add(ParentInteractionLog(
                        student_code=code, student_name=name, english_name=en_name,
                        class_name=cls, staff_name='Naomi',
                        month=month_label, note=val
                    ))
                    pi_count += 1

    # Tab: (Amber) Daily checking
    ws_amber = safe_get_worksheet(s1, '(Amber) Daily checking')
    if ws_amber:
        rows = ws_amber.get_all_values()
        time.sleep(1.5)
        header = rows[0] if rows else []
        month_cols = []
        for ci in range(6, len(header)):
            val = header[ci].strip()
            if val and ('Nhật ký' in val or 'Tương tác' in val or 'Tháng' in val):
                month_cols.append((ci, val))

        current_class = ''
        for r in rows[2:]:
            cls_val = r[0].strip() if len(r) > 0 else ''
            if cls_val and len(cls_val) > 5:
                current_class = cls_val.split('\n')[0].strip() if '\n' in cls_val else cls_val
            name = r[2].strip() if len(r) > 2 else ''
            en_name = r[3].strip() if len(r) > 3 else ''
            if not name:
                continue

            for ci, month_label in month_cols:
                val = r[ci].strip() if ci < len(r) else ''
                if val:
                    session.add(ParentInteractionLog(
                        student_name=name, english_name=en_name,
                        class_name=current_class, staff_name='Amber',
                        month=month_label, note=val
                    ))
                    pi_count += 1

    session.commit()
    logger.info(f"✅ Đã lưu {pi_count} bản ghi parent_interaction_logs!")

    # =========================================================================
    # STEP 17: Nạp 14 tabs NXHT → class_feedback_logs (Sheet 2)
    # =========================================================================
    logger.info("\n📌 STEP 17: Nạp 14 tabs NXHT → class_feedback_logs (Sheet 2)...")
    cf_count = 0
    all_tabs = s2.worksheets()
    time.sleep(1)
    nxht_tabs = [ws for ws in all_tabs if ws.title.startswith('NXHT')]
    logger.info(f"  Phát hiện {len(nxht_tabs)} tabs NXHT")

    for nxht_ws in nxht_tabs:
        try:
            rows = nxht_ws.get_all_values()
            time.sleep(1.5)
            tab_name = nxht_ws.title
            class_name_label = rows[0][0].strip() if rows and rows[0] else tab_name

            current_date = ''
            for r in rows[2:]:
                first_col = r[0].strip() if len(r) > 0 else ''
                if first_col and ('/' in first_col or 'Thứ' in first_col) and not first_col.startswith('EVI'):
                    current_date = first_col
                    continue

                code = first_col if first_col.startswith('EVI') else ''
                name = r[1].strip() if len(r) > 1 else ''
                en_name = r[2].strip() if len(r) > 2 else ''
                feedback = r[3].strip() if len(r) > 3 else ''
                content = r[4].strip() if len(r) > 4 else ''

                if (name or code) and (feedback or content):
                    lesson = current_date if current_date else ''
                    full_feedback = ''
                    if content:
                        full_feedback += f"[Nội dung bài học] {content}"
                    if feedback:
                        if full_feedback:
                            full_feedback += '\n'
                        full_feedback += f"[Nhận xét] {feedback}"

                    session.add(ClassFeedbackLog(
                        class_name=class_name_label,
                        student_name=name, english_name=en_name,
                        lesson_name=lesson,
                        feedback_content=full_feedback
                    ))
                    cf_count += 1

        except Exception as e:
            logger.error(f"  ❌ Error processing tab '{nxht_ws.title}': {e}")
            time.sleep(3)

    session.commit()
    logger.info(f"✅ Đã lưu {cf_count} bản ghi class_feedback_logs!")

    # =========================================================================
    # STEP 18: Bổ sung thông tin HV 2012-2015 vào Student (Sheet 1)
    # =========================================================================
    logger.info("\n📌 STEP 18: Bổ sung thông tin học lực/PH từ tabs HV 2012-2015...")
    hv_count = 0
    for tab_name in ['HV 2012, 2013', 'HV 2014, 2015']:
        ws_hv = safe_get_worksheet(s1, tab_name)
        if not ws_hv:
            continue
        rows = ws_hv.get_all_values()
        time.sleep(1)
        for r in rows[1:]:
            code = r[0].strip() if len(r) > 0 else ''
            if not code or not code.startswith('EVI'):
                continue
            code = code.upper()
            year_birth = r[5].strip() if len(r) > 5 else ''
            age_val = r[6].strip() if len(r) > 6 else ''
            academic = r[8].strip() if len(r) > 8 else ''
            parent_att = r[9].strip() if len(r) > 9 else ''

            student = session.query(Student).filter_by(code=code).first()
            if student:
                if year_birth:
                    student.year_of_birth = year_birth
                if age_val:
                    student.age = age_val
                if academic:
                    student.academic_level = academic
                if parent_att:
                    student.parent_attitude = parent_att
                hv_count += 1

    session.commit()
    logger.info(f"✅ Đã cập nhật {hv_count} học sinh với thông tin HV 2012-2015!")

    # FINAL SUMMARY
    from database.models import (
        RenewalDetailLog, MonthlyAttendanceRecord, GrammarClubEnrollment,
        StudentHistorySnapshot, UnitGrade, TestScheduleEntry, LevelCompletion,
        HomeworkRecord, KpiMonthlyReport
    )
    logger.info("\n" + "=" * 80)
    logger.info("🎉 HOÀN THÀNH MIGRATION MỞ RỘNG - TOÀN BỘ 4 GOOGLE SHEETS!")
    logger.info("=" * 80)
    logger.info(f"  • renewal_detail_logs:         {session.query(RenewalDetailLog).count()}")
    logger.info(f"  • monthly_attendance_records:  {session.query(MonthlyAttendanceRecord).count()}")
    logger.info(f"  • grammar_club_enrollments:    {session.query(GrammarClubEnrollment).count()}")
    logger.info(f"  • student_history_snapshots:   {session.query(StudentHistorySnapshot).count()}")
    logger.info(f"  • unit_grades (total):         {session.query(UnitGrade).count()}")
    logger.info(f"  • test_schedules:              {session.query(TestScheduleEntry).count()}")
    logger.info(f"  • level_completions:           {session.query(LevelCompletion).count()}")
    logger.info(f"  • homework_records (total):    {session.query(HomeworkRecord).count()}")
    logger.info(f"  • kpi_monthly_reports:         {session.query(KpiMonthlyReport).count()}")
    logger.info(f"  • parent_interaction_logs:     {session.query(ParentInteractionLog).count()}")
    logger.info(f"  • class_feedback_logs:         {session.query(ClassFeedbackLog).count()}")
    logger.info("=" * 80)


if __name__ == '__main__':
    run_steps_16_18()
