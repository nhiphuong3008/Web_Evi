import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()
cursor.execute("SELECT lesson_num, lesson_title, official_date FROM lesson_syllabuses WHERE class_name LIKE '%Moon 5.1%' AND lesson_num >= 44 AND lesson_num <= 52 ORDER BY lesson_num")
for r in cursor.fetchall():
    print(r)

print("\n--- Adjustment ---")
cursor.execute("SELECT * FROM class_schedule_adjustments WHERE class_name LIKE '%Moon 5.1%'")
for r in cursor.fetchall():
    print(r)

conn.close()
