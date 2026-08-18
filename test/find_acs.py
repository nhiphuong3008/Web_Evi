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

ws = service.spreadsheet.worksheet('Báo cáo')
rows = ws.get_all_values()

print("Searching for ACS and Total Students in 'Báo cáo'...")
for idx, r in enumerate(rows):
    row_str = ' '.join(r)
    if 'ACS' in row_str or 'Tổng số HS' in row_str or 'TB' in row_str or '207' in row_str:
        print(f"Row {idx+1}: {[(i, val) for i, val in enumerate(r) if val.strip()]}")
