import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import LessonSyllabus, ClassSchedule
from services.db_service import calculate_real_class_lesson_dates

session = db_session()

for cname in ['Sun 4.3', 'Sun 3.5']:
    schedules = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{cname}%")).all()
    syllabuses = session.query(LessonSyllabus).filter(LessonSyllabus.class_name == cname).order_by(LessonSyllabus.lesson_num).all()

    lesson_dates, delayed = calculate_real_class_lesson_dates(schedules, cname, syllabuses, session)

    print(f"\n--- {cname} Calculated Lesson Dates ---")
    print(f"Official dates set in DB:")
    for s in syllabuses:
        if s.official_date:
            print(f"  Lesson {s.lesson_num}: official_date='{s.official_date}'")

    print("\nCalculated dates around today (2026-08-14):")
    for idx, d in enumerate(lesson_dates):
        l_num = idx + 1
        if 45 <= l_num <= 56:
            print(f"  Lesson {l_num:2d}: date={d}")

session.close()
