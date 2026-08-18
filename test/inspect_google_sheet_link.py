import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import get_config
from services.google_sheets import GoogleSheetsService
from services.data_parser import DataParser

def inspect_sheet():
    config = get_config()
    target_spreadsheet_id = "1wKcmRH9azv9urXvp-Ld4zWwmZ-iuGA2Vo30WzEkBR1I"

    print(f"Connecting to Google Sheets ID: {target_spreadsheet_id}...")
    svc = GoogleSheetsService(
        credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE,
        spreadsheet_id=target_spreadsheet_id
    )

    if not svc.connect():
        print("[FAIL] Cannot connect to Google Sheets using credentials!")
        return

    # Read sheet tabs info if available or read sheet_index 0
    print("[SUCCESS] Connected! Fetching sheet tabs...")
    try:
        worksheets = svc.spreadsheet.worksheets()
        print(f"Found {len(worksheets)} tabs in spreadsheet:")
        for idx, ws in enumerate(worksheets):
            clean_t = ws.title.encode('ascii', 'ignore').decode('ascii')
            print(f"  Tab {idx+1:2d}: '{clean_t}' (rows: {ws.row_count}, cols: {ws.col_count})")
    except Exception as e:
        print(f"Error fetching metadata: {e}")

if __name__ == '__main__':
    inspect_sheet()
