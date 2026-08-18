import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session, init_db
from database.models import ClassSchedule, HomeworkRecord, UnitGrade, Student

def test_class_detail(class_name='Sun 2.4'):
    init_db()
    session = db_session()

    # Query schedule for class
    sched = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{class_name}%")).all()
    print(f"Schedules for {class_name}: {len(sched)} records")
    for s in sched:
        print(f"  - Day: {s.day}, Shift: {s.shift_name}, Room: {s.room}, Teacher: {s.teacher}, CM: {s.cm_staff}, Mat: {s.materials}")

    # Query homework for class
    hw = session.query(HomeworkRecord).filter(HomeworkRecord.class_name.ilike(f"%{class_name}%")).limit(10).all()
    print(f"\nHomework records for {class_name}: {len(hw)}")

    # Query grades for class
    gr = session.query(UnitGrade).filter(UnitGrade.class_name.ilike(f"%{class_name}%")).limit(10).all()
    print(f"Unit grades for {class_name}: {len(gr)}")

if __name__ == '__main__':
    test_class_detail('Sun 2.4')
