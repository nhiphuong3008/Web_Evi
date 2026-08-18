import sys
import os
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database/evi_center.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT code, full_name, class_name, total_sessions, remaining_sessions, expiry_date FROM students WHERE status = 'Đang học'")
students = c.fetchall()

mismatch_count = 0
print("=== CHECKING SHORT-COURSE OVERWRITE VS LONG-COURSE DATA IN DB ===")

for st in students:
    s_code = st['code']
    s_name = st['full_name']
    c_name = st['class_name'] or ''
    st_tot = st['total_sessions'] or 0
    st_rem = st['remaining_sessions'] or 0
    st_exp = st['expiry_date'] or ''

    c.execute("SELECT total_sessions, remaining_sessions, expiry_date, source_tab FROM renewal_detail_logs WHERE student_code = ? ORDER BY id DESC LIMIT 1", (s_code,))
    log = c.fetchone()
    if log:
        log_tot = log['total_sessions'] or 0
        log_rem = log['remaining_sessions'] or 0
        log_exp = log['expiry_date'] or ''

        # If log has long-term course data (e.g., total > 50) while students table has short-term package (e.g. 15)
        if log_tot > st_tot + 20 or log_rem > st_rem + 15:
            mismatch_count += 1
            print(f"[{s_code}] {s_name} ({c_name})")
            print(f"   --> Students Table (Short Course): {st_tot} total | {st_rem} rem | Expiry: {st_exp}")
            print(f"   --> Renewal Logs (Long Course) : {log_tot} total | {log_rem} rem | Expiry: {log_exp}")

print(f"\nTotal students affected by Short-Course Overwrite issue: {mismatch_count}")
conn.close()
