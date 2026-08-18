"""
Script to sync all existing Student records' teacher, cm_staff, schedule, room from ClassSchedule.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

from services.db_service import db_session, resolve_class_info_from_schedule_db
from database.models import Student

def main():
    session = db_session()
    students = session.query(Student).all()
    updated_count = 0

    for s in students:
        if s.class_name and s.class_name.strip():
            res_info = resolve_class_info_from_schedule_db(s.class_name, session)
            changed = False
            if not s.teacher and res_info['teacher']:
                s.teacher = res_info['teacher']
                changed = True
            if not s.cm_staff and res_info['cm_staff']:
                s.cm_staff = res_info['cm_staff']
                changed = True
            if not s.schedule and res_info['schedule']:
                s.schedule = res_info['schedule']
                changed = True
            if not s.room and res_info['room']:
                s.room = res_info['room']
                changed = True

            if changed:
                updated_count += 1

    session.commit()
    session.close()
    print(f"✅ Successfully updated {updated_count} students with class schedule info!")

if __name__ == '__main__':
    main()
