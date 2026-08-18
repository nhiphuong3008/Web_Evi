import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ParentInteractionLog

def inspect_naomi_logs():
    session = db_session()
    logs = session.query(ParentInteractionLog).filter(ParentInteractionLog.id >= 100, ParentInteractionLog.id <= 120).all()
    print("--- INTERACTION LOGS #100 TO #120 ---")
    for l in logs:
        st = l.student_name or ''
        dt = (l.note or l.interaction_detail or '')[:60]
        code = l.student_code or 'NONE'
        print(f"ID: #{l.id} | Code: {code} | Student: '{st}' | Note: '{dt}'")
    session.close()

if __name__ == '__main__':
    inspect_naomi_logs()
