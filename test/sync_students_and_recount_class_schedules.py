import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import Student, ClassSchedule

def sync_and_recount():
    session = db_session()
    
    # 1. Update EVI411 (Ngo Bao Vy) to Galax 1.4
    evi411 = session.query(Student).filter(Student.code == 'EVI411').first()
    if evi411:
        evi411.class_name = 'Galax 1.4'
        evi411.schedule = 'TF5'
        evi411.status = 'Đang học'
        print("[SUCCESS] Fixed EVI411 (Ngo Bao Vy - Lily) => Assigned to 'Galax 1.4'")

    session.commit()

    # 2. Recount exact student count per class from Student table
    all_schedules = session.query(ClassSchedule).all()
    for sc in all_schedules:
        cname = sc.class_name.strip()
        count = session.query(Student).filter(
            Student.class_name.ilike(f"%{cname}%"),
            Student.status == 'Đang học'
        ).count()
        sc.students_count = count
        clean_cname = cname.encode('ascii', 'ignore').decode('ascii')
        print(f"  Class '{clean_cname:12s}': Updated students_count = {count}")

    session.commit()
    print("\n==========================================")
    print("SUCCESSFULLY SYNCED AND RECOUNTED ALL CLASS STUDENT COUNTS!")
    session.close()

if __name__ == '__main__':
    sync_and_recount()
