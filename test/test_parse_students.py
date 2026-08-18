import sys
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
from services.data_parser import parse_number
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

s1 = service.spreadsheet
s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)

def parse_students_master():
    students_dict = {}

    # 1. Read 'DATA HS FULL PHÍ' from Sheet 1
    try:
        ws_full = s1.worksheet('DATA HS FULL PHÍ')
        rows = ws_full.get_all_values()
        if len(rows) > 1:
            for r in rows[1:]:
                if len(r) < 3 or not r[1].strip():
                    continue
                code = r[1].strip().upper()
                name = r[2].strip()
                en_name = r[3].strip() if len(r) > 3 else ''
                dob = r[4].strip() if len(r) > 4 else ''
                parent = r[5].strip() if len(r) > 5 else ''
                phone = r[6].strip() if len(r) > 6 else ''
                address = r[7].strip() if len(r) > 7 else ''
                status = r[8].strip() if len(r) > 8 else 'Đang học'

                students_dict[code] = {
                    'code': code,
                    'name': name,
                    'english_name': en_name,
                    'dob': dob,
                    'parent_name': parent,
                    'phone': phone,
                    'address': address,
                    'status': status or 'Đang học',
                    'class_name': '',
                    'schedule': '',
                    'teacher': '',
                    'cm': '',
                    'ta': '',
                    'total_sessions': 0,
                    'remaining_sessions': 0,
                    'expiry_date': '',
                    'expiry_month': '',
                }
    except Exception as e:
        print(f"Error reading DATA HS FULL PHÍ: {e}")

    # 2. Read 'Data DSHS' from Sheet 2 or Sheet 3 to enrich class, teacher, sessions
    try:
        ws_dshs = s2.worksheet('Data DSHS')
        rows = ws_dshs.get_all_values()
        if len(rows) > 3:
            for r in rows[3:]:
                if len(r) < 2 or not r[0].strip():
                    continue
                code = r[0].strip().upper()
                name = r[1].strip() if len(r) > 1 else ''
                en_name = r[2].strip() if len(r) > 2 else ''
                parent = r[3].strip() if len(r) > 3 else ''
                phone = r[4].strip() if len(r) > 4 else ''
                c_name = r[5].strip() if len(r) > 5 else ''
                sched = r[6].strip() if len(r) > 6 else ''
                gv = r[7].strip() if len(r) > 7 else ''
                cm = r[8].strip() if len(r) > 8 else ''
                ta = r[9].strip() if len(r) > 9 else ''
                tot_sess = parse_number(r[10]) if len(r) > 10 else 0
                rem_sess = parse_number(r[11]) if len(r) > 11 else 0

                if code not in students_dict:
                    students_dict[code] = {
                        'code': code,
                        'name': name,
                        'english_name': en_name,
                        'dob': '',
                        'parent_name': parent,
                        'phone': phone,
                        'address': '',
                        'status': 'Đang học',
                    }

                st = students_dict[code]
                if name and not st.get('name'): st['name'] = name
                if en_name: st['english_name'] = en_name
                if parent and not st.get('parent_name'): st['parent_name'] = parent
                if phone and not st.get('phone'): st['phone'] = phone
                st['class_name'] = c_name
                st['schedule'] = sched
                st['teacher'] = gv
                st['cm'] = cm
                st['ta'] = ta
                st['total_sessions'] = tot_sess
                st['remaining_sessions'] = rem_sess
    except Exception as e:
        print(f"Error reading Data DSHS: {e}")

    # 3. Read 'Tái phí' from Sheet 1 to enrich expiry date/month
    try:
        ws_tai = s1.worksheet('Tái phí')
        rows = ws_tai.get_all_values()
        if len(rows) > 1:
            for r in rows[1:]:
                if len(r) < 2 or not r[0].strip():
                    continue
                code = r[0].strip().upper()
                exp_date = r[10].strip() if len(r) > 10 else ''
                exp_month = r[11].strip() if len(r) > 11 else ''

                if code in students_dict:
                    st = students_dict[code]
                    if exp_date and exp_date != '#VALUE!': st['expiry_date'] = exp_date
                    if exp_month and exp_month != '#VALUE!': st['expiry_month'] = exp_month
    except Exception as e:
        print(f"Error reading Tái phí: {e}")

    return list(students_dict.values())

students = parse_students_master()
print(f"\n✅ PARSED TOTAL MASTER STUDENTS: {len(students)}")
print("SAMPLE STUDENT PROFILE:")
print(json.dumps(students[0] if students else {}, ensure_ascii=False, indent=2))
