import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session, init_db
from database.models import ClassSchedule

def check():
    init_db()
    session = db_session()
    cnt = session.query(ClassSchedule).count()
    print(f"Current ClassSchedule count in DB: {cnt}")
    s = session.query(ClassSchedule).first()
    if s:
        print("First schedule in DB:", s.to_dict())

if __name__ == '__main__':
    check()
