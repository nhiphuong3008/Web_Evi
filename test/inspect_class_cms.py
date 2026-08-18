import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassMaster, ClassSchedule, Student, User

def main():
    session = db_session()
    
    users = session.query(User).filter(User.role == 'cm').all()
    user_cm_names = sorted([u.cm_staff_name for u in users if u.cm_staff_name])
    print("Registered CM Users in DB:")
    print(user_cm_names)
    print(f"Total CM Users: {len(user_cm_names)}\n")

    print("ClassMaster records:")
    cm_masters = session.query(ClassMaster).all()
    for c in cm_masters:
        print(f"Class: {c.class_name} | CM: '{c.cm_staff}' | GV: '{c.teacher}' | Status: {c.status}")

    print("\nClassSchedule distinct CMs:")
    schedules = session.query(ClassSchedule).all()
    sc_cms = sorted(list(set(s.cm_staff for s in schedules if s.cm_staff)))
    print(sc_cms)

    print("\nStudents distinct CMs:")
    students = session.query(Student).all()
    st_cms = sorted(list(set(s.cm_staff for s in students if s.cm_staff)))
    print(st_cms)

    session.close()

if __name__ == "__main__":
    main()
