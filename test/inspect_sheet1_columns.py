import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

def check_sheet1():
    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not svc.connect():
        print("Cannot connect")
        return

    sp1 = svc.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)

    # 1. DATA HS FULL PHÍ
    ws1 = sp1.worksheet('DATA HS FULL PHÍ')
    r1 = ws1.get_all_values()
    print("=== DATA HS FULL PHÍ ===")
    print("Row 0:", r1[0][:15])
    print("Row 1 (EVI001):", r1[1][:15])
    print("Row 5 (EVI005):", r1[5][:15])

    # 2. Điểm danh
    ws2 = sp1.worksheet('Điểm danh')
    r2 = ws2.get_all_values()
    print("\n=== Điểm danh ===")
    print("Row 0:", r2[0][:15])
    print("Row 1:", r2[1][:15])
    print("Row 5:", r2[5][:15])

if __name__ == '__main__':
    check_sheet1()
