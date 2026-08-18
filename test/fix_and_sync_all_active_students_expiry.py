import sys
import os
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import calculate_fee_expiry_date

def sync_all_active_students_expiry():
    conn = sqlite3.connect('database/evi_center.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Fetch class schedule mapping
    c.execute("SELECT class_name, schedule FROM classes WHERE schedule IS NOT NULL AND schedule != ''")
    class_schedule_map = {}
    for row in c.fetchall():
        class_schedule_map[row['class_name'].strip()] = row['schedule'].strip()

    # 2. Fetch all active students
    c.execute("""
        SELECT id, code, full_name, class_name, schedule, total_sessions, remaining_sessions, expiry_date 
        FROM students 
        WHERE status = 'Đang học'
    """)
    students = c.fetchall()

    updated_count = 0
    synced_list = []

    for st in students:
        s_id = st['id']
        s_code = st['code']
        s_name = st['full_name']
        c_name = st['class_name'] or ''
        sch = (st['schedule'] or '').strip()
        rem = st['remaining_sessions'] if st['remaining_sessions'] is not None else 0

        # Backfill schedule from class if missing
        if not sch and c_name:
            c_first = c_name.split(',')[0].strip()
            sch = class_schedule_map.get(c_first, '')

        # Calculate exact expiry date according to remaining sessions & schedule
        if rem <= 0:
            # Check if student is EVI305 (Minh Hưng) -> Keep 10/08/2026
            if s_code == 'EVI305':
                new_exp = '10/08/2026'
            else:
                new_exp = 'Đã hết phí'
        else:
            new_exp = calculate_fee_expiry_date(rem, sch)

        month_val = ''
        year_val = ''
        if new_exp and '/' in new_exp:
            try:
                p = new_exp.split('/')
                if len(p) == 3:
                    month_val = str(int(p[1]))
                    year_val = p[2]
            except Exception:
                pass

        c.execute("""
            UPDATE students 
            SET schedule = ?, expiry_date = ?, expiry_month = ?, expiry_year = ?
            WHERE id = ?
        """, (sch, new_exp, month_val, year_val, s_id))
        
        updated_count += 1
        synced_list.append({
            'code': s_code,
            'name': s_name,
            'class': c_name,
            'rem': rem,
            'sch': sch,
            'expiry_date': new_exp
        })

    conn.commit()
    print(f"✅ Successfully audited and updated expiry dates for ALL {updated_count} active students!")

    # Summary table output
    print("\n--- SAMPLE ACTIVE STUDENTS WITH RECALCULATED EXPIRY DATES ---")
    for st in synced_list[:15]:
        print(f"[{st['code']}] {st['name']} ({st['class']}) - Rem: {st['rem']} sessions - Expiry: {st['expiry_date']}")

    conn.close()

if __name__ == '__main__':
    sync_all_active_students_expiry()
