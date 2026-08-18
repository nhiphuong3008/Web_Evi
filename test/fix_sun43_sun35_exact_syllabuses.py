import sys
import os
import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import LessonSyllabus, ClassSchedule
from services.db_service import get_next_study_date, get_prev_study_date, get_class_lesson_log_db, get_schedule_matrix_db

session = db_session()

# Tue=1, Fri=4
tue_fri_weekdays = [1, 4]

# Function to generate 68 dates backward and forward from an anchor date
def generate_dates_for_class(anchor_lesson_num, anchor_date):
    dates_map = {}
    dates_map[anchor_lesson_num] = anchor_date

    # Fill backward
    curr_d = anchor_date
    for l_num in range(anchor_lesson_num - 1, 0, -1):
        curr_d = get_prev_study_date(curr_d, tue_fri_weekdays)
        dates_map[l_num] = curr_d

    # Fill forward
    curr_d = anchor_date
    for l_num in range(anchor_lesson_num + 1, 69):
        curr_d = get_next_study_date(curr_d, tue_fri_weekdays)
        dates_map[l_num] = curr_d

    return dates_map

# 1. Sun 4.3 -> Lesson 53 = 2026-08-14
sun43_dates = generate_dates_for_class(53, datetime.date(2026, 8, 14))

# 2. Sun 3.5 -> Lesson 52 = 2026-08-14
sun35_dates = generate_dates_for_class(52, datetime.date(2026, 8, 14))

# Apply to LessonSyllabus table in SQLite
for cname, dates_map in [('Sun 4.3', sun43_dates), ('Sun 3.5', sun35_dates)]:
    print(f"\nApplying 68 dates to '{cname}'...")
    syllabuses = session.query(LessonSyllabus).filter(LessonSyllabus.class_name == cname).all()
    for s in syllabuses:
        if s.lesson_num in dates_map:
            s.official_date = dates_map[s.lesson_num].strftime('%Y-%m-%d')

session.commit()
print("✅ Successfully updated official_date for 100% of lessons in Sun 4.3 and Sun 3.5!")

print("\n--- Verifying get_class_lesson_log_db ---")
for cname, expected_num in [('Sun 4.3', 53), ('Sun 3.5', 52)]:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    today_lessons = [l for l in lessons if l.get('status_code') == 'today']
    print(f"\nClass '{cname}' (Expected Today Lesson {expected_num}):")
    for tl in today_lessons:
        print(f"  -> Today Lesson {tl.get('buoi')}: Title='{tl.get('lesson_title')}' | Date='{tl.get('date')}' | Status='{tl.get('status_code')}'")

print("\n--- Verifying Schedule Matrix API Output ---")
matrix_res = get_schedule_matrix_db()
for row in matrix_res.get('matrix', []):
    if row.get('day_code') == 'Fri':
        for shift in ['mt5', 'mt6']:
            item = row.get(shift)
            if item and item.get('class_name') in ['Sun 4.3', 'Sun 3.5']:
                print(f"FRI Shift {shift.upper()}: Class='{item.get('class_name')}' | current_buoi={item.get('current_buoi')} | current_title='{item.get('current_title')}'")

session.close()
