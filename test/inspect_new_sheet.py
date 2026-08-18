import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

NEW_SHEET_ID = "1BkNjEfYBXNjY4GyZOhhAVWgOk7t7sNWhxFdpA84vM6o"

def inspect():
    cfg = config.get_config()
    service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, NEW_SHEET_ID)
    if not service.connect():
        print("Cannot connect to new spreadsheet")
        return

    sp = service.spreadsheet
    print(f"Spreadsheet Title: {sp.title}")
    print(f"\n--- Worksheets in new sheet ({len(sp.worksheets())}) ---")
    for w in sp.worksheets():
        print(f"\nTab: {w.title}")
        rows = w.get_all_values()
        print(f"  Total rows: {len(rows)}")
        if len(rows) > 0:
            print(f"  Row 0 (Header): {rows[0][:15]}")
        if len(rows) > 1:
            print(f"  Row 1 (Sample): {rows[1][:15]}")
        if len(rows) > 2:
            print(f"  Row 2 (Sample): {rows[2][:15]}")

if __name__ == '__main__':
    inspect()
