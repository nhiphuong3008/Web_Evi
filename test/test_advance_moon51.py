import sqlite3
import datetime
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_next_study_date, get_prev_study_date, get_class_lesson_log_db, get_schedule_matrix_db

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()

# Get study weekdays for Moon 5.1 (Wed=2, Sat=5)
sorted_weekdays = [2, 5]

# Current dates for Moon 5.1:
# Lesson 45: 2026-08-15
# Lesson 46: 2026-08-19 -> we shift Lesson 47 to 2026-08-19, Lesson 48 to 2026-08-22, etc.

cursor.execute("SELECT lesson_num, official_date FROM lesson_syllabuses WHERE class_name LIKE '%Moon 5.1%' AND lesson_num >= 45 ORDER BY lesson_num")
rows = cursor.fetchall()
print("Current syllabus dates:", rows[:10])

# Let's compute new dates starting from Lesson 47 = 2026-08-19
new_dates = {}
curr_d = datetime.date(2026, 8, 19)
new_dates[47] = curr_d.strftime('%Y-%m-%d')

for l_num in range(48, 71):
    curr_d = get_next_study_date(curr_d, sorted_weekdays)
    new_dates[l_num] = curr_d.strftime('%Y-%m-%d')

print("\nNew planned dates:")
for k in range(47, 55):
    print(f"Lesson {k}: {new_dates[k]}")

# Also update Lesson 46 to be 2026-08-15
cursor.execute("UPDATE lesson_syllabuses SET official_date = '2026-08-15' WHERE class_name = 'Moon 5.1' AND lesson_num = 46")

for k, d in new_dates.items():
    cursor.execute("UPDATE lesson_syllabuses SET official_date = ? WHERE class_name = 'Moon 5.1' AND lesson_num = ?", (d, k))

conn.commit()
conn.close()

print("\n--- Testing get_class_lesson_log_db for Moon 5.1 ---")
log_res = get_class_lesson_log_db('Moon 5.1')
for l in log_res['lessons']:
    if l['buoi'] in [45, 46, 47, 48, 49, 50]:
        print(f"Buoi {l['buoi']}: Date={l['date']} | Status={l['status_label']} ({l['status_code']})")

print("\n--- Testing get_schedule_matrix_db for Moon 5.1 ---")
matrix_res = get_schedule_matrix_db()
for row in matrix_res['matrix']:
    for s in [row['mt5'], row['mt6']]:
        if s and 'Moon 5.1' in s.get('class_name', ''):
            print(f"Day: {row['day_full']} | Shift: {s.get('shift_code')} | Class: {s.get('class_name')} | current_buoi={s.get('current_buoi')} | current_title={s.get('current_title')}")
