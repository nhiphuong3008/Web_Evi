import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("""
    SELECT source_tab, expiry_month, expiry_year, renewal_status, COUNT(*)
    FROM renewal_detail_logs
    WHERE source_tab LIKE '%6/5/2026%' OR source_tab LIKE '%2026%'
    GROUP BY source_tab, expiry_year, expiry_month, renewal_status
    ORDER BY expiry_year, expiry_month, renewal_status
""")
rows = c.fetchall()
print("Breakdown of renewal_detail_logs ONLY for Tab Tái phí (từ 6/5/2026):")
for r in rows:
    print(r)

conn.close()
