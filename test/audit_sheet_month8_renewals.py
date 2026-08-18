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

print(f"Total rows in Google Sheet 'Tái phí (từ 6/5/2026)': {len(raw_data)}")
if raw_data:
    print("Header row (row 0):", raw_data[0])
    print("Row 1:", raw_data[1] if len(raw_data) > 1 else '')
    print("Row 2:", raw_data[2] if len(raw_data) > 2 else '')

# Filter rows where month is 8 (or date is 08/2026 or August)
print("\nScanning all rows for Month 8/2026 in Sheet:")
month8_rows = []
for idx, row in enumerate(raw_data):
    row_str = " | ".join(row)
    if '8/2026' in row_str or '/8/2026' in row_str or '08/2026' in row_str or 'Tháng 8' in row_str:
        month8_rows.append((idx + 1, row))

print(f"Total rows matching Month 8/2026: {len(month8_rows)}")
for r in month8_rows:
    print(f"Row {r[0]}: {r[1]}")
