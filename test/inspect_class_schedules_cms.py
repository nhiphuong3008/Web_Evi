import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule

def inspect():
    session = db_session()
    all_s = session.query(ClassSchedule).all()
    print(f"Total ClassSchedule records: {len(all_s)}")
    
    cms = set()
    teachers = set()
    for s in all_s:
        if s.cm_staff: cms.add(s.cm_staff)
        if s.teacher: teachers.add(s.teacher)

    print(f"ClassSchedule distinct CMs: {sorted(list(cms))}")
    print(f"ClassSchedule distinct Teachers: {sorted(list(teachers))}")
    session.close()

if __name__ == '__main__':
    inspect()
