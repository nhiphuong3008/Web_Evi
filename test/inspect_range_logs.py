import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ParentInteractionLog

def inspect_range():
    session = db_session()
    logs = session.query(ParentInteractionLog).filter(ParentInteractionLog.id >= 195, ParentInteractionLog.id <= 215).all()
    print("--- INTERACTION LOGS #195 TO #215 ---")
    for l in logs:
        st = l.student_name or ''
        dt = (l.interaction_detail or l.note or '')[:50]
        code = l.student_code or 'NONE'
        print(f"ID: #{l.id} | Code: {code} | Student: '{st}' | Detail: '{dt}'")
    session.close()

if __name__ == '__main__':
    inspect_range()
