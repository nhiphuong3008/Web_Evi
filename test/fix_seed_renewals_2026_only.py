import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

# 1. Clear student_renewals completely
c.execute("DELETE FROM student_renewals")
print("Cleared student_renewals table.")

# 2. Fetch ONLY records from tab 'Tái phí (từ 6/5/2026)'
c.execute("""
    SELECT student_code, student_name, english_name, class_name, cm_staff, expiry_month, expiry_year, expiry_date, renewal_status, interaction_note
    FROM renewal_detail_logs
    WHERE source_tab LIKE '%6/5/2026%'
      AND expiry_month IS NOT NULL AND expiry_month != '' AND expiry_month != '#VALUE!'
      AND expiry_year = '2026'
""")
logs = c.fetchall()
print(f"Total 2026 renewal records from tab 'Tái phí (từ 6/5/2026)': {len(logs)}")

status_map = {
    'thành công': 'success',
    'chồng phí': 'stacked',
    'chưa tái phí': 'pending',
    'thất bại': 'failed',
    'chuyển phí': 'pending'
}

inserted = 0

for log in logs:
    st_code = (log[0] or '').strip().upper()
    st_name = (log[1] or '').strip()
    en_name = (log[2] or '').strip()
    cls_name = (log[3] or '').strip()
    cm = (log[4] or '').strip()
    try:
        m = int(log[5])
        y = int(log[6])
    except ValueError:
        continue
    exp_date = (log[7] or '').strip()
    raw_status = (log[8] or '').strip().lower()
    notes = (log[9] or '').strip()

    status_code = status_map.get(raw_status, 'pending')

    c.execute("""
        INSERT INTO student_renewals (student_code, student_name, english_name, class_name, cm_staff, month, year, status, expected_expiry_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (st_code, st_name, en_name, cls_name, cm, m, y, status_code, exp_date, notes))
    inserted += 1

conn.commit()

c.execute("SELECT month, year, COUNT(*), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END), SUM(CASE WHEN status='stacked' THEN 1 ELSE 0 END), SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END), SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) FROM student_renewals GROUP BY year, month ORDER BY year, month")
print("\nExact 2026 Renewals distribution in CSDL:")
print("Month/Year | Total | Success | Stacked | Pending | Failed")
print("-" * 55)
for r in c.fetchall():
    print(f"Tháng {r[0]}/{r[1]} | {r[2]:5} | {r[3]:7} | {r[4]:7} | {r[5]:7} | {r[6]:6}")

conn.close()
