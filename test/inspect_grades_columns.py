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

s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)

for w in s3.worksheets():
    if w.title == 'Data DSHS':
        continue
    
    rows = w.get_all_values()
    print(f"\n==========================================")
    print(f"WORKSHEET TAB: '{w.title}' (Total rows: {len(rows)})")
    print(f"==========================================")
    
    for idx, r in enumerate(rows[:6]):
        print(f"  Row {idx+1}: {r}")
