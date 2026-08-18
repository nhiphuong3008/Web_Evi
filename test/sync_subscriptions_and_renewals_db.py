import sys
import os
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

def sync_subscriptions_and_renewals():
    conn = sqlite3.connect('database/evi_center.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Fetch all students
    c.execute("SELECT code, full_name, class_name, cm_staff, expiry_date, expiry_month, expiry_year, remaining_sessions FROM students")
    students = c.fetchall()

    student_map = {st['code']: st for st in students if st['code']}
    student_name_map = {st['full_name']: st for st in students if st['full_name']}

    updated_subs = 0
    updated_ren = 0

    # 1. Update student_subscriptions
    c.execute("SELECT id, student_code, student_name, current_end_date, original_end_date FROM student_subscriptions")
    subs = c.fetchall()

    for s in subs:
        st_code = s['student_code']
        st_name = s['student_name']
        st = student_map.get(st_code) or student_name_map.get(st_name)

        if st and st['expiry_date']:
            exp = st['expiry_date']
            rem = st['remaining_sessions'] or 0
            
            c.execute("""
                UPDATE student_subscriptions 
                SET current_end_date = ?, original_end_date = ?, remaining_sessions = ?, class_name = ?, cm_staff = ?
                WHERE id = ?
            """, (exp, exp, rem, st['class_name'] or '', st['cm_staff'] or '', s['id']))
            updated_subs += 1

    # 2. Update student_renewals
    c.execute("SELECT id, student_code, student_name, expected_expiry_date, month, year FROM student_renewals")
    renewals = c.fetchall()

    for r in renewals:
        st_code = r['student_code']
        st_name = r['student_name']
        st = student_map.get(st_code) or student_name_map.get(st_name)

        if st and st['expiry_date']:
            exp = st['expiry_date']
            month_val = int(st['expiry_month']) if (st['expiry_month'] and st['expiry_month'].isdigit()) else r['month']
            year_val = int(st['expiry_year']) if (st['expiry_year'] and st['expiry_year'].isdigit()) else r['year']

            c.execute("""
                UPDATE student_renewals 
                SET expected_expiry_date = ?, month = ?, year = ?, class_name = ?, cm_staff = ?
                WHERE id = ?
            """, (exp, month_val, year_val, st['class_name'] or '', st['cm_staff'] or '', r['id']))
            updated_ren += 1

    conn.commit()
    print(f"✅ Synchronized {updated_subs} StudentSubscription records and {updated_ren} StudentRenewal records with Student Master Data!")

    # Check EVI266
    c.execute("SELECT student_code, student_name, class_name, current_end_date FROM student_subscriptions WHERE student_code = 'EVI266'")
    print("EVI266 in student_subscriptions after sync:", dict(c.fetchone()))

    conn.close()

if __name__ == '__main__':
    sync_subscriptions_and_renewals()
