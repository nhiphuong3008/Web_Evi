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
    ws = sp1.worksheet('SCHEDULE')
    rows = ws.get_all_values()
    print(f"=== SCHEDULE Tab ({len(rows)} rows) ===")
    for idx, r in enumerate(rows[:25]):
        print(f"Row {idx}: {r}")

    print("\nCheck if there are more rows with data:")
    non_empty = [ (idx, r) for idx, r in enumerate(rows) if any(r) ]
    print(f"Total non-empty rows: {len(non_empty)}")
    for idx, r in non_empty[:20]:
        print(f"  Line {idx}: {r[:10]}")

if __name__ == '__main__':
    inspect_schedule()
