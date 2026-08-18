import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService
from database.db_manager import db_session, init_db
from database.models import Student, ParentInteractionLog

def check():
    init_db()
    session = db_session()
    st = session.query(Student).filter(Student.code == 'EVI056').first()
    if st:
        print(f"DB Student EVI056:")
        print(f"  code: {st.code}")
        print(f"  full_name: {st.full_name}")
        print(f"  english_name: {st.english_name}")
        print(f"  class_name: '{st.class_name}'")
        print(f"  total_sessions: {st.total_sessions}")
        print(f"  remaining_sessions: {st.remaining_sessions}")

    cm_logs = session.query(ParentInteractionLog).filter(ParentInteractionLog.student_code == 'EVI056').all()
    print(f"\nParentInteractionLog for EVI056 ({len(cm_logs)} records):")
    for c in cm_logs:
        print(f"  - Staff: {c.staff_name} | Note: {c.note}")

    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if svc.connect():
        sp1 = svc.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
        ws_dd = sp1.worksheet('Điểm danh')
        rows = ws_dd.get_all_values()
        print(f"\nAll rows for EVI056 in 'Điểm danh' tab:")
        for idx, r in enumerate(rows):
            if len(r) > 0 and 'evi056' in r[0].lower():
                print(f"  Row {idx+1}: {r[:14]}")

if __name__ == '__main__':
    check()
