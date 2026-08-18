import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ParentInteractionLog

def verify():
    session = db_session()
    logs = session.query(ParentInteractionLog).filter(ParentInteractionLog.student_code == 'EVI377').all()
    print(f"--- VERIFYING EVI377 RECORDS (TOTAL: {len(logs)}) ---")
    for l in logs:
        print(f"ID: #{l.id} | Code: {l.student_code} | Student: {l.student_name} | Staff: {l.staff_name}")
        print(f"   Note: {l.note[:120]}...\n")
    session.close()

if __name__ == '__main__':
    verify()
