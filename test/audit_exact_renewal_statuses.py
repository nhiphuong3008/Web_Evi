import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("""
    SELECT expiry_year, expiry_month, renewal_status, COUNT(*) 
    FROM renewal_detail_logs
    GROUP BY expiry_year, expiry_month, renewal_status
    ORDER BY expiry_year, expiry_month
""")
rows = c.fetchall()
print("Exact renewal_status in renewal_detail_logs from Google Sheets:")
for r in rows:
    print(f"Year {r[0]} | Month {r[1]} | Status: '{r[2]}' | Count: {r[3]}")

conn.close()
