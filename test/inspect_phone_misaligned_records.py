import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ParentInteractionLog

def inspect():
    session = db_session()
    logs = session.query(ParentInteractionLog).all()
    print(f"Total records in ParentInteractionLog: {len(logs)}")

    misaligned_ids = []

    for l in logs:
        note = l.note or l.interaction_detail or ''
        # Check if note is just "Tình hình học tập: <PHONE_NUMBER> | Lịch sử chăm sóc PH: <CLASS_NAME>"
        if "Tình hình học tập:" in note and "Lịch sử chăm sóc PH:" in note:
            parts = note.split("| Lịch sử chăm sóc PH:")
            acad = parts[0].replace("Tình hình học tập:", "").strip()
            care = parts[1].strip() if len(parts) > 1 else ''
            
            # If academic note is just digits/phone numbers or 'SĐT' or 'SDT' or blank, and care is just class name like 'Sun 4.3' or 'Lớp'
            acad_clean = re.sub(r'[\d\s/\.\-]', '', acad)
            if acad_clean in ('', 'sdt', 'sđt') or re.match(r'^[\d\s/\.\-]+$', acad):
                misaligned_ids.append(l.id)

    print(f"  • Found {len(misaligned_ids)} misaligned phone/class records imported from old (Naomi) Daily Checking tab!")
    print(f"  • Range of IDs: min #{min(misaligned_ids)} to max #{max(misaligned_ids)}")
    session.close()

if __name__ == '__main__':
    inspect()
