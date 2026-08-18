import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("""
    SELECT student_code, student_name, class_name, expiry_date, expiry_month, expiry_year, total_sessions, remaining_sessions, source_tab
    FROM renewal_detail_logs
    WHERE expiry_year IN ('2027', '2028')
    LIMIT 10
""")
rows = c.fetchall()
print("Sample students with 2027 / 2028 expiry dates in Google Sheets tabs:")
for r in rows:
    print(r)

conn.close()
