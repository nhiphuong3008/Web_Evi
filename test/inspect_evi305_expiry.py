import sys
import os
import json
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

def main():
    conn = sqlite3.connect('database/evi_center.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    print("=== 1. STUDENTS TABLE FOR EVI305 ===")
    c.execute("SELECT code, full_name, class_name, total_sessions, remaining_sessions, expiry_date, expiry_month, expiry_year, status FROM students WHERE code = 'EVI305'")
    st = c.fetchone()
    print(dict(st) if st else "No student found")

    print("\n=== 2. SUBSCRIPTIONS TABLE FOR EVI305 ===")
    c.execute("SELECT * FROM student_subscriptions WHERE student_code = 'EVI305'")
    subs = c.fetchall()
    for s in subs:
        print(dict(s))

    print("\n=== 3. ATTENDANCE COUNT FOR EVI305 IN attendance_records ===")
    c.execute("SELECT COUNT(*) as att_count FROM attendance_records WHERE student_code = 'EVI305' OR student_name LIKE '%Lương Minh Hưng%'")
    print("Attendance records count:", c.fetchone()['att_count'])

    c.execute("SELECT date, status, class_name FROM attendance_records WHERE student_code = 'EVI305' OR student_name LIKE '%Lương Minh Hưng%' ORDER BY date DESC LIMIT 10")
    for r in c.fetchall():
        print(dict(r))

    print("\n=== 4. CLASS INFO FOR Moon 5.2 ===")
    c.execute("SELECT * FROM classes WHERE name LIKE '%Moon 5.2%'")
    cls = c.fetchone()
    if cls:
        cls_d = dict(cls)
        print("Class:", cls_d.get('name'), "Start date:", cls_d.get('start_date'), "Schedule days:", cls_d.get('schedule_days'))

    print("\n=== 5. CHECKING OTHER STUDENTS IN Moon 5.2 ===")
    c.execute("SELECT code, full_name, total_sessions, remaining_sessions, expiry_date FROM students WHERE class_name LIKE '%Moon 5.2%' LIMIT 5")
    for row in c.fetchall():
        print(dict(row))

if __name__ == '__main__':
    main()
