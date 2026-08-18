import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule, ClassMaster, Student

def main():
    session = db_session()
    schedules = session.query(ClassSchedule).all()
    print(f"Total Schedule records: {len(schedules)}\n")
    print(f"{'ID':<4} | {'Class Name':<15} | {'Shift':<6} | {'Room':<10} | {'Teacher':<12} | {'CM Staff':<12}")
    print("-" * 75)
    for s in schedules:
        print(f"{s.id:<4} | {s.class_name:<15} | {s.shift_code:<6} | {s.room or '':<10} | {s.teacher or '':<12} | {s.cm_staff or '':<12}")
    session.close()

if __name__ == "__main__":
    main()
