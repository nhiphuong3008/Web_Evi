import sys
import os
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import calculate_fee_expiry_date

def audit_active_students():
    conn = sqlite3.connect('database/evi_center.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT id, code, full_name, class_name, schedule, total_sessions, remaining_sessions, expiry_date, expiry_month, expiry_year, status 
        FROM students 
        WHERE status = 'Đang học'
        ORDER BY id ASC
    """)
    students = c.fetchall()

    print(f"=== AUDIT ALL ACTIVE STUDENTS (Total Active: {len(students)}) ===")
    
    issues = []
    zero_rem_count = 0
    valid_rem_count = 0
    no_schedule_count = 0

    for st in students:
        s_code = st['code']
        s_name = st['full_name']
        c_name = st['class_name'] or 'Chưa phân lớp'
        sch = st['schedule'] or ''
        total = st['total_sessions'] or 0
        rem = st['remaining_sessions'] if st['remaining_sessions'] is not None else 0
        exp = st['expiry_date'] or ''

        # If schedule is missing from student record, try fetching from class record
        if not sch and st['class_name']:
            c_first = st['class_name'].split(',')[0].strip()
            c.execute("SELECT schedule FROM classes WHERE class_name = ?", (c_first,))
            cls_row = c.fetchone()
            if cls_row and cls_row['schedule']:
                sch = cls_row['schedule']

        if not sch:
            no_schedule_count += 1

        if rem <= 0:
            zero_rem_count += 1
            # Check if expiry_date is a future date (which could be misleading)
            if exp and exp != 'Đã hết phí' and '/' in exp:
                try:
                    parts = exp.split('/')
                    exp_dt = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
                    if exp_dt > datetime.date.today():
                        issues.append({
                            'code': s_code,
                            'name': s_name,
                            'class': c_name,
                            'rem': rem,
                            'current_exp': exp,
                            'type': 'ZERO_REM_FUTURE_EXPIRY'
                        })
                except Exception:
                    pass
        else:
            valid_rem_count += 1
            # Recalculate based on schedule
            calc_exp = calculate_fee_expiry_date(rem, sch)
            if calc_exp != exp:
                issues.append({
                    'code': s_code,
                    'name': s_name,
                    'class': c_name,
                    'sch': sch,
                    'rem': rem,
                    'current_exp': exp,
                    'calculated_exp': calc_exp,
                    'type': 'MISMATCH_EXPIRY'
                })

    print(f"\n--- Statistics ---")
    print(f"Total Active Students: {len(students)}")
    print(f"Students with Remaining Sessions > 0: {valid_rem_count}")
    print(f"Students with Remaining Sessions <= 0: {zero_rem_count}")
    print(f"Students with Missing Schedule: {no_schedule_count}")
    print(f"Total Discrepancies Found: {len(issues)}")

    if issues:
        print("\n--- Discrepancy Samples (First 20) ---")
        for i in issues[:20]:
            print(i)

    conn.close()

if __name__ == '__main__':
    audit_active_students()
