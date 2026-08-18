import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import LessonSyllabus, ClassSchedule
from services.db_service import calculate_real_class_lesson_dates, get_class_lesson_log_db, get_schedule_matrix_db

session = db_session()

# For Sun 3.5, set Lesson 52 = 2026-08-14, Lesson 51 = 2026-08-11, Lesson 50 = 2026-08-07, Lesson 49 = 2026-08-04, Lesson 48 = 2026-07-31
sun35_anchors = {
    48: '2026-07-31',
    49: '2026-08-04',
    50: '2026-08-07',
    51: '2026-08-11',
    52: '2026-08-14'
}

for l_num, dt in sun35_anchors.items():
    row = session.query(LessonSyllabus).filter(
        LessonSyllabus.class_name == 'Sun 3.5',
        LessonSyllabus.lesson_num == l_num
    ).first()
    if row:
        row.official_date = dt

session.commit()

# Also ensure Sun 4.3 has Lesson 53 = 2026-08-14, Lesson 52 = 2026-08-11, Lesson 51 = 2026-08-07, Lesson 50 = 2026-08-04, Lesson 49 = 2026-07-31, Lesson 48 = 2026-07-28
sun43_anchors = {
    48: '2026-07-28',
    49: '2026-07-31',
    50: '2026-08-04',
    51: '2026-08-07',
    52: '2026-08-11',
    53: '2026-08-14'
}

for l_num, dt in sun43_anchors.items():
    row = session.query(LessonSyllabus).filter(
        LessonSyllabus.class_name == 'Sun 4.3',
        LessonSyllabus.lesson_num == l_num
    ).first()
    if row:
        row.official_date = dt

session.commit()

print("--- Testing get_class_lesson_log_db for Sun 4.3 & Sun 3.5 ---")
for cname, expected_num in [('Sun 4.3', 53), ('Sun 3.5', 52)]:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    today_lessons = [l for l in lessons if l.get('status_code') == 'today']
    print(f"\nClass '{cname}' (Expected Today Lesson {expected_num}):")
    for tl in today_lessons:
        print(f"  -> Today Lesson {tl.get('buoi')}: Title='{tl.get('lesson_title')}' | Date='{tl.get('date')}' | Status='{tl.get('status_code')}'")

print("\n--- Testing get_schedule_matrix_db API Output ---")
matrix_res = get_schedule_matrix_db()
for row in matrix_res.get('matrix', []):
    if row.get('day_code') == 'Fri':
        for shift in ['mt5', 'mt6']:
            item = row.get(shift)
            if item and item.get('class_name') in ['Sun 4.3', 'Sun 3.5']:
                print(f"FRI Shift {shift.upper()}: Class='{item.get('class_name')}' | current_buoi={item.get('current_buoi')} | current_title='{item.get('current_title')}'")

session.close()
