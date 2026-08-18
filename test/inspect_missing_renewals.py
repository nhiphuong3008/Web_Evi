import sys
import os
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

def inspect_missing_renewals():
    conn = sqlite3.connect('database/evi_center.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Total active students in students table
    c.execute("SELECT COUNT(*) FROM students WHERE status = 'Đang học'")
    total_st = c.fetchone()[0]
    print(f"Total active students in `students` table: {total_st}")

    # 2. Total records in `student_subscriptions` table
    c.execute("SELECT COUNT(*) FROM student_subscriptions")
    total_subs = c.fetchone()[0]
    print(f"Total records in `student_subscriptions` table: {total_subs}")

    # 3. Check EVI124 in students vs student_subscriptions
    c.execute("SELECT code, full_name, class_name, expiry_date, expiry_month, expiry_year, remaining_sessions FROM students WHERE code = 'EVI124'")
    st_124 = c.fetchone()
    print("\nEVI124 in `students` table:", dict(st_124) if st_124 else 'NOT FOUND')

    c.execute("SELECT * FROM student_subscriptions WHERE student_code = 'EVI124'")
    sub_124 = c.fetchone()
    print("EVI124 in `student_subscriptions` table:", dict(sub_124) if sub_124 else '❌ NOT FOUND IN student_subscriptions!')

    # 4. Check active students missing from student_subscriptions
    c.execute("SELECT code, full_name, class_name, expiry_date, expiry_month, expiry_year FROM students WHERE status = 'Đang học' AND code NOT IN (SELECT student_code FROM student_subscriptions WHERE student_code IS NOT NULL AND student_code != '')")
    missing_st = c.fetchall()
    print(f"\n❌ Active students in `students` table MISSING from `student_subscriptions` table: {len(missing_st)}")
    for m in missing_st[:15]:
        print("  - Missing:", dict(m))

    # 5. Check students for Month 7 Year 2027 in students table vs student_subscriptions table
    c.execute("SELECT code, full_name, class_name, expiry_date, expiry_month, expiry_year FROM students WHERE status = 'Đang học' AND expiry_month = '7' AND expiry_year = '2027'")
    m7_2027_st = c.fetchall()
    print(f"\n📅 Active students expiring in Month 7/2027 in `students` table: {len(m7_2027_st)}")
    for s in m7_2027_st:
        print("  - Expiring in Month 7/2027:", dict(s))

    conn.close()

if __name__ == '__main__':
    inspect_missing_renewals()
