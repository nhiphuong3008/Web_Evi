import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import LessonSyllabus

def check_sun2():
    session = db_session()
    lessons = session.query(LessonSyllabus).filter(LessonSyllabus.course_name == 'Sun 2').order_by(LessonSyllabus.lesson_num.asc()).all()
    print(f"Total Sun 2 lessons in DB: {len(lessons)}")
    
    for l in lessons[:10]:
        print(f"\n--- Lesson {l.lesson_num}: {l.lesson_title} ---")
        print(f"  Unit: '{l.unit_name}'")
        print(f"  Pages: '{l.pages}'")
        print(f"  Vocab: '{l.vocabulary}'")
        print(f"  Grammar: '{l.grammar}'")
        print(f"  Target: '{l.lesson_target}'")
        print(f"  HW Teacher: '{l.homework_teacher}'")
        print(f"  HW CM: '{l.homework_cm}'")

    session.close()

if __name__ == '__main__':
    check_sun2()
