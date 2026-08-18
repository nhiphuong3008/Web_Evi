import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("""
    SELECT source_tab, expiry_month, expiry_year, COUNT(*) 
    FROM renewal_detail_logs 
    GROUP BY source_tab, expiry_year, expiry_month
    ORDER BY expiry_year DESC, expiry_month DESC
""")
rows = c.fetchall()
print("Breakdown of renewal_detail_logs by source_tab, expiry_year, expiry_month:")
for r in rows:
    print(r)

conn.close()
