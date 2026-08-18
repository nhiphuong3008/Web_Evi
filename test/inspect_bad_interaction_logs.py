import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ParentInteractionLog

def inspect_logs():
    session = db_session()
    logs = session.query(ParentInteractionLog).all()
    print(f"Total ParentInteractionLog records in SQLite DB: {len(logs)}")
    
    bad_logs = []
    good_logs = []

    for log in logs:
        name = log.student_name or ''
        detail = log.interaction_detail or ''
        # Criteria for bad records imported by mistake from Syllabus / Materials sheet:
        if any(keyword in name.lower() or keyword in detail.lower() for keyword in [
            'handbook', 'activity book', 'syllabus', 'wordwall', 'chương trình hè', 'bcht', 'e-learning', 'elearning', 'link tl'
        ]) and not log.student_code:
            bad_logs.append(log)
        else:
            good_logs.append(log)

    print(f"  • Good interaction log records: {len(good_logs)}")
    print(f"  • Bad/Junk records (Syllabus/Materials): {len(bad_logs)}")
    
    print("\n--- SAMPLE BAD RECORDS ---")
    for b in bad_logs:
        dt = (b.interaction_detail or b.note or '')[:60]
        print(f"ID: #{b.id} | Student: '{b.student_name}' | Staff: '{b.staff_name}' | Detail: '{dt}...'")

    session.close()

if __name__ == '__main__':
    inspect_logs()
