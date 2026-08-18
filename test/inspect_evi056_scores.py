import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

def find_evi056():
    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not svc.connect():
        print("Cannot connect")
        return

    sheet_ids = [
        ("Sheet 1 (Master)", cfg.GOOGLE_SHEETS_SPREADSHEET_ID),
        ("Sheet 2 (BTVN)", cfg.GOOGLE_SHEETS_BTVN_ID),
        ("Sheet 3 (Grades)", cfg.GOOGLE_SHEETS_GRADES_ID),
        ("Sheet 4 (New Grades)", cfg.GOOGLE_SHEETS_NEW_GRADES_ID)
    ]

    for label, sid in sheet_ids:
        try:
            sp = svc.client.open_by_key(sid)
            print(f"\n==========================================")
            print(f"Searching in {label} ({sp.title})...")
            print(f"==========================================")

            for ws in sp.worksheets():
                rows = ws.get_all_values()
                found = []
                for idx, r in enumerate(rows):
                    r_str = " | ".join(r).lower()
                    if 'evi056' in r_str or 'nguyễn ngọc huyền' in r_str:
                        found.append((idx + 1, r[:12]))
                if found:
                    print(f"\n  Tab [{ws.title}]: Found {len(found)} rows")
                    for row_num, content in found[:5]:
                        print(f"    Line {row_num}: {content}")
        except Exception as e:
            print(f"Error checking {label}: {e}")

if __name__ == '__main__':
    find_evi056()
