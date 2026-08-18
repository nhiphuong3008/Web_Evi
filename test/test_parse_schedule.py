import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

def parse_schedule_rows(rows):
    """
    Parse tab SCHEDULE thành danh sách các record thời khóa biểu chuẩn.
    """
    schedules = []

    # Block definitions for Main Schedule (Rows 1 - 17)
    # MON / THU: MT5 & MT6
    # TUE / FRI: TF5 & TF6
    # WED / SAT: WS5 & WS6

    # Block 1 (Cols 2-9): Left side (MON, TUE, WED) -> Block 5 / 5.30-7.00 PM
    # Block 2 (Cols 10-17): Left side (MON, TUE, WED) -> Block 6 / 7.15-8.45 PM
    # Block 3 (Cols 19-26): Right side (THU, FRI, SAT) -> Block 5 / 5.30-7.00 PM
    # Block 4 (Cols 27-34): Right side (THU, FRI, SAT) -> Block 6 / 7.15-8.45 PM

    day_mappings = [
        # (Start_row, End_row, day1_name, day2_name, shift1_code, shift2_code)
        (3, 6, 'Thứ 2 (MON)', 'Thứ 5 (THU)', 'MT5', 'MT6'),
        (8, 11, 'Thứ 3 (TUE)', 'Thứ 6 (FRI)', 'TF5', 'TF6'),
        (13, 16, 'Thứ 4 (WED)', 'Thứ 7 (SAT)', 'WS5', 'WS6'),
    ]

    for start_r, end_r, day_left, day_right, shift5, shift6 in day_mappings:
        for r_idx in range(start_r, end_r + 1):
            if r_idx >= len(rows): break
            row = rows[r_idx]

            # 1. Left Day - Block 5 (17h30-19h00)
            if len(row) > 2 and row[2].strip():
                cname = row[2].strip()
                if cname.lower() not in ('classes', ''):
                    schedules.append({
                        'section': 'Chính thức',
                        'day': day_left,
                        'shift_code': shift5,
                        'shift_name': 'Block 5 (17:30 - 19:00)',
                        'class_name': cname,
                        'materials': row[3].strip() if len(row) > 3 else '',
                        'room': row[4].strip() if len(row) > 4 else '',
                        'teacher': row[5].strip() if len(row) > 5 else '',
                        'students_count': int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 0,
                        'cm_staff': row[7].strip() if len(row) > 7 else '',
                        'ta_staff': row[8].strip() if len(row) > 8 else '',
                        'tutoring_info': row[9].strip() if len(row) > 9 else ''
                    })

            # 2. Left Day - Block 6 (19h15-20h45)
            if len(row) > 10 and row[10].strip():
                cname = row[10].strip()
                if cname.lower() not in ('classes', ''):
                    schedules.append({
                        'section': 'Chính thức',
                        'day': day_left,
                        'shift_code': shift6,
                        'shift_name': 'Block 6 (19:15 - 20:45)',
                        'class_name': cname,
                        'materials': row[11].strip() if len(row) > 11 else '',
                        'room': row[12].strip() if len(row) > 12 else '',
                        'teacher': row[13].strip() if len(row) > 13 else '',
                        'students_count': int(row[14]) if len(row) > 14 and row[14].strip().isdigit() else 0,
                        'cm_staff': row[15].strip() if len(row) > 15 else '',
                        'ta_staff': row[16].strip() if len(row) > 16 else '',
                        'tutoring_info': row[17].strip() if len(row) > 17 else ''
                    })

            # 3. Right Day - Block 5 (17h30-19h00)
            if len(row) > 19 and row[19].strip():
                cname = row[19].strip()
                if cname.lower() not in ('classes', ''):
                    schedules.append({
                        'section': 'Chính thức',
                        'day': day_right,
                        'shift_code': shift5,
                        'shift_name': 'Block 5 (17:30 - 19:00)',
                        'class_name': cname,
                        'materials': row[20].strip() if len(row) > 20 else '',
                        'room': row[21].strip() if len(row) > 21 else '',
                        'teacher': row[22].strip() if len(row) > 22 else '',
                        'students_count': int(row[23]) if len(row) > 23 and row[23].strip().isdigit() else 0,
                        'cm_staff': row[24].strip() if len(row) > 24 else '',
                        'ta_staff': row[25].strip() if len(row) > 25 else '',
                        'tutoring_info': row[26].strip() if len(row) > 26 else ''
                    })

            # 4. Right Day - Block 6 (19h15-20h45)
            if len(row) > 27 and row[27].strip():
                cname = row[27].strip()
                if cname.lower() not in ('classes', ''):
                    schedules.append({
                        'section': 'Chính thức',
                        'day': day_right,
                        'shift_code': shift6,
                        'shift_name': 'Block 6 (19:15 - 20:45)',
                        'class_name': cname,
                        'materials': row[28].strip() if len(row) > 28 else '',
                        'room': row[29].strip() if len(row) > 29 else '',
                        'teacher': row[30].strip() if len(row) > 30 else '',
                        'students_count': int(row[31]) if len(row) > 31 and row[31].strip().isdigit() else 0,
                        'cm_staff': row[32].strip() if len(row) > 32 else '',
                        'ta_staff': row[33].strip() if len(row) > 33 else '',
                        'tutoring_info': row[34].strip() if len(row) > 34 else ''
                    })

    # Supplementary Schedule (Lịch Dạy Bổ Trợ, Rows 32-45)
    supp_mappings = [
        (32, 35, 'Thứ 2 (MON)'),
        (37, 40, 'Thứ 3 (TUE)'),
        (42, 44, 'Thứ 4 (WED)')
    ]

    for start_r, end_r, day_name in supp_mappings:
        for r_idx in range(start_r, end_r + 1):
            if r_idx >= len(rows): break
            row = rows[r_idx]

            # Block 5 (Cols 2-8)
            if len(row) > 2 and row[2].strip() and row[2].strip().lower() != 'classes':
                schedules.append({
                    'section': 'Bổ trợ',
                    'day': day_name,
                    'shift_code': 'MT5' if 'MON' in day_name else ('TF5' if 'TUE' in day_name else 'WS5'),
                    'shift_name': 'Block 5 (17:30 - 19:00)',
                    'class_name': row[2].strip(),
                    'materials': '',
                    'room': row[4].strip() if len(row) > 4 else '',
                    'teacher': row[5].strip() if len(row) > 5 else '',
                    'students_count': int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 0,
                    'cm_staff': row[7].strip() if len(row) > 7 else '',
                    'ta_staff': row[8].strip() if len(row) > 8 else '',
                    'tutoring_info': ''
                })

            # Block 6 (Cols 9-14)
            if len(row) > 9 and row[9].strip() and row[9].strip().lower() != 'classes':
                schedules.append({
                    'section': 'Bổ trợ',
                    'day': day_name,
                    'shift_code': 'MT6' if 'MON' in day_name else ('TF6' if 'TUE' in day_name else 'WS6'),
                    'shift_name': 'Block 6 (19:15 - 20:45)',
                    'class_name': row[9].strip(),
                    'materials': '',
                    'room': row[10].strip() if len(row) > 10 else '',
                    'teacher': row[12].strip() if len(row) > 12 else '',
                    'students_count': int(row[13]) if len(row) > 13 and row[13].strip().isdigit() else 0,
                    'cm_staff': row[14].strip() if len(row) > 14 else '',
                    'ta_staff': '',
                    'tutoring_info': ''
                })

    return schedules

def test():
    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not svc.connect(): return

    sp1 = svc.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    ws = sp1.worksheet('SCHEDULE')
    rows = ws.get_all_values()

    parsed = parse_schedule_rows(rows)
    print(f"Parsed {len(parsed)} official schedule records!\n")

    print("Sample parsed records:")
    for s in parsed[:10]:
        print(f"  - [{s['day']} - {s['shift_code']}] Class: '{s['class_name']}' | Room: '{s['room']}' | Teacher: '{s['teacher']}' | CM: '{s['cm_staff']}' | Students: {s['students_count']}")

    print("\nRecords by CM staff:")
    cm_map = {}
    for s in parsed:
        cm = s['cm_staff'] or 'Khác'
        cm_map[cm] = cm_map.get(cm, 0) + 1
    for cm, cnt in cm_map.items():
        print(f"  • CM '{cm}': {cnt} lớp")

if __name__ == '__main__':
    test()
