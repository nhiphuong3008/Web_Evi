import sqlite3
import datetime
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_next_study_date, get_prev_study_date, get_class_lesson_log_db, get_schedule_matrix_db

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()

sorted_weekdays = [2, 5] # Wed, Sat

# We anchor Lesson 47 = 2026-08-19 (Wed)
# Backward from 47 to 1
dates = {}
dates[47] = datetime.date(2026, 8, 19)

for l_num in range(46, 0, -1):
    dates[l_num] = get_prev_study_date(dates[l_num + 1], sorted_weekdays)

for l_num in range(48, 71):
    dates[l_num] = get_next_study_date(dates[l_num - 1], sorted_weekdays)

for l_num, dt in dates.items():
    cursor.execute("UPDATE lesson_syllabuses SET official_date = ? WHERE class_name = 'Moon 5.1' AND lesson_num = ?", (dt.strftime('%Y-%m-%d'), l_num))

conn.commit()
conn.close()

print("\n--- Testing get_class_lesson_log_db for Moon 5.1 ---")
log_res = get_class_lesson_log_db('Moon 5.1')
for l in log_res['lessons']:
    if l['buoi'] in range(44, 52):
        print(f"Buoi {l['buoi']}: Date={l['date']} | Status={l['status_label']} ({l['status_code']})")

print("\n--- Testing get_schedule_matrix_db for Moon 5.1 ---")
matrix_res = get_schedule_matrix_db()
for row in matrix_res['matrix']:
    for s in [row['mt5'], row['mt6']]:
        if s and 'Moon 5.1' in s.get('class_name', ''):
            print(f"Day: {row['day_full']} | Shift: {s.get('shift_code')} | Class: {s.get('class_name')} | current_buoi={s.get('current_buoi')} | current_title={s.get('current_title')}")
