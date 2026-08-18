import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ParentInteractionLog

def inspect_phone_logs():
    session = db_session()
    logs = session.query(ParentInteractionLog).all()
    print(f"Total ParentInteractionLog records in SQLite DB: {len(logs)}")
    
    phone_logs = []
    good_logs = []

    for log in logs:
        note = log.note or log.interaction_detail or ''
        # Criteria for bad records created by misinterpreting Phone/Class columns from old Daily Checking sheets
        if "Tình hình học tập:" in note and ("Lịch sử chăm sóc PH:" in note or "SĐT" in note or any(c.isdigit() for c in note)):
            phone_logs.append(log)
        else:
            good_logs.append(log)

    print(f"  • Real/Valid Parent Interaction Logs: {len(good_logs)}")
    print(f"  • Phone number / Column misalignment records (from old Daily Checking sheets): {len(phone_logs)}")
    
    print("\n--- SAMPLE PHONE NUMBER MISALIGNED RECORDS ---")
    for p in phone_logs[:10]:
        print(f"ID: #{p.id} | Student: '{p.student_name}' | Staff: '{p.staff_name}' | Note: '{p.note}'")

    session.close()

if __name__ == '__main__':
    inspect_phone_logs()
