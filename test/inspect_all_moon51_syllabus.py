import sqlite3

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()

cursor.execute("SELECT lesson_num, lesson_title, unit_name, official_date FROM lesson_syllabuses WHERE class_name LIKE '%Moon 5.1%' ORDER BY lesson_num")
rows = cursor.fetchall()
print(f"Total syllabus rows for Moon 5.1: {len(rows)}")
for r in rows:
    if r[0] >= 40:
        print(r)

conn.close()
