import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

def inspect_nxht():
    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not svc.connect(): return

    sp2 = svc.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
    ws = sp2.worksheet('NXHT MT_B5_Sun 2.4')
    rows = ws.get_all_values()
    print(f"=== NXHT MT_B5_Sun 2.4 ({len(rows)} rows) ===")
    for idx, r in enumerate(rows[:15]):
        print(f"Row {idx}: {r[:10]}")

if __name__ == '__main__':
    inspect_nxht()
