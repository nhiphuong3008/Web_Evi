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
        print("Cannot connect")
        return

    sp = service.spreadsheet
    ws = sp.worksheet('Nhập điểm (Import results)')
    rows = ws.get_all_values()
    print(f"Total rows in 'Nhập điểm (Import results)': {len(rows)}")

    valid_count = 0
    with_comments = 0
    sample_records = []

    for i, r in enumerate(rows[2:], start=3):
        if len(r) > 1 and r[1].strip() and r[1].strip().startswith('EVI'):
            valid_count += 1
            st_code = r[1].strip()
            name = r[2].strip() if len(r) > 2 else ''
            cname = r[4].strip() if len(r) > 4 else ''
            test_name = r[6].strip() if len(r) > 6 else ''
            l_score = r[8].strip() if len(r) > 8 else ''
            rw_score = r[9].strip() if len(r) > 9 else ''
            s_score = r[10].strip() if len(r) > 10 else ''
            comment = r[11].strip() if len(r) > 11 else ''

            if comment:
                with_comments += 1

            if len(sample_records) < 10:
                sample_records.append({
                    'row': i,
                    'code': st_code,
                    'name': name,
                    'class': cname,
                    'test': test_name,
                    'scores': f"L:{l_score}, RW:{rw_score}, S:{s_score}",
                    'comment': comment
                })

    print(f"Found {valid_count} valid student grade rows in this new sheet.")
    print(f"Found {with_comments} rows with teacher comments.")
    print("\nSample grade records:")
    for s in sample_records:
        print(f"  Row {s['row']}: [{s['code']}] {s['name']} | Class: {s['class']} | Test: {s['test']} | {s['scores']}")
        if s['comment']:
            print(f"    💬 Comment: {s['comment']}")

if __name__ == '__main__':
    inspect()
