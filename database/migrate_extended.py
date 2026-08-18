"""
EVI Dashboard - Extended Migration Engine (Sheets -> SQLite DB)
Nạp DỮ LIỆU MỞ RỘNG từ 4 Google Spreadsheets: 
  - Tái phí (3 tabs), Điểm danh pivot, Ngữ pháp + CLB, 
  - Lịch sử HS tháng (Sheet 4), Nhập điểm (Sheet 4), Lịch kiểm tra, 
  - Level completion, BTVN cũ, KPI, Daily Checking, NXHT tabs
"""

import sys
import os
import time
import re
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database.db_manager import init_db, db_session
from database.models import (
    StudentHistorySnapshot, RenewalDetailLog, MonthlyAttendanceRecord,
    GrammarClubEnrollment, TestScheduleEntry, LevelCompletion,
    KpiMonthlyReport, UnitGrade, HomeworkRecord, ParentInteractionLog,
    ClassFeedbackLog, Student
)
from services.google_sheets import GoogleSheetsService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def safe_get_worksheet(sp, title, retries=3):
    """Lấy worksheet an toàn có xử lý 429 Rate Limit."""
    for attempt in range(retries):
        try:
            ws = sp.worksheet(title)
            time.sleep(0.8)
            return ws
        except Exception as e:
            if '429' in str(e):
                wait = (attempt + 1) * 8
                logger.warning(f"Quota 429 hit for '{title}', sleeping {wait}s...")
                time.sleep(wait)
            else:
                logger.error(f"Error getting worksheet '{title}': {e}")
                return None
    return None


def safe_int(val, default=0):
    """Parse int an toàn."""
    if not val or not str(val).strip():
        return default
    try:
        return int(str(val).strip().replace(',', ''))
    except (ValueError, TypeError):
        return default


def safe_float(val, default=0.0):
    """Parse float an toàn (hỗ trợ dấu phẩy VN)."""
    if not val or not str(val).strip():
        return default
    try:
        return float(str(val).strip().replace(',', '.'))
    except (ValueError, TypeError):
        return default


