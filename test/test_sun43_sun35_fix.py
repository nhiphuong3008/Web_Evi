import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import LessonSyllabus
from services.db_service import get_class_lesson_log_db, get_schedule_matrix_db

session = db_session()

print("--- Testing official_date update for Sun 4.3 & Sun 3.5 ---")

# Sun 4.3 -> Lesson 53 on 2026-08-14
sun43_l53 = session.query(LessonSyllabus).filter(
    LessonSyllabus.class_name == 'Sun 4.3',
    LessonSyllabus.lesson_num == 53
).first()
if sun43_l53:
    print(f"Sun 4.3 Lesson 53 current date: '{sun43_l53.official_date}'")
    sun43_l53.official_date = '2026-08-14'

# Sun 3.5 -> Lesson 52 on 2026-08-14
sun35_l52 = session.query(LessonSyllabus).filter(
    LessonSyllabus.class_name == 'Sun 3.5',
    LessonSyllabus.lesson_num == 52
).first()
if sun35_l52:
    print(f"Sun 3.5 Lesson 52 current date: '{sun35_l52.official_date}'")
    sun35_l52.official_date = '2026-08-14'

session.commit()
print("Updated official dates in DB!")

print("\n--- Re-verifying get_class_lesson_log_db ---")
for cname, expected_num in [('Sun 4.3', 53), ('Sun 3.5', 52)]:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    today_lessons = [l for l in lessons if l.get('status_code') == 'today']
    print(f"\nClass {cname}: Today lessons count = {len(today_lessons)}")
    for tl in today_lessons:
        print(f"  -> Today Lesson {tl.get('buoi')}: Title='{tl.get('lesson_title')}' | Date='{tl.get('date')}' | Status='{tl.get('status_code')}'")

print("\n--- Re-verifying get_schedule_matrix_db ---")
matrix_res = get_schedule_matrix_db()
for row in matrix_res.get('matrix', []):
    if row.get('day_code') == 'Fri':
        for shift in ['mt5', 'mt6']:
            item = row.get(shift)
            if item and item.get('class_name') in ['Sun 4.3', 'Sun 3.5']:
                print(f"FRI Shift {shift.upper()}: Class='{item.get('class_name')}' | current_buoi={item.get('current_buoi')} | current_title='{item.get('current_title')}'")

session.close()
