import sys
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

# Sheet 1 (Main Dashboard & Report & 'Tổng 2025')
s1 = service.spreadsheet
print(f"=== SPREADSHEET 1 TABS ({s1.title}): ===")
for w in s1.worksheets():
    print(f"  - '{w.title}'")

# Sheet 2 (BTVN)
s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
print(f"\n=== SPREADSHEET 2 TABS ({s2.title}): ===")
for w in s2.worksheets():
    print(f"  - '{w.title}'")

# Sheet 3 (Grades)
s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)
print(f"\n=== SPREADSHEET 3 TABS ({s3.title}): ===")
for w in s3.worksheets():
    print(f"  - '{w.title}'")

# Inspect tab 'Tổng 2025' in Sheet 1 if exists
try:
    ws_tong = s1.worksheet('Tổng 2025')
    rows_tong = ws_tong.get_all_values()
    print(f"\n=== TAB 'Tổng 2025' (Rows: {len(rows_tong)}) ===")
    for idx, r in enumerate(rows_tong[:15]):
        non_empty = [(i, val) for i, val in enumerate(r) if val.strip()]
        if non_empty:
            print(f"  Row {idx+1}: {non_empty[:10]}")
except Exception as e:
    print(f"Could not open 'Tổng 2025': {e}")
