import os
import sys
import sqlite3
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

ws = service.spreadsheet.worksheet('Tái phí (từ 6/5/2026)')
raw_data = ws.get_all_values()

print(f"Reading Google Sheet 'Tái phí (từ 6/5/2026)': {len(raw_data)} rows")

status_map = {
    'thành công': 'success',
    'chồng phí': 'stacked',
    'chưa tái phí': 'pending',
    'thất bại': 'failed',
    'chuyển phí': 'pending'
}

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

# Clear student_renewals table
c.execute("DELETE FROM student_renewals")

synced = 0
skipped = 0

for idx, row in enumerate(raw_data[1:], start=2):
    if len(row) <= 12:
        continue
    st_code = row[0].strip().upper()
    st_name = row[1].strip()
    en_name = row[2].strip()
    cls_name = row[3].strip()
    cm = row[6].strip()
    exp_date = row[10].strip()
    m_str = row[11].strip()
    y_str = row[12].strip()
    raw_status = row[13].strip().lower()
    notes = row[15].strip() if len(row) > 15 else ''

    if not m_str or not y_str or m_str.startswith('#') or y_str.startswith('#'):
        skipped += 1
        continue

    try:
        m = int(m_str)
        y = int(y_str)
    except ValueError:
        skipped += 1
        continue

    # Only include 2026 active tracking year
    if y != 2026:
        skipped += 1
        continue

    status_code = status_map.get(raw_status, 'pending')

    c.execute("""
        INSERT INTO student_renewals (student_code, student_name, english_name, class_name, cm_staff, month, year, status, expected_expiry_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (st_code, st_name, en_name, cls_name, cm, m, y, status_code, exp_date, notes))
    synced += 1

conn.commit()
print(f"Synced {synced} exact rows for 2026 from Sheet. Skipped {skipped} rows.")

c.execute("SELECT month, year, COUNT(*), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END), SUM(CASE WHEN status='stacked' THEN 1 ELSE 0 END), SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END), SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) FROM student_renewals WHERE year=2026 GROUP BY year, month ORDER BY month")
print("\nEXACT 2026 RENEWALS SUMMARY IN DB:")
print("Month/Year | Total | Success | Stacked | Pending | Failed")
print("-" * 55)
for r in c.fetchall():
    print(f"Tháng {r[0]}/{r[1]} | {r[2]:5} | {r[3]:7} | {r[4]:7} | {r[5]:7} | {r[6]:6}")

conn.close()
