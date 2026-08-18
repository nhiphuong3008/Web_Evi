import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule

def inspect_sched():
    session = db_session()
    print("==================================================")
    print("INSPECT CLASS SCHEDULE IN SQLITE DB")
    print("==================================================")

    rows = session.query(ClassSchedule).all()
    print(f"Total ClassSchedule rows in SQLite DB: {len(rows)}")

    for r in rows:
        print(f"  ID: {r.id:2d} | Day: {r.day:15s} | Class: {r.class_name:15s} | Room: {r.room:10s} | Shift: {r.shift_code:6s} | Teacher: {r.teacher:10s} | CM: {r.cm_staff:10s}")

    session.close()

if __name__ == '__main__':
    inspect_sched()
