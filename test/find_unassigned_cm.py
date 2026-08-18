import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("""
    SELECT id, student_code, student_name, class_name, cm_staff, month, year, status, notes
    FROM student_renewals
    WHERE month = 8 AND year = 2026 AND (cm_staff IS NULL OR cm_staff = '' OR cm_staff = 'Chưa phân công')
""")
rows = c.fetchall()
print("Records in student_renewals for Month 8/2026 with empty/NULL cm_staff:")
for r in rows:
    print(r)

# Also check renewal_detail_logs for those student_codes to see what raw data was in Google Sheets
for r in rows:
    code = r[1]
    name = r[2]
    c.execute("SELECT student_code, student_name, class_name, cm_staff, source_tab FROM renewal_detail_logs WHERE student_code = ? OR student_name = ?", (code, name))
    print(f"\nRaw log for {code} - {name}:", c.fetchall())

conn.close()
