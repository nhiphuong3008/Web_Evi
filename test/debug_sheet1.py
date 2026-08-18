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

print(f"Total rows in 'Báo cáo': {len(rows)}")
for idx, r in enumerate(rows[:60]):
    non_empty = [(i, c) for i, c in enumerate(r) if c.strip()]
    if non_empty:
        print(f"Row {idx+1}: {non_empty[:6]}")
