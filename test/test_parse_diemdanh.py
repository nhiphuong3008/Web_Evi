import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService
from services.data_parser import parse_number

def test_diemdanh_tab():
    cfg = config.get_config()
    service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not service.connect():
        print("Failed to connect")
        return

    s1 = service.spreadsheet
    ws = s1.worksheet('Điểm danh')
    rows = ws.get_all_values()
    print(f"Total rows in 'Điểm danh': {len(rows)}")

    # Header in row 0
    if len(rows) > 0:
        print("Header row 0:", rows[0][:15])
    if len(rows) > 1:
        print("Sample row 1:", rows[1][:15])
    if len(rows) > 200:
        print("Sample row 200:", rows[200][:15])

if __name__ == '__main__':
    test_diemdanh_tab()
