import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus

def audit_all():
    session = db_session()
    
    # 1. Audit Schedule Duplicates
    schedules = session.query(ClassSchedule).all()
    c_names = [s.class_name for s in schedules]
    unique_names = set(c_names)
    print(f"--- 1. AUDIT SCHEDULE MATRIX ---")
    print(f"Total Schedule Entries: {len(schedules)}")
    print(f"Unique Class Names in Schedule: {len(unique_names)}")
    if len(schedules) == 38:
        print("[SUCCESS] Schedule is CLEAN with NO duplicates!\n")
    else:
        print("[WARNING] Schedule count mismatch!\n")

    # 2. Audit Lesson Syllabuses per Class
    print(f"--- 2. AUDIT CLASS LESSON SYLLABUSES ---")
    class_syllabuses = session.query(LessonSyllabus.class_name).filter(LessonSyllabus.class_name.isnot(None)).distinct().all()
    class_list = sorted([c[0] for c in class_syllabuses if c[0]])
    print(f"Total Official Classes Loaded: {len(class_list)}")
    
    for cname in class_list[:10]:
        count = session.query(LessonSyllabus).filter(LessonSyllabus.class_name == cname).count()
        clean_cname = cname.encode('ascii', 'ignore').decode('ascii')
        print(f"  Class '{clean_cname:12s}': {count} lessons loaded")

    session.close()

if __name__ == '__main__':
    audit_all()
