import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

print("--- SHEET 3 (GRADES) TABS ---")
s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)
for w in s3.worksheets():
    if w.title != 'Data DSHS':
        vals = w.get_all_values()
        print(f"\nTab Grades: '{w.title}' (Total rows: {len(vals)})")
        for idx, row in enumerate(vals[:8]):
            print(f"  Row {idx+1}: {row[:8]}")

print("\n--- SHEET 2 (BTVN) TABS ---")
s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
w_rep = s2.worksheet('Báo cáo BVN')
vals_rep = w_rep.get_all_values()
print(f"\nTab BTVN 'Báo cáo BVN' (Total rows: {len(vals_rep)})")
for idx, row in enumerate(vals_rep[:20]):
    non_empty = [c for c in row if c.strip()]
    if non_empty:
        print(f"  Row {idx+1}: {row[:10]}")

w_data = s2.worksheet('Nhập KQ BVN')
vals_data = w_data.get_all_values()
print(f"\nTab BTVN 'Nhập KQ BVN' (Total rows: {len(vals_data)})")
for idx, row in enumerate(vals_data[:10]):
    print(f"  Row {idx+1}: {row[:10]}")
