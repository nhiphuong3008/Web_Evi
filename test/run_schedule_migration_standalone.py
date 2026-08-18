import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService
from database.db_manager import db_session, init_db
from database.models import ClassSchedule

def migrate_schedule():
    init_db()
    session = db_session()

    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)

    rows = None
    for attempt in range(5):
        try:
            if svc.connect():
                sp1 = svc.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
                ws = sp1.worksheet('SCHEDULE')
                rows = ws.get_all_values()
                if rows: break
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}. Retrying in 3s...")
            time.sleep(3)

    if not rows:
        print("Failed to read SCHEDULE worksheet after retries.")
        return False

    session.query(ClassSchedule).delete()
    sched_count = 0

    day_mappings = [
        (3, 6, 'Thứ 2 (MON)', 'Thứ 5 (THU)', 'MT5', 'MT6'),
        (8, 11, 'Thứ 3 (TUE)', 'Thứ 6 (FRI)', 'TF5', 'TF6'),
        (13, 16, 'Thứ 4 (WED)', 'Thứ 7 (SAT)', 'WS5', 'WS6'),
    ]

    for start_r, end_r, day_left, day_right, shift5, shift6 in day_mappings:
        for r_idx in range(start_r, end_r + 1):
            if r_idx >= len(rows): break
            row = rows[r_idx]

            # 1. Left Day - Block 5
            if len(row) > 2 and row[2].strip() and row[2].strip().lower() != 'classes':
                s_obj = ClassSchedule(
                    section='Chính thức', day=day_left, shift_code=shift5, shift_name='Block 5 (17:30 - 19:00)',
                    class_name=row[2].strip(), materials=row[3].strip() if len(row) > 3 else '',
                    room=row[4].strip() if len(row) > 4 else '', teacher=row[5].strip() if len(row) > 5 else '',
                    students_count=int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 0,
                    cm_staff=row[7].strip() if len(row) > 7 else '', ta_staff=row[8].strip() if len(row) > 8 else '',
                    tutoring_info=row[9].strip() if len(row) > 9 else ''
                )
                session.add(s_obj); sched_count += 1

            # 2. Left Day - Block 6
            if len(row) > 10 and row[10].strip() and row[10].strip().lower() != 'classes':
                s_obj = ClassSchedule(
                    section='Chính thức', day=day_left, shift_code=shift6, shift_name='Block 6 (19:15 - 20:45)',
                    class_name=row[10].strip(), materials=row[11].strip() if len(row) > 11 else '',
                    room=row[12].strip() if len(row) > 12 else '', teacher=row[13].strip() if len(row) > 13 else '',
                    students_count=int(row[14]) if len(row) > 14 and row[14].strip().isdigit() else 0,
                    cm_staff=row[15].strip() if len(row) > 15 else '', ta_staff=row[16].strip() if len(row) > 16 else '',
                    tutoring_info=row[17].strip() if len(row) > 17 else ''
                )
                session.add(s_obj); sched_count += 1

            # 3. Right Day - Block 5
            if len(row) > 19 and row[19].strip() and row[19].strip().lower() != 'classes':
                s_obj = ClassSchedule(
                    section='Chính thức', day=day_right, shift_code=shift5, shift_name='Block 5 (17:30 - 19:00)',
                    class_name=row[19].strip(), materials=row[20].strip() if len(row) > 20 else '',
                    room=row[21].strip() if len(row) > 21 else '', teacher=row[22].strip() if len(row) > 22 else '',
                    students_count=int(row[23]) if len(row) > 23 and row[23].strip().isdigit() else 0,
                    cm_staff=row[24].strip() if len(row) > 24 else '', ta_staff=row[25].strip() if len(row) > 25 else '',
                    tutoring_info=row[26].strip() if len(row) > 26 else ''
                )
                session.add(s_obj); sched_count += 1

            # 4. Right Day - Block 6
            if len(row) > 27 and row[27].strip() and row[27].strip().lower() != 'classes':
                s_obj = ClassSchedule(
                    section='Chính thức', day=day_right, shift_code=shift6, shift_name='Block 6 (19:15 - 20:45)',
                    class_name=row[27].strip(), materials=row[28].strip() if len(row) > 28 else '',
                    room=row[29].strip() if len(row) > 29 else '', teacher=row[30].strip() if len(row) > 30 else '',
                    students_count=int(row[31]) if len(row) > 31 and row[31].strip().isdigit() else 0,
                    cm_staff=row[32].strip() if len(row) > 32 else '', ta_staff=row[33].strip() if len(row) > 33 else '',
                    tutoring_info=row[34].strip() if len(row) > 34 else ''
                )
                session.add(s_obj); sched_count += 1

    # Supplementary Schedule (Rows 32-45)
    supp_mappings = [(32, 35, 'Thứ 2 (MON)'), (37, 40, 'Thứ 3 (TUE)'), (42, 44, 'Thứ 4 (WED)')]
    for start_r, end_r, day_name in supp_mappings:
        for r_idx in range(start_r, end_r + 1):
            if r_idx >= len(rows): break
            row = rows[r_idx]
            if len(row) > 2 and row[2].strip() and row[2].strip().lower() != 'classes':
                s_obj = ClassSchedule(
                    section='Bổ trợ', day=day_name,
                    shift_code='MT5' if 'MON' in day_name else ('TF5' if 'TUE' in day_name else 'WS5'),
                    shift_name='Block 5 (17:30 - 19:00)', class_name=row[2].strip(),
                    room=row[4].strip() if len(row) > 4 else '', teacher=row[5].strip() if len(row) > 5 else '',
                    students_count=int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 0,
                    cm_staff=row[7].strip() if len(row) > 7 else '', ta_staff=row[8].strip() if len(row) > 8 else ''
                )
                session.add(s_obj); sched_count += 1

            if len(row) > 9 and row[9].strip() and row[9].strip().lower() != 'classes':
                s_obj = ClassSchedule(
                    section='Bổ trợ', day=day_name,
                    shift_code='MT6' if 'MON' in day_name else ('TF6' if 'TUE' in day_name else 'WS6'),
                    shift_name='Block 6 (19:15 - 20:45)', class_name=row[9].strip(),
                    room=row[10].strip() if len(row) > 10 else '', teacher=row[12].strip() if len(row) > 12 else '',
                    students_count=int(row[13]) if len(row) > 13 and row[13].strip().isdigit() else 0,
                    cm_staff=row[14].strip() if len(row) > 14 else ''
                )
                session.add(s_obj); sched_count += 1

    session.commit()
    print(f"✅ Successfully saved {sched_count} ClassSchedule records in SQLite DB!")
    return True

if __name__ == '__main__':
    migrate_schedule()
