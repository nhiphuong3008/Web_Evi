import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_config
from services.google_sheets import GoogleSheetsService
from database.db_manager import db_session
from database.models import Student

def sync_correct_statuses():
    config = get_config()
    sheets_service = GoogleSheetsService(
        credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE,
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
    )

    if not sheets_service.connect():
        print("Could not connect to Google Sheets!")
        return

    session = db_session()
    all_students_map = {s.code: s for s in session.query(Student).all()}
    print(f"Loaded {len(all_students_map)} students from DB.")

    # 1. Read 'Data DSHS' from BTVN Sheet (1wKcmRH9azv9urXvp-Ld4zWwmZ-iuGA2Vo30WzEkBR1I)
    print("Reading 'Data DSHS' worksheet from BTVN Google Sheet...")
    dshs_rows = []
    try:
        s_btvn = sheets_service.client.open_by_key(config.GOOGLE_SHEETS_BTVN_ID)
        ws_dshs = s_btvn.worksheet('Data DSHS')
        dshs_rows = ws_dshs.get_all_values()
        print(f"Read {len(dshs_rows)} rows from Data DSHS.")
    except Exception as e:
        print("Error reading Data DSHS worksheet:", e)

    baoluu_list_found = []
    danghi_list_found = []
    danghoc_list_found = []

    if len(dshs_rows) > 3:
        for r in dshs_rows[3:]:
            if len(r) < 1 or not r[0].strip():
                continue
            code = r[0].strip().upper()
            name = r[1].strip() if len(r) > 1 else ''
            c_name = r[5].strip() if len(r) > 5 else ''
            
            if code not in all_students_map:
                continue

            st = all_students_map[code]
            c_name_clean = c_name.strip()
            c_name_lower = c_name_clean.lower()

            if 'bảo lưu' in c_name_lower:
                st.status = 'Bảo lưu'
                if st.class_name and 'bảo lưu' not in st.class_name.lower():
                    st.last_class_name = st.class_name
                st.class_name = ''
                baoluu_list_found.append((code, name, c_name_clean))
            elif 'đã nghỉ' in c_name_lower or c_name_clean in ['Nghỉ', 'Đã Nghỉ', 'Đã nghỉ', 'Nghỉ học']:
                st.status = 'Đã nghỉ'
                if st.class_name and 'nghỉ' not in st.class_name.lower():
                    st.last_class_name = st.class_name
                st.class_name = ''
                danghi_list_found.append((code, name, c_name_clean))
            elif c_name_clean and c_name_clean != '—':
                st.status = 'Đang học'
                st.class_name = c_name_clean
                danghoc_list_found.append((code, name, c_name_clean))

    session.commit()
    print(f"\n✅ SUCCESSFULLY SYNCED STUDENT STATUSES FROM GOOGLE SHEETS!")
    print(f"  • Bảo lưu: {len(baoluu_list_found)} học sinh")
    print(f"  • Đã nghỉ: {len(danghi_list_found)} học sinh")
    print(f"  • Đang học: {len(danghoc_list_found)} học sinh")

    print("\nSample Bảo lưu students synced:")
    for b in baoluu_list_found[:15]:
        print(f"  {b[0]} - {b[1]} | Raw Class Value: '{b[2]}'")

    # Summary from DB
    statuses = {}
    for s in session.query(Student).all():
        st = s.status or 'Unknown'
        statuses[st] = statuses.get(st, 0) + 1

    print("\n--- FINAL STATUS BREAKDOWN IN DB ---")
    for st_name, count in statuses.items():
        print(f"  • {st_name}: {count} học sinh")

if __name__ == '__main__':
    sync_correct_statuses()
