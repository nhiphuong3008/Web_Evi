import sys
import os
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import calculate_fee_expiry_date

def restore_primary_courses():
    conn = sqlite3.connect('database/evi_center.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT code, full_name, class_name, total_sessions, remaining_sessions, expiry_date FROM students WHERE status = 'Đang học'")
    students = c.fetchall()

    restored_count = 0
    restored_details = []

    for st in students:
        s_code = st['code']
        st_tot = st['total_sessions'] or 0
        st_rem = st['remaining_sessions'] or 0

        # Check if there is a primary course record in renewal_detail_logs with larger total sessions
        c.execute("""
            SELECT total_sessions, remaining_sessions, expiry_date, class_name, schedule 
            FROM renewal_detail_logs 
            WHERE student_code = ? AND total_sessions > ?
            ORDER BY id DESC LIMIT 1
        """, (s_code, max(st_tot, 30)))
        
        log = c.fetchone()
        if log:
            primary_total = log['total_sessions']
            primary_rem = log['remaining_sessions']
            primary_exp = log['expiry_date']

            # If remaining_sessions in log is positive, recalculate expiry date accurately
            if primary_rem > 0:
                sch = log['schedule'] or st['class_name'] or ''
                calc_exp = calculate_fee_expiry_date(primary_rem, sch)
                if calc_exp and '/' in calc_exp:
                    primary_exp = calc_exp

            # Parse month/year
            month_val = ''
            year_val = ''
            if primary_exp and '/' in primary_exp:
                parts = primary_exp.split('/')
                if len(parts) == 3:
                    month_val = str(int(parts[1]))
                    year_val = parts[2]

            # Store short-course info in fee_package_1 before updating
            short_pkg_info = f"Khóa bổ trợ/ngắn hạn: {st_tot} buổi (Còn {st_rem} buổi - Hạn: {st['expiry_date']})"

            c.execute("""
                UPDATE students 
                SET total_sessions = ?, remaining_sessions = ?, expiry_date = ?, expiry_month = ?, expiry_year = ?, fee_package_1 = ?
                WHERE code = ?
            """, (primary_total, primary_rem, primary_exp, month_val, year_val, short_pkg_info, s_code))

            restored_count += 1
            restored_details.append({
                'code': s_code,
                'name': st['full_name'],
                'primary_tot': primary_total,
                'primary_rem': primary_rem,
                'primary_exp': primary_exp,
                'short_info': short_pkg_info
            })

    conn.commit()
    print(f"✅ Successfully restored Primary Course (Khóa chính dài hạn) for {restored_count} active students!")
    print("\n--- RESTORED STUDENTS SAMPLE ---")
    for r in restored_details[:10]:
        print(f"[{r['code']}] {r['name']} | Primary Course: {r['primary_tot']} total, {r['primary_rem']} rem, Expiry: {r['primary_exp']} | {r['short_info']}")

    conn.close()

if __name__ == '__main__':
    restore_primary_courses()
