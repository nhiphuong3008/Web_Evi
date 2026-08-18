import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus

def inspect_mapping():
    session = db_session()
    
    # 1. Unique materials in class_schedules
    schedules = session.query(ClassSchedule).all()
    print(f"Total schedules in DB: {len(schedules)}")
    
    materials_set = set(s.materials for s in schedules if s.materials)
    print(f"\nUnique materials in ClassSchedule ({len(materials_set)}):")
    for m in sorted(materials_set):
        print(f"  - '{m}'")

    # 2. Unique course_names in LessonSyllabus
    syllabuses = session.query(LessonSyllabus).all()
    courses_set = set(s.course_name for s in syllabuses if s.course_name)
    print(f"\nUnique course_names in LessonSyllabus ({len(courses_set)}):")
    for c in sorted(courses_set):
        count = session.query(LessonSyllabus).filter(LessonSyllabus.course_name == c).count()
        print(f"  - '{c}' ({count} lessons)")

    # 3. Check sample classes mapping
    print("\nSample Class Materials Mapping Check:")
    sample_classes = ['Sun 2.1', 'Sun 2.2', 'KB2 U5', 'Moon 3', 'Galax 1', 'Sun 1']
    for cname in sample_classes:
        scheds = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{cname}%")).all()
        if scheds:
            mat = scheds[0].materials
            print(f"  Class '{cname}' -> materials: '{mat}'")
        else:
            print(f"  Class '{cname}' -> No schedule found")

    session.close()

if __name__ == '__main__':
    inspect_mapping()
