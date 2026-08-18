import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

def inspect_schedule():
    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not svc.connect():
        print("Cannot connect")
        return

    sp1 = svc.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    ws = sp1.worksheet('Schedule')
    rows = ws.get_all_values()
    print(f"Total rows in 'Schedule' tab: {len(rows)}")
    print("\nFirst 15 rows:")
    for idx, r in enumerate(rows[:15]):
        print(f"Row {idx}: {r}")

if __name__ == '__main__':
    inspect_schedule()
