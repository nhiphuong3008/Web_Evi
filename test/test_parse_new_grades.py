import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService
from services.data_parser import parse_float_vn

NEW_SHEET_ID = "1BkNjEfYBXNjY4GyZOhhAVWgOk7t7sNWhxFdpA84vM6o"

def test_parse():
    cfg = config.get_config()
    service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, NEW_SHEET_ID)
    if not service.connect():
        print("Failed to connect")
        return

    sp = service.spreadsheet
    ws = sp.worksheet('Nhập điểm (Import results)')
    rows = ws.get_all_values()
    print(f"Total rows: {len(rows)}")

    records = []
    for r in rows[2:]:
        if len(r) > 1 and r[1].strip() and r[1].strip().startswith('EVI'):
            month_str = r[0].strip() if len(r) > 0 else ''
            st_code = r[1].strip().upper()
            name = r[2].strip() if len(r) > 2 else ''
            en_name = r[3].strip() if len(r) > 3 else ''
            cname = r[4].strip() if len(r) > 4 else ''
            gv = r[5].strip() if len(r) > 5 else ''
            test_name = r[6].strip() if len(r) > 6 else ''
            tot_sc = parse_float_vn(r[7]) if len(r) > 7 else None
            lis_sc = parse_float_vn(r[8]) if len(r) > 8 and r[8].strip() else None
            rw_sc = parse_float_vn(r[9]) if len(r) > 9 and r[9].strip() else None
            spk_sc = parse_float_vn(r[10]) if len(r) > 10 and r[10].strip() else None
            comment = r[11].strip() if len(r) > 11 else ''

            if test_name or lis_sc is not None or rw_sc is not None or spk_sc is not None or comment:
                records.append({
                    'code': st_code,
                    'name': name,
                    'english_name': en_name,
                    'class_name': cname,
                    'teacher': gv,
                    'test_name': test_name or 'Bài kiểm tra',
                    'listening': lis_sc,
                    'reading_writing': rw_sc,
                    'speaking': spk_sc,
                    'total_score': tot_sc,
                    'comment': comment,
                    'month': month_str
                })

    print(f"Successfully parsed {len(records)} grade records!")
    print("First 5 records sample:")
    for rec in records[:5]:
        print(rec)

if __name__ == '__main__':
    test_parse()
