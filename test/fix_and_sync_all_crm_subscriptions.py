import sys
import os
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

def fix_and_sync_all_crm_subscriptions():
    conn = sqlite3.connect('database/evi_center.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Fetch all active students from master students table
    c.execute("""
        SELECT code, full_name, english_name, class_name, cm_staff, expiry_date, expiry_month, expiry_year, remaining_sessions, status 
        FROM students 
        WHERE status = 'Đang học' AND expiry_date IS NOT NULL AND expiry_date != '' AND expiry_date != 'Đã hết phí'
    """)
    active_students = c.fetchall()
    print(f"📊 Found {len(active_students)} active students with valid expiration dates in `students` master table.")

    # Fetch existing student_subscriptions by student_code
    c.execute("SELECT student_code FROM student_subscriptions WHERE student_code IS NOT NULL AND student_code != ''")
    existing_sub_codes = set(r['student_code'].strip().upper() for r in c.fetchall() if r['student_code'])

    # Fetch existing student_renewals by student_code
    c.execute("SELECT student_code FROM student_renewals WHERE student_code IS NOT NULL AND student_code != ''")
    existing_ren_codes = set(r['student_code'].strip().upper() for r in c.fetchall() if r['student_code'])

    created_subs = 0
    created_rens = 0
    updated_subs = 0
    updated_rens = 0

    now_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')

    for st in active_students:
        code = st['code'].strip().upper() if st['code'] else ''
        if not code:
            continue

        exp_date = st['expiry_date'].strip()
        rem_sess = st['remaining_sessions'] or 0
        cls_name = st['class_name'] or ''
        cm_staff = st['cm_staff'] or ''
        name = st['full_name'] or ''
        eng_name = st['english_name'] or ''

        # Parse month & year from expiry_date if not present
        month_val = 8
        year_val = 2026
        parts = exp_date.split('/')
        if len(parts) == 3:
            try:
                month_val = int(parts[1])
                year_val = int(parts[2])
            except ValueError:
                pass

        # 1. Sync/Insert student_subscriptions
        if code in existing_sub_codes:
            c.execute("""
                UPDATE student_subscriptions 
                SET current_end_date = ?, original_end_date = ?, remaining_sessions = ?, class_name = ?, cm_staff = ?, student_name = ?, english_name = ?, updated_at = ?
                WHERE UPPER(student_code) = ?
            """, (exp_date, exp_date, rem_sess, cls_name, cm_staff, name, eng_name, now_str, code))
            updated_subs += 1
        else:
            sub_id_str = f"SUB-{code}-{month_val}-{year_val}"
            c.execute("""
                INSERT INTO student_subscriptions 
                (subscription_id, student_code, student_name, english_name, class_name, cm_staff, start_date, original_end_date, current_end_date, remaining_sessions, renewal_status, pipeline_stage, is_cm_locked, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Upcoming', 'D-30', 0, '', ?, ?)
            """, (sub_id_str, code, name, eng_name, cls_name, cm_staff, '01/01/2026', exp_date, exp_date, rem_sess, now_str, now_str))
            created_subs += 1

        # 2. Sync/Insert student_renewals
        if code in existing_ren_codes:
            c.execute("""
                UPDATE student_renewals
                SET expected_expiry_date = ?, month = ?, year = ?, class_name = ?, cm_staff = ?, student_name = ?, english_name = ?
                WHERE UPPER(student_code) = ?
            """, (exp_date, month_val, year_val, cls_name, cm_staff, name, eng_name, code))
            updated_rens += 1
        else:
            c.execute("""
                INSERT INTO student_renewals
                (student_code, student_name, english_name, class_name, cm_staff, month, year, status, expected_expiry_date, fee_package, amount, due_date, notes, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, '72 buổi', 7200000.0, ?, '', 'Admin', ?)
            """, (code, name, eng_name, cls_name, cm_staff, month_val, year_val, exp_date, exp_date, now_str))
            created_rens += 1

    conn.commit()

    print(f"🎉 Created {created_subs} new Subscription records and {created_rens} new Renewal records.")
    print(f"🔄 Updated {updated_subs} existing Subscription records and {updated_rens} existing Renewal records.")

    # Check Month 7 / Year 2027 subscriptions after sync
    c.execute("SELECT student_code, student_name, class_name, current_end_date FROM student_subscriptions WHERE current_end_date LIKE '%/07/2027'")
    m7_subs = c.fetchall()
    print(f"\n📅 Total subscriptions for Month 7/2027 after sync: {len(m7_subs)}")
    for s in m7_subs:
        print("  - Subscription Month 7/2027:", dict(s))

    conn.close()

if __name__ == '__main__':
    fix_and_sync_all_crm_subscriptions()
