import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

print("=== 1. STUDENTS TABLE INFO ===")
c.execute("SELECT id, code, full_name, english_name, class_name, total_sessions, remaining_sessions, attended_sessions, fee_status FROM students WHERE code IN ('EVI068', 'EVI056') OR full_name LIKE '%Ngọc Minh%' OR full_name LIKE '%Ngọc Huyền%'")
rows = c.fetchall()
for r in rows:
    print(r)

print("\n=== 2. STUDENT RENEWALS TABLE INFO ===")
c.execute("SELECT id, student_code, student_name, class_name, month, year, status, fee_package, due_date, expected_expiry_date FROM student_renewals WHERE student_code IN ('EVI068', 'EVI056') OR student_name LIKE '%Ngọc Minh%' OR student_name LIKE '%Ngọc Huyền%'")
r_rows = c.fetchall()
for r in r_rows:
    print(r)

print("\n=== 3. ATTENDANCE RECORDS FOR EVI068 & EVI056 ===")
c.execute("SELECT id, student_code, student_name, class_name, attendance_date, status FROM monthly_attendance_records WHERE student_code IN ('EVI068', 'EVI056') OR student_name LIKE '%Ngọc Minh%' OR student_name LIKE '%Ngọc Huyền%' LIMIT 30")
att_rows = c.fetchall()
for r in att_rows:
    print(r)

conn.close()
