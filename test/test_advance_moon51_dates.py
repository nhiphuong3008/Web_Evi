import sqlite3
import datetime
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_next_study_date, get_prev_study_date, get_class_lesson_log_db, get_schedule_matrix_db

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()

sorted_weekdays = [2, 5]

# Shift dates backwards by 1 slot starting from lesson 46:
# Lesson 46 -> 2026-08-15
# Lesson 47 -> 2026-08-19
# Lesson 48 -> 2026-08-22
# Lesson 49 -> 2026-08-26
# Lesson 50 -> 2026-08-29
# Lesson 51 -> 2026-09-02
# Lesson 52 -> 2026-09-05

# And lesson 45 -> 2026-08-12, lesson 44 -> 2026-08-08, etc.

cursor.execute("UPDATE lesson_syllabuses SET official_date = '2026-08-12' WHERE class_name = 'Moon 5.1' AND lesson_num = 45")
cursor.execute("UPDATE lesson_syllabuses SET official_date = '2026-08-15' WHERE class_name = 'Moon 5.1' AND lesson_num = 46")

curr_d = datetime.date(2026, 8, 19)
cursor.execute("UPDATE lesson_syllabuses SET official_date = ? WHERE class_name = 'Moon 5.1' AND lesson_num = 47", (curr_d.strftime('%Y-%m-%d'),))

for l_num in range(48, 71):
    curr_d = get_next_study_date(curr_d, sorted_weekdays)
    cursor.execute("UPDATE lesson_syllabuses SET official_date = ? WHERE class_name = 'Moon 5.1' AND lesson_num = ?", (curr_d.strftime('%Y-%m-%d'), l_num))

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
