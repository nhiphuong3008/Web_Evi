import sqlite3

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()
cursor.execute("SELECT class_name, course_name, lesson_num, lesson_title, unit_name, official_date, vocabulary FROM lesson_syllabuses WHERE class_name LIKE '%Moon%' AND lesson_num IN (45, 46, 47)")
rows = cursor.fetchall()
for r in rows:
    print(r)
conn.close()
