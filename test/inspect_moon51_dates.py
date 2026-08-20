import sqlite3

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()
cursor.execute("SELECT lesson_num, lesson_title, official_date FROM lesson_syllabuses WHERE class_name LIKE '%Moon 5.1%' ORDER BY lesson_num")
for r in cursor.fetchall():
    print(r)
conn.close()
