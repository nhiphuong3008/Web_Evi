import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

def inspect():
    cfg = config.get_config()
    service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not service.connect():
        print("Cannot connect to Google Sheets")
        return

    s1 = service.spreadsheet
    print("\n--- Worksheets in Sheet 1 ---")
    for w in s1.worksheets():
        print(f"Sheet 1 tab: {w.title}")

    # Inspect 'Điểm danh' tab
    try:
        ws_dd = s1.worksheet('Điểm danh')
        rows = ws_dd.get_all_values()
        print(f"\nTab 'Điểm danh' total rows: {len(rows)}")
        # Check student codes/names appearing multiple times
        student_classes = {}
        for r in rows[1:]:
            if len(r) > 5 and r[1].strip():
                code = r[0].strip().upper()
                name = r[1].strip()
                cname = r[5].strip()
                key = code if code else name.lower()
                if key not in student_classes:
                    student_classes[key] = {'code': code, 'name': name, 'classes': []}
                if cname and cname not in student_classes[key]['classes']:
                    student_classes[key]['classes'].append(cname)

        multi = {k: v for k, v in student_classes.items() if len(v['classes']) > 1}
        print(f"\nFound {len(multi)} students taking multiple classes in 'Điểm danh' tab:")
        for k, v in list(multi.items())[:15]:
            print(f"  - [{v['code']}] {v['name']}: {v['classes']}")
    except Exception as e:
        print(f"Error inspecting 'Điểm danh': {e}")

if __name__ == '__main__':
    inspect()
