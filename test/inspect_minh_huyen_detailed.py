import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

print("=== 1. STUDENTS TABLE ===")
c.execute("""
    SELECT code, full_name, english_name, class_name, grammar_class, 
           total_sessions, remaining_sessions, expiry_date, expiry_month, expiry_year
    FROM students 
    WHERE code IN ('EVI068', 'EVI056') OR full_name LIKE '%Ngọc Minh%' OR full_name LIKE '%Ngọc Huyền%'
""")
for r in c.fetchall():
    print(r)

print("\n=== 2. STUDENT RENEWALS TABLE ===")
c.execute("""
    SELECT id, student_code, student_name, class_name, month, year, status, due_date, expected_expiry_date
    FROM student_renewals 
    WHERE student_code IN ('EVI068', 'EVI056') OR student_name LIKE '%Ngọc Minh%' OR student_name LIKE '%Ngọc Huyền%'
""")
for r in c.fetchall():
    print(r)

print("\n=== 3. ATTENDANCE DATES FOR EVI068 & EVI056 ===")
c.execute("""
    SELECT student_code, student_name, class_name, attendance_date, status 
    FROM monthly_attendance_records 
    WHERE student_code IN ('EVI068', 'EVI056') OR student_name LIKE '%Ngọc Minh%' OR student_name LIKE '%Ngọc Huyền%'
""")
att = c.fetchall()
print(f"Total attendance records found: {len(att)}")
for a in att[:20]:
    print(a)

conn.close()
