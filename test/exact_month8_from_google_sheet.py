import os
import sys
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

# Header: Col 11 is Tháng hết phí (idx 11), Col 12 is Năm hết phí (idx 12)
month8_exact = []
for idx, row in enumerate(raw_data[1:], start=2):
    if len(row) > 12:
        m_str = row[11].strip()
        y_str = row[12].strip()
        if m_str == '8' and y_str == '2026':
            st_code = row[0].strip()
            st_name = row[1].strip()
            cls_name = row[3].strip()
            cm = row[6].strip()
            exp_date = row[10].strip()
            status = row[13].strip()
            month8_exact.append((idx, st_code, st_name, cls_name, cm, exp_date, status))

print(f"Total rows where Col 11 == '8' and Col 12 == '2026': {len(month8_exact)}\n")
print(f"{'Row':4} | {'Code':7} | {'Name':25} | {'Class':10} | {'CM':10} | {'Exp Date':10} | {'Status':12}")
print("-" * 90)
for r in month8_exact:
    print(f"{r[0]:4} | {r[1]:7} | {r[2]:25} | {r[3]:10} | {r[4]:10} | {r[5]:10} | '{r[6]}'")

conn_stats = {}
for r in month8_exact:
    cm = r[4] or 'Chưa phân công'
    st = r[6] or 'Chưa tái phí'
    if cm not in conn_stats:
        conn_stats[cm] = {'total': 0, 'success': 0, 'stacked': 0, 'pending': 0, 'failed': 0}
    conn_stats[cm]['total'] += 1
    if st == 'Thành công': conn_stats[cm]['success'] += 1
    elif st == 'Chồng phí': conn_stats[cm]['stacked'] += 1
    elif st in ('Chưa tái phí', ''): conn_stats[cm]['pending'] += 1
    elif st == 'Thất bại': conn_stats[cm]['failed'] += 1
    else: conn_stats[cm]['pending'] += 1

print("\nEXACT SUMMARY FROM GOOGLE SHEET FOR MONTH 8/2026:")
print(json.dumps(conn_stats, ensure_ascii=False, indent=2))
