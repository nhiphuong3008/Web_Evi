import sqlite3

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()
cursor.execute("SELECT class_name, course_name, lesson_num, lesson_title, unit_name FROM lesson_syllabuses WHERE unit_name LIKE '%SMART PHONICS 3%' OR lesson_title LIKE '%46%' LIMIT 10")
rows = cursor.fetchall()
print("Syllabus rows found:", rows)

cursor.execute("SELECT DISTINCT class_name, materials FROM class_schedules WHERE materials LIKE '%SMART PHONICS%' OR class_name LIKE '%Sun%' OR class_name LIKE '%Galax%'")
print("Classes:", cursor.fetchall())
conn.close()
