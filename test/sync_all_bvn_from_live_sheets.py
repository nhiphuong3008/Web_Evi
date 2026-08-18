import os
import sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import get_config
from services.google_sheets import GoogleSheetsService
from database.db_manager import db_session
from database.models import AttendanceRecord, Student

def parse_date(date_str):
    """Normalize date DD/MM/YYYY to YYYY-MM-DD."""
    if not date_str:
        return ''
    date_str = str(date_str).strip()
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
    if m:
        day, month, year = m.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return date_str

def sync_all_bvn():
    config = get_config()
    target_id = "1wKcmRH9azv9urXvp-Ld4zWwmZ-iuGA2Vo30WzEkBR1I"
    svc = GoogleSheetsService(config.GOOGLE_SHEETS_CREDENTIALS_FILE, target_id)
    if not svc.connect():
        print("[FAIL] Cannot connect to Google Sheets using credentials!")
        return

    print("[SUCCESS] Connected to Google Sheets! Reading 'Nhap KQ BVN' tab...")
    ws = svc.spreadsheet.worksheet("Nhập KQ BVN")
    all_vals = ws.get_all_values()
    print(f"Total raw rows: {len(all_vals)}")

    session = db_session()
    synced_count = 0
    updated_count = 0

    for idx, row in enumerate(all_vals[3:], start=4):
        if len(row) < 12:
            continue

        raw_date = row[0].strip()
        st_code = row[1].strip()
        st_name = row[2].strip()
        class_name = row[5].strip()

        if not raw_date or not st_name:
            continue

        att_date = parse_date(raw_date)
        if not att_date:
            continue

        # Extract BVN fields
        score_str = row[8].strip().replace(',', '.') if len(row) > 8 else ''
        tot_str = row[9].strip() if len(row) > 9 else ''
        corr_str = row[10].strip() if len(row) > 10 else ''
        sub_status = row[11].strip() if len(row) > 11 else ''
        comment = row[13].strip() if len(row) > 13 else ''

        # Map submission status to standard attendance status
        att_status = 'Có mặt'
        if 'Nghỉ' in sub_status or 'nghỉ' in sub_status:
            att_status = 'Vắng có phép'
        elif sub_status == 'Không làm':
            att_status = 'Có mặt'

        hw_tot = int(tot_str) if tot_str.isdigit() else None
        hw_corr = int(corr_str) if corr_str.isdigit() else None
        try:
            hw_score = float(score_str) if score_str else None
        except ValueError:
            hw_score = None

        if hw_score is None and hw_corr is not None and hw_tot is not None and hw_tot > 0:
            hw_score = round((hw_corr / hw_tot) * 10.0, 1)

        # Check existing record
        att = session.query(AttendanceRecord).filter(
            AttendanceRecord.attendance_date == att_date,
            AttendanceRecord.student_name == st_name
        ).first()

        if not att and st_code:
            att = session.query(AttendanceRecord).filter(
                AttendanceRecord.attendance_date == att_date,
                AttendanceRecord.student_code == st_code
            ).first()

        if not att:
            att = AttendanceRecord(
                class_name=class_name or 'Chưa phân lớp',
                attendance_date=att_date,
                student_code=st_code,
                student_name=st_name,
                status=att_status
            )
            session.add(att)
            synced_count += 1
        else:
            updated_count += 1

        if class_name:
            att.class_name = class_name
        att.status = att_status
        att.hw_total_questions = hw_tot
        att.hw_correct_answers = hw_corr
        att.hw_score = hw_score
        att.hw_submission_status = sub_status or 'Nộp đúng giờ'
        att.hw_comment = comment

    session.commit()
    print(f"[SUCCESS] Synced total {synced_count + updated_count} BTVN records ({synced_count} new, {updated_count} updated) into SQLite!")
    session.close()

if __name__ == '__main__':
    sync_all_bvn()
