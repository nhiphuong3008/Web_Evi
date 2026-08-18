import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

print("=== EVI363 (Nguyễn Tuệ Nhi) IN STUDENTS TABLE ===")
c.execute("""
    SELECT code, full_name, english_name, class_name, total_sessions, remaining_sessions, charged_absent_sessions, expiry_date 
    FROM students 
    WHERE code = 'EVI363' OR full_name LIKE '%Tuệ Nhi%'
""")
for r in c.fetchall():
    print(r)

print("\n=== EVI363 IN STUDENT RENEWALS TABLE ===")
c.execute("""
    SELECT id, student_code, student_name, class_name, month, year, status, due_date, expected_expiry_date 
    FROM student_renewals 
    WHERE student_code = 'EVI363' OR student_name LIKE '%Tuệ Nhi%'
""")
for r in c.fetchall():
    print(r)

conn.close()
