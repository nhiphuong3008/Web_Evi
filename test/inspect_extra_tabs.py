import sys
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

print("=== CHECKING HEADERS OF EXTRA TABS IN SHEET 1 ===")

for tab in ['DATA HS FULL PHÍ', 'Tái phí', 'Withdraw', 'Độ tuổi']:
    try:
        ws = s1.worksheet(tab)
        rows = ws.get_all_values()
        print(f"\nTab '{tab}' (Rows: {len(rows)}):")
        if rows:
            print(f"  Header 1: {rows[0][:15]}")
            if len(rows) > 1:
                print(f"  Sample Row 2: {rows[1][:15]}")
    except Exception as e:
        print(f"Error checking '{tab}': {e}")
