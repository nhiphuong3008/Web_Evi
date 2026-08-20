import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()

print("--- ClassSchedules for Moon 5.1 ---")
cursor.execute("SELECT * FROM class_schedules WHERE class_name LIKE '%Moon 5.1%'")
for r in cursor.fetchall():
    print(r)

print("\n--- ClassScheduleAdjustment for Moon 5.1 ---")
cursor.execute("SELECT * FROM class_schedule_adjustments WHERE class_name LIKE '%Moon 5.1%'")
for r in cursor.fetchall():
    print(r)

print("\n--- LessonSyllabus for Moon 5.1 (Lessons 40-52) ---")
cursor.execute("SELECT id, class_name, course_name, lesson_num, lesson_title, unit_name, official_date, file_source FROM lesson_syllabuses WHERE class_name LIKE '%Moon 5.1%' AND lesson_num BETWEEN 40 AND 52 ORDER BY lesson_num")
for r in cursor.fetchall():
    print(r)

conn.close()