def run_extended_migration():
    """Nạp toàn bộ dữ liệu mở rộng từ 4 Google Sheets vào SQLite."""
    cfg = config.get_config()
    init_db()
    session = db_session()

    logger.info("=" * 80)
    logger.info("🚀 BẮT ĐẦU MIGRATION MỞ RỘNG - NẠP TOÀN BỘ 4 GOOGLE SHEETS VÀO CSDL")
    logger.info("=" * 80)

    # Clear new tables
    for model in [StudentHistorySnapshot, RenewalDetailLog, MonthlyAttendanceRecord,
                  GrammarClubEnrollment, TestScheduleEntry, LevelCompletion, KpiMonthlyReport]:
        try:
            session.query(model).delete()
        except Exception:
            pass
    session.commit()

    # Connect
    service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not service.connect():
        logger.error("❌ Không thể kết nối tới Google Sheets API!")
        return

    s1 = service.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    time.sleep(1.5)
    s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
    time.sleep(1.5)
    s4 = service.client.open_by_key(cfg.GOOGLE_SHEETS_NEW_GRADES_ID)
    time.sleep(1.5)

    # =========================================================================
    # STEP 7: Nạp renewal_detail_logs từ 3 tabs Tái phí (Sheet 1)
    # =========================================================================
    logger.info("\n📌 STEP 7: Nạp Tái phí (3 tabs) → renewal_detail_logs...")
    renewal_count = 0
    renewal_tabs = [
        ('Tái phí', 'Tái phí 2025'),
        ('Tái phí (từ 6/5/2026)', 'Tái phí (từ 6/5/2026)'),
        ('Tái phí đến 6/2026', 'Tái phí đến 6/2026'),
    ]
    for tab_name, source_label in renewal_tabs:
        ws = safe_get_worksheet(s1, tab_name)
        if not ws:
            logger.warning(f"  ⚠️ Không tìm thấy tab '{tab_name}'")
            continue
        rows = ws.get_all_values()
        time.sleep(1)
        header = rows[0] if rows else []
        logger.info(f"  Tab '{tab_name}': {len(rows)-1} rows, header={header[:15]}")

        for r in rows[1:]:
            code = r[0].strip() if len(r) > 0 else ''
            name = r[1].strip() if len(r) > 1 else ''
            if not code or not code.startswith('EVI'):
                continue
            code = code.upper()
            en_name = r[2].strip() if len(r) > 2 else ''
            cls = r[3].strip() if len(r) > 3 else ''
            sched = r[4].strip() if len(r) > 4 else ''
            teacher = r[5].strip() if len(r) > 5 else ''
            cm = r[6].strip() if len(r) > 6 else ''
            ta = r[7].strip() if len(r) > 7 else ''
            total_s = safe_int(r[8]) if len(r) > 8 else 0
            remain = safe_int(r[9]) if len(r) > 9 else 0
            exp_date = r[10].strip() if len(r) > 10 else ''
            exp_month = r[11].strip() if len(r) > 11 else ''
            exp_year = r[12].strip() if len(r) > 12 else ''
            ren_status = r[13].strip() if len(r) > 13 else ''
            ren_time = r[14].strip() if len(r) > 14 else ''
            # Extra columns for interaction notes (col 15+)
            interaction = ''
            for ci in range(15, min(len(r), 27)):
                if r[ci].strip():
                    interaction += r[ci].strip() + ' | '
            interaction = interaction.rstrip(' | ')

            session.add(RenewalDetailLog(
                student_code=code, student_name=name, english_name=en_name,
                class_name=cls, schedule=sched, teacher=teacher, cm_staff=cm, ta_staff=ta,
                total_sessions=total_s, remaining_sessions=remain,
                expiry_date=exp_date, expiry_month=exp_month, expiry_year=exp_year,
                renewal_status=ren_status, renewal_time=ren_time,
                interaction_note=interaction, source_tab=source_label
            ))
            renewal_count += 1

    session.commit()
    logger.info(f"✅ Đã lưu {renewal_count} bản ghi renewal_detail_logs!")

    # =========================================================================
    # STEP 8: Nạp monthly_attendance_records (unpivot Điểm danh, Sheet 1)
    # =========================================================================
    logger.info("\n📌 STEP 8: Nạp Điểm danh (unpivot 97 cột) → monthly_attendance_records...")
    att_count = 0
    ws_att = safe_get_worksheet(s1, 'Điểm danh')
    if ws_att:
        rows = ws_att.get_all_values()
        time.sleep(1.5)
        header = rows[0] if rows else []
        # Columns 0-14 are student info, columns 15+ are attendance dates
        date_cols = []
        for ci in range(15, len(header)):
            val = header[ci].strip()
            if val:
                date_cols.append((ci, val))

        logger.info(f"  Điểm danh: {len(rows)-2} students, {len(date_cols)} date columns")

        for r in rows[2:]:  # Skip header row + empty row
            code = r[0].strip() if len(r) > 0 else ''
            if not code or not code.startswith('EVI'):
                continue
            code = code.upper()
            name = r[1].strip() if len(r) > 1 else ''
            en_name = r[2].strip() if len(r) > 2 else ''
            cls = r[5].strip() if len(r) > 5 else ''
            sched = r[6].strip() if len(r) > 6 else ''
            teacher = r[7].strip() if len(r) > 7 else ''
            cm = r[8].strip() if len(r) > 8 else ''

            for ci, date_label in date_cols:
                val = r[ci].strip() if ci < len(r) else ''
                if val and val not in ('', '0'):
                    session.add(MonthlyAttendanceRecord(
                        student_code=code, student_name=name, english_name=en_name,
                        class_name=cls, schedule=sched, teacher=teacher, cm_staff=cm,
                        attendance_date=date_label, attendance_value=val
                    ))
                    att_count += 1

        session.commit()
        logger.info(f"✅ Đã lưu {att_count} bản ghi monthly_attendance_records!")
    else:
        logger.warning("  ⚠️ Không tìm thấy tab 'Điểm danh'")

    # =========================================================================
    # STEP 9: Nạp grammar_club_enrollments (Sheet 1)
    # =========================================================================
    logger.info("\n📌 STEP 9: Nạp DS lớp ngữ pháp + CLB → grammar_club_enrollments...")
    gc_count = 0
    ws_gc = safe_get_worksheet(s1, 'DS lớp ngữ pháp + CLB')
    if ws_gc:
        rows = ws_gc.get_all_values()
        time.sleep(1)
        for r in rows[1:]:
            name = r[1].strip() if len(r) > 1 else ''
            if not name:
                continue
            session.add(GrammarClubEnrollment(
                student_name=name,
                english_name=r[2].strip() if len(r) > 2 else '',
                dob=r[3].strip() if len(r) > 3 else '',
                parent_name=r[4].strip() if len(r) > 4 else '',
                phone=r[5].strip() if len(r) > 5 else '',
                main_class=r[0].strip() if len(r) > 0 else '',
                school_grade=r[6].strip() if len(r) > 6 else '',
                grammar_class=r[7].strip() if len(r) > 7 else '',
                speaking_club=r[8].strip() if len(r) > 8 else '',
                note_grammar=r[10].strip() if len(r) > 10 else ''
            ))
            gc_count += 1

        session.commit()
        logger.info(f"✅ Đã lưu {gc_count} bản ghi grammar_club_enrollments!")

    # =========================================================================
    # STEP 10: Nạp student_history_snapshots (Sheet 4 > 'Data', 84 cột)
    # =========================================================================
    logger.info("\n📌 STEP 10: Nạp Lịch sử HS tháng (Sheet 4 Data) → student_history_snapshots...")
    snap_count = 0
    ws_hist = safe_get_worksheet(s4, 'Data')
    if ws_hist:
        rows = ws_hist.get_all_values()
        time.sleep(1.5)
        header_row0 = rows[0] if rows else []
        header_row1 = rows[1] if len(rows) > 1 else []

        # Parse month blocks: each block is 7 columns (mã, tên, nickname, DOB, lớp, GV, CM)
        month_blocks = []
        for ci in range(0, len(header_row0), 7):
            title = header_row0[ci].strip()
            if title and 'DATA' in title.upper():
                # Parse "DATA THÁNG 5/2023" -> month=5, year=2023
                match = re.search(r'(\d+)/(\d+)', title)
                if match:
                    m, y = int(match.group(1)), int(match.group(2))
                    month_blocks.append((ci, m, y))

        logger.info(f"  Phát hiện {len(month_blocks)} blocks tháng: {[(m,y) for _,m,y in month_blocks]}")

        for r in rows[2:]:
            for col_start, month, year in month_blocks:
                code = r[col_start].strip() if col_start < len(r) else ''
                if not code or not code.startswith('EVI'):
                    continue
                code = code.upper()
                name = r[col_start+1].strip() if col_start+1 < len(r) else ''
                en_name = r[col_start+2].strip() if col_start+2 < len(r) else ''
                dob = r[col_start+3].strip() if col_start+3 < len(r) else ''
                cls = r[col_start+4].strip() if col_start+4 < len(r) else ''
                teacher = r[col_start+5].strip() if col_start+5 < len(r) else ''
                cm = r[col_start+6].strip() if col_start+6 < len(r) else ''

                if name:
                    session.add(StudentHistorySnapshot(
                        student_code=code, student_name=name, english_name=en_name,
                        dob=dob, class_name=cls, teacher=teacher, cm_staff=cm,
                        snapshot_month=month, snapshot_year=year,
                        source_sheet='Sheet 4 - Grades Mới - Data'
                    ))
                    snap_count += 1

        session.commit()
        logger.info(f"✅ Đã lưu {snap_count} bản ghi student_history_snapshots!")

    # =========================================================================
    # STEP 11: Nạp grades từ Sheet 4 'Nhập điểm (Import results)' → unit_grades
    # =========================================================================
    logger.info("\n📌 STEP 11: Nạp Nhập điểm (Sheet 4, 4872 rows) → unit_grades...")
    grade_count = 0
    ws_grades = safe_get_worksheet(s4, 'Nhập điểm (Import results)')
    if ws_grades:
        rows = ws_grades.get_all_values()
        time.sleep(1.5)
        # Header ở row 1: Tháng kiểm tra, Mã học viên, Tên, Tiếng Anh, Mã lớp, GV, Bài KT, Tổng điểm, Listening, R&W, Speaking, Nhận xét, THÁNG, NĂM, BỔ TRỢ
        for r in rows[2:]:
            code = r[1].strip() if len(r) > 1 else ''
            if not code or not code.startswith('EVI'):
                continue
            code = code.upper()
            name = r[2].strip() if len(r) > 2 else ''
            en_name = r[3].strip() if len(r) > 3 else ''
            cls = r[4].strip() if len(r) > 4 else ''
            teacher = r[5].strip() if len(r) > 5 else ''
            test_name = r[6].strip() if len(r) > 6 else ''
            total_score = safe_float(r[7]) if len(r) > 7 else None
            listening = safe_float(r[8]) if len(r) > 8 and r[8].strip() else None
            rw = safe_float(r[9]) if len(r) > 9 and r[9].strip() else None
            speaking = safe_float(r[10]) if len(r) > 10 and r[10].strip() else None
            comment = r[11].strip() if len(r) > 11 else ''
            test_month = r[0].strip() if len(r) > 0 else ''

            # Build course from test_month
            course = test_month

            if test_name or total_score:
                session.add(UnitGrade(
                    student_code=code, student_name=name, english_name=en_name,
                    class_name=cls, course=course, test_name=test_name,
                    listening=listening, reading_writing=rw, speaking=speaking,
                    total_score=total_score, comment=comment
                ))
                grade_count += 1

        session.commit()
        logger.info(f"✅ Đã lưu {grade_count} bản ghi unit_grades từ Sheet 4!")

    # =========================================================================
    # STEP 12: Nạp test_schedules (Sheet 4)
    # =========================================================================
    logger.info("\n📌 STEP 12: Nạp Lịch kiểm tra → test_schedules...")
    ts_count = 0
    ws_ts = safe_get_worksheet(s4, 'Nhập lịch kiểm tra')
    if ws_ts:
        rows = ws_ts.get_all_values()
        time.sleep(1)
        for r in rows[1:]:
            test_date = r[0].strip() if len(r) > 0 else ''
            cls_code = r[1].strip() if len(r) > 1 else ''
            if not cls_code or cls_code.startswith('NĂM') or cls_code.startswith('THÁNG'):
                continue
            teacher = r[2].strip() if len(r) > 2 else ''
            stu_count = safe_int(r[3]) if len(r) > 3 else 0
            content = r[4].strip() if len(r) > 4 else ''
            existing = safe_int(r[5]) if len(r) > 5 else 0
            justif = r[6].strip() if len(r) > 6 else ''
            week = r[7].strip() if len(r) > 7 else ''
            month = r[8].strip() if len(r) > 8 else ''
            year = r[9].strip() if len(r) > 9 else ''

            if test_date or content:
                session.add(TestScheduleEntry(
                    test_date=test_date, class_code=cls_code, teacher=teacher,
                    student_count=stu_count, test_content=content,
                    existing_tests_count=existing, justification=justif,
                    week=week, month=month, year=year
                ))
                ts_count += 1

        session.commit()
        logger.info(f"✅ Đã lưu {ts_count} bản ghi test_schedules!")

    # =========================================================================
    # STEP 13: Nạp level_completions (Sheet 4)
    # =========================================================================
    logger.info("\n📌 STEP 13: Nạp Lịch hết trình độ → level_completions...")
    lc_count = 0
    ws_lc = safe_get_worksheet(s4, 'Lịch hết trình độ và họp PH')
    if ws_lc:
        rows = ws_lc.get_all_values()
        time.sleep(1)
        for r in rows[2:]:
            # Find non-empty meaningful rows
            vals = [c.strip() for c in r if c.strip()]
            if len(vals) >= 2:
                session.add(LevelCompletion(
                    class_name=r[0].strip() if len(r) > 0 else '',
                    current_level=r[1].strip() if len(r) > 1 else '',
                    completion_date=r[2].strip() if len(r) > 2 else '',
                    next_level=r[4].strip() if len(r) > 4 else '',
                    meeting_notes=r[5].strip() if len(r) > 5 else ''
                ))
                lc_count += 1

        session.commit()
        logger.info(f"✅ Đã lưu {lc_count} bản ghi level_completions!")

    # =========================================================================
    # STEP 14: Nạp BTVN cũ từ Sheet 1 (3 tabs BTVN)
    # =========================================================================
    logger.info("\n📌 STEP 14: Nạp BTVN cũ (Sheet 1, 3 tabs) → homework_records...")
    btvn_count = 0
    btvn_tabs = [
        ('BTVN - NGỌC LINH', 'Sheet 1 - BTVN Ngọc Linh'),
        ('BTVN tháng 1 - Thục Anh', 'Sheet 1 - BTVN Thục Anh'),
        ('Bài về nhà', 'Sheet 1 - Bài về nhà'),
    ]
    for tab_name, source in btvn_tabs:
        ws = safe_get_worksheet(s1, tab_name)
        if not ws:
            logger.warning(f"  ⚠️ Không tìm thấy tab '{tab_name}'")
            continue
        rows = ws.get_all_values()
        time.sleep(1.5)
        logger.info(f"  Tab '{tab_name}': {len(rows)} rows")

        for r in rows[1:]:
            # Find code column - usually col 1
            code = ''
            date_val = ''
            for ci in range(min(2, len(r))):
                v = r[ci].strip()
                if v.startswith('EVI'):
                    code = v.upper()
                elif '/' in v and len(v) <= 12:
                    date_val = v

            if not code:
                continue

            name = r[2].strip() if len(r) > 2 else ''
            en_name = r[3].strip() if len(r) > 3 else ''
            cls = r[4].strip() if len(r) > 4 else ''

            # Parse BTVN status from columns
            status_parts = []
            for ci in range(5, min(len(r), 12)):
                v = r[ci].strip()
                if v and v.lower() not in ('', 'nan'):
                    status_parts.append(v)
            status_text = ' | '.join(status_parts) if status_parts else ''

            if name or en_name:
                session.add(HomeworkRecord(
                    student_code=code, student_name=name or en_name,
                    english_name=en_name, class_name=cls,
                    submission_date=date_val, status=status_text or 'Imported',
                    teacher_note=f'[{source}]'
                ))
                btvn_count += 1

    session.commit()
    logger.info(f"✅ Đã lưu {btvn_count} bản ghi homework_records (BTVN cũ)!")

    # =========================================================================
    # STEP 15: Nạp kpi_monthly_reports (Sheet 1 > Báo cáo + Dashboard)
    # =========================================================================
    logger.info("\n📌 STEP 15: Nạp KPI Báo cáo → kpi_monthly_reports...")
    kpi_count = 0
    ws_bc = safe_get_worksheet(s1, 'Báo cáo')
    if ws_bc:
        rows = ws_bc.get_all_values()
        time.sleep(1)
        # Row 0: header "BÁO CÁO TỈ LỆ TÁI PHÍ HÀNG THÁNG"
        # Row 1: Tháng, 5, Năm, 2026
        report_month = safe_int(rows[1][1]) if len(rows) > 1 and len(rows[1]) > 1 else 0
        report_year = safe_int(rows[1][3]) if len(rows) > 1 and len(rows[1]) > 3 else 0
        # Row 2: CM, Số HS đến hạn, Tái phí thành công, Chưa tái phí, Thất bại, Tỉ lệ
        for r in rows[3:]:
            cm = r[0].strip() if len(r) > 0 else ''
            if not cm or cm.lower() in ('tổng', 'total', ''):
                # Total row
                if cm.lower() in ('tổng', 'total'):
                    cm = 'TỔNG'
                else:
                    continue

            due = safe_int(r[1]) if len(r) > 1 else 0
            success = safe_int(r[2]) if len(r) > 2 else 0
            pending = safe_int(r[3]) if len(r) > 3 else 0
            failed = safe_int(r[4]) if len(r) > 4 else 0
            rate_raw = r[5].strip() if len(r) > 5 else ''
            rate = safe_float(rate_raw.replace('%', '')) if rate_raw else 0.0

            session.add(KpiMonthlyReport(
                report_type='renewal_rate', cm_staff=cm,
                month=report_month, year=report_year,
                due_count=due, success_count=success,
                pending_count=pending, failed_count=failed,
                rate_percent=rate, raw_value=rate_raw,
                source_tab='Báo cáo'
            ))
            kpi_count += 1

        # Also parse yearly KPI from columns 8+ (BÁO CÁO TỈ LỆ TÁI PHÍ NĂM 2025)
        if len(rows) > 2:
            year_header = rows[2][8:] if len(rows[2]) > 8 else []
            # Year KPI has months as columns from col 9 onwards
            for r in rows[3:]:
                cm = r[0].strip() if len(r) > 0 else ''
                if not cm:
                    continue
                for yi, month_col in enumerate(range(9, min(len(r), 21))):
                    val = r[month_col].strip() if month_col < len(r) else ''
                    if val and val != '0':
                        session.add(KpiMonthlyReport(
                            report_type='renewal_rate_yearly', cm_staff=cm,
                            month=yi + 1, year=2025,
                            raw_value=val, source_tab='Báo cáo - Năm 2025'
                        ))
                        kpi_count += 1

    # Dashboard tab
    ws_dash = safe_get_worksheet(s1, 'Dashboard')
    if ws_dash:
        rows = ws_dash.get_all_values()
        time.sleep(1)
        for r in rows:
            if len(r) > 1 and r[0].strip().startswith('Tháng'):
                month_name = r[0].strip()
                match = re.search(r'(\d+)', month_name)
                month_num = int(match.group(1)) if match else 0
                session.add(KpiMonthlyReport(
                    report_type='dashboard_summary', cm_staff='TỔNG',
                    month=month_num, year=2026,
                    raw_value=f"Điểm danh: {r[1]}, BTVN: {r[2]}, Hoàn thành: {r[3]}, Còn lại: {r[4]}" if len(r) > 4 else '',
                    source_tab='Dashboard'
                ))
                kpi_count += 1

    session.commit()
    logger.info(f"✅ Đã lưu {kpi_count} bản ghi kpi_monthly_reports!")

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
        # Month columns start from col 10+
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

            # Old interaction (col 10)
            old_note = r[10].strip() if len(r) > 10 else ''
            if old_note:
                session.add(ParentInteractionLog(
                    student_code=code, student_name=name, english_name=en_name,
                    class_name=cls, staff_name='Thục Anh',
                    month='Tương tác cũ', note=old_note
                ))
                pi_count += 1

            # Monthly interactions
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

            # Học lực (col 8) & Tình trạng PH (col 9) → bổ sung vào Student
            academic = r[8].strip() if len(r) > 8 else ''
            parent_att = r[9].strip() if len(r) > 9 else ''

            # Update student's academic_level & parent_attitude
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
            # Amber tab format: col0=Ca-Lớp, col1=STT, col2=name, col3=nickname, col4=học lực, col5=PH
            cls_val = r[0].strip() if len(r) > 0 else ''
            if cls_val and len(cls_val) > 5:
                current_class = cls_val.split('\n')[0].strip() if '\n' in cls_val else cls_val
            name = r[2].strip() if len(r) > 2 else ''
            en_name = r[3].strip() if len(r) > 3 else ''
            if not name:
                continue

            academic = r[4].strip() if len(r) > 4 else ''
            parent_att = r[5].strip() if len(r) > 5 else ''

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
    # STEP 17: Nạp 14 tabs NXHT * → class_feedback_logs (Sheet 2)
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

            # Row 1 is header: Mã HS, Full name, English name, Feedback, Main content, OM CHECK
            # Row 2+ alternate between date rows and data rows
            current_date = ''
            for r in rows[2:]:
                first_col = r[0].strip() if len(r) > 0 else ''
                # Check if this is a date row
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

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
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
    run_extended_migration()
