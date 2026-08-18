import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("SELECT id, student_code, student_name, class_name, month, year, status FROM student_renewals WHERE cm_staff IS NULL OR cm_staff = ''")
rows = c.fetchall()
print("15 remaining rows with empty cm_staff:")
for r in rows:
    print(r)

conn.close()
