import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

def find_schedule_tabs():
    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not svc.connect():
        print("Cannot connect")
        return

    sheets = {
        'Sheet 1 (Master)': cfg.GOOGLE_SHEETS_SPREADSHEET_ID,
        'Sheet 2 (BTVN)': getattr(cfg, 'GOOGLE_SHEETS_BTVN_ID', None),
        'Sheet 3 (Old Grades)': getattr(cfg, 'GOOGLE_SHEETS_GRADES_ID', None),
        'Sheet 4 (New Grades)': getattr(cfg, 'GOOGLE_SHEETS_NEW_GRADES_ID', '1BkNjEfYBXNjY4GyZOhhAVWgOk7t7sNWhxFdpA84vM6o')
    }

    for name, key in sheets.items():
        if not key: continue
        try:
            sp = svc.client.open_by_key(key)
            title = sp.title
            ws_titles = [w.title for w in sp.worksheets()]
            print(f"\nSpreadsheet: '{name}' (Title: '{title}')")
            print(f"  Worksheets ({len(ws_titles)}): {ws_titles}")
        except Exception as e:
            print(f"  Error reading {name}: {e}")

if __name__ == '__main__':
    find_schedule_tabs()
