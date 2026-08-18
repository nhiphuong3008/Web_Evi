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

s1 = service.spreadsheet
s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)

tabs_to_check = [
    (s1, 'DATA HS FULL PHÍ'),
    (s1, 'DATA LỚP HỌC'),
    (s1, 'Tái phí'),
    (s2, 'Data DSHS'),
    (s3, 'Data DSHS'),
]

for sp, tab_name in tabs_to_check:
    try:
        ws = sp.worksheet(tab_name)
        rows = ws.get_all_values()
        print(f"\n=======================================================")
        print(f"Spreadsheet: '{sp.title}' | Tab: '{tab_name}' (Total Rows: {len(rows)})")
        print(f"=======================================================")
        for idx in range(min(5, len(rows))):
            non_empty = [(i, val) for i, val in enumerate(rows[idx]) if val.strip()]
            if non_empty:
                print(f"  Row {idx+1}: {non_empty[:12]}")
    except Exception as e:
        print(f"Error checking '{tab_name}': {e}")
