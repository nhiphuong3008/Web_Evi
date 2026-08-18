import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import LessonSyllabus, ClassSchedule
from services.db_service import calculate_real_class_lesson_dates

session = db_session()

for cname, target_num in [('Sun 4.3', 53), ('Sun 3.5', 52)]:
    schedules = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{cname}%")).all()
    syllabuses = session.query(LessonSyllabus).filter(LessonSyllabus.class_name == cname).order_by(LessonSyllabus.lesson_num).all()

    # Clear all official_date for lessons 40..68 first, then set ONLY target_num to '2026-08-14'
    for s in syllabuses:
        if s.lesson_num >= 40:
            s.official_date = ''
        if s.lesson_num == target_num:
            s.official_date = '2026-08-14'

    session.commit()

    lesson_dates, delayed = calculate_real_class_lesson_dates(schedules, cname, syllabuses, session)

    print(f"\n==========================================")
    print(f"CLASS '{cname}': Target Lesson {target_num} set to 2026-08-14")
    print(f"==========================================")

    for idx, d in enumerate(lesson_dates):
        l_num = idx + 1
        if 45 <= l_num <= 56:
            mark = " <-- TODAY" if str(d) == '2026-08-14' else ""
            print(f"  Lesson {l_num:2d}: date={d}{mark}")

session.close()
