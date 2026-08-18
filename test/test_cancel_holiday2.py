import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import HolidayHistoryLog, LessonSyllabus
from services.db_service import get_class_lesson_log_db, get_schedule_matrix_db

session = db_session()

# Set Holiday ID 2 to 'Cancelled'
h2 = session.query(HolidayHistoryLog).filter(HolidayHistoryLog.id == 2).first()
if h2:
    h2.status = 'Cancelled'

session.commit()
print("Set Holiday ID 2 to Cancelled!")

print("\n--- Checking get_class_lesson_log_db for Sun 4.3 & Sun 3.5 ---")
for cname, expected_num in [('Sun 4.3', 53), ('Sun 3.5', 52)]:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    today_lessons = [l for l in lessons if l.get('status_code') == 'today']
    print(f"\nClass '{cname}' (Expected Today Lesson {expected_num}):")
    for tl in today_lessons:
        print(f"  -> Today Lesson {tl.get('buoi')}: Title='{tl.get('lesson_title')}' | Date='{tl.get('date')}' | Status='{tl.get('status_code')}'")

print("\n--- Checking Schedule Matrix API Output ---")
matrix_res = get_schedule_matrix_db()
for row in matrix_res.get('matrix', []):
    if row.get('day_code') == 'Fri':
        for shift in ['mt5', 'mt6']:
            item = row.get(shift)
            if item and item.get('class_name') in ['Sun 4.3', 'Sun 3.5']:
                print(f"FRI Shift {shift.upper()}: Class='{item.get('class_name')}' | current_buoi={item.get('current_buoi')} | current_title='{item.get('current_title')}'")

session.close()
