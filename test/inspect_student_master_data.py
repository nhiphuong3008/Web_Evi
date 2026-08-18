import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from database.db_manager import db_session, init_db
from database.models import Student
from services.google_sheets import GoogleSheetsService

def inspect():
    init_db()
    session = db_session()

    print("Checking first 10 students in SQLite DB...")
    st_list = session.query(Student).limit(15).all()
    for s in st_list:
        print(f"  - [{s.code}] {s.full_name} ({s.english_name}): class='{s.class_name}', phone='{s.phone}', parent='{s.parent_name}', rem_sess={s.remaining_sessions}")

    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if svc.connect():
        sp1 = svc.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
        ws = sp1.worksheet('DATA HS FULL PHÍ')
        rows = ws.get_all_values()
        print(f"\nSheet 1 'DATA HS FULL PHÍ' row count: {len(rows)}")
        print("Header row 0:", rows[0][:15])
        print("Header row 1:", rows[1][:15])
        print("First 5 student rows:")
        for r in rows[2:7]:
            print(f"  Row: {r[:10]}")

if __name__ == '__main__':
    inspect()
