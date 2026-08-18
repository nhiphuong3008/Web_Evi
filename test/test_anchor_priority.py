import sys
import os
import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import LessonSyllabus, ClassSchedule
from services.db_service import get_next_study_date, get_prev_study_date, get_class_lesson_log_db, get_schedule_matrix_db, calculate_real_class_lesson_dates

session = db_session()

# Set explicit official_date for Sun 4.3 Lesson 53 -> 2026-08-14
row_sun43 = session.query(LessonSyllabus).filter(
    LessonSyllabus.class_name == 'Sun 4.3',
    LessonSyllabus.lesson_num == 53
).first()
if row_sun43:
    row_sun43.official_date = '2026-08-14'

# Set explicit official_date for Sun 3.5 Lesson 52 -> 2026-08-14
row_sun35 = session.query(LessonSyllabus).filter(
    LessonSyllabus.class_name == 'Sun 3.5',
    LessonSyllabus.lesson_num == 52
).first()
if row_sun35:
    row_sun35.official_date = '2026-08-14'

session.commit()

print("--- Testing get_class_lesson_log_db after anchor assignment ---")

for cname, target_buoi in [('Sun 4.3', 53), ('Sun 3.5', 52)]:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    today_lessons = [l for l in lessons if l.get('status_code') == 'today']
    print(f"\nClass '{cname}' (Expected Today Lesson {target_buoi}):")
    for tl in today_lessons:
        print(f"  -> Today Lesson {tl.get('buoi')}: Title='{tl.get('lesson_title')}' | Date='{tl.get('date')}' | Status='{tl.get('status_code')}'")

session.close()
