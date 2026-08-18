import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("""
    SELECT student_code, student_name, class_name, cm_staff, expiry_date, expiry_month, expiry_year, renewal_status, interaction_note
    FROM renewal_detail_logs
    WHERE expiry_month IN ('7', '8', '9', '10', '11', '12') AND expiry_year = '2026'
    LIMIT 20
""")
rows = c.fetchall()
print("Sample valid renewal detail logs:")
for r in rows:
    print(r)

conn.close()
