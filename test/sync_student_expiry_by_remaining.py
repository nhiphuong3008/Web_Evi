import sys
import os
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import calculate_fee_expiry_date

def sync_student_expiry_dates():
    conn = sqlite3.connect('database/evi_center.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, code, full_name, schedule, remaining_sessions, expiry_date FROM students")
    students = cursor.fetchall()

    updated_count = 0
    for st in students:
        rem = st['remaining_sessions'] or 0
        sch = st['schedule'] or ''
        new_exp = calculate_fee_expiry_date(rem, sch)

        month_val = ''
        year_val = ''
        if new_exp != 'Đã hết phí':
            try:
                parts = new_exp.split('/')
                if len(parts) == 3:
                    month_val = str(int(parts[1]))
                    year_val = parts[2]
            except Exception:
                pass

        if st['expiry_date'] != new_exp:
            cursor.execute("""
                UPDATE students 
                SET expiry_date = ?, expiry_month = ?, expiry_year = ?
                WHERE id = ?
            """, (new_exp, month_val, year_val, st['id']))
            updated_count += 1

    conn.commit()
    print(f"✅ Synchronized expiry dates for {updated_count} / {len(students)} students in DB!")

    # Verify EVI305
    cursor.execute("SELECT code, full_name, remaining_sessions, expiry_date FROM students WHERE code = 'EVI305'")
    print("EVI305 record after sync:", dict(cursor.fetchone()))

    conn.close()

if __name__ == '__main__':
    sync_student_expiry_dates()
