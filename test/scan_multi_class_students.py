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

def scan_multi_classes():
    config = get_config()
    sheets_service = GoogleSheetsService(
        credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE,
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
    )

    if not sheets_service.connect():
        print("Could not connect to Google Sheets!")
        return

    # Student code/name -> set of classes
    student_classes_map = {}

    def add_to_map(code, name, c_name):
        if not c_name or c_name.strip() in ('—', '', 'Bảo lưu', 'Đã nghỉ', 'Nghỉ'):
            return
        c_clean = c_name.strip()
        
        key = None
        if code and code.strip():
            key = code.strip().upper()

        if key:
            if key not in student_classes_map:
                student_classes_map[key] = set()
            for c in c_clean.split(','):
                if c.strip() and c.strip() not in ('Bảo lưu', 'Đã nghỉ'):
                    student_classes_map[key].add(c.strip())

    # 1. Scan Dashboard Sheet (1TfI4zZyOXOmm8i3DEbSfh0BsR4KXUVGt2RFRi9nn9M0)
    sp_dash = sheets_service.client.open_by_key(config.GOOGLE_SHEETS_SPREADSHEET_ID)
    
    # 1a. Tab 'Điểm danh lớp ngữ pháp.'
    try:
        ws_np = sp_dash.worksheet('Điểm danh lớp ngữ pháp.')
        rows_np = ws_np.get_all_values()
        print(f"Read {len(rows_np)} rows from 'Điểm danh lớp ngữ pháp.'")
        if len(rows_np) > 1:
            for r in rows_np[1:]:
                if len(r) > 1 and r[1].strip():
                    code = r[1].strip().upper() if len(r) > 1 else ''
                    c_np = r[4].strip() if len(r) > 4 else 'Lớp Ngữ Pháp'
                    if not c_np: c_np = 'Lớp Ngữ Pháp'
                    add_to_map(code, '', c_np)
    except Exception as e:
        print("Error reading 'Điểm danh lớp ngữ pháp.':", e)

    # 1b. Tab 'DATA LỚP HỌC'
    try:
        ws_lh = sp_dash.worksheet('DATA LỚP HỌC')
        rows_lh = ws_lh.get_all_values()
        print(f"Read {len(rows_lh)} rows from 'DATA LỚP HỌC'")
        if len(rows_lh) > 1:
            for r in rows_lh[1:]:
                if len(r) > 1 and r[1].strip():
                    code = r[1].strip().upper()
                    c_lh = r[5].strip() if len(r) > 5 else ''
                    add_to_map(code, '', c_lh)
    except Exception as e:
        print("Error reading 'DATA LỚP HỌC':", e)

    # 2. Scan BTVN Sheet Data DSHS
    try:
        sp_btvn = sheets_service.client.open_by_key(config.GOOGLE_SHEETS_BTVN_ID)
        ws_dshs = sp_btvn.worksheet('Data DSHS')
        rows_dshs = ws_dshs.get_all_values()
        print(f"Read {len(rows_dshs)} rows from BTVN 'Data DSHS'")
        if len(rows_dshs) > 3:
            for r in rows_dshs[3:]:
                if len(r) > 0 and r[0].strip():
                    code = r[0].strip().upper()
                    c_dshs = r[5].strip() if len(r) > 5 else ''
                    add_to_map(code, '', c_dshs)
    except Exception as e:
        print("Error reading BTVN 'Data DSHS':", e)

    # 3. Scan Grades Sheet class tabs
    try:
        sp_grades = sheets_service.client.open_by_key(config.GOOGLE_SHEETS_GRADES_ID)
        for ws in sp_grades.worksheets():
            if ws.title != 'Data DSHS':
                c_title = ws.title.strip()
                rows_g = ws.get_all_values()
                if len(rows_g) > 2:
                    for r in rows_g[2:]:
                        if len(r) > 0 and r[0].strip().startswith('EVI'):
                            code = r[0].strip().upper()
                            add_to_map(code, '', c_title)
    except Exception as e:
        print("Error reading Grades Sheet tabs:", e)

    # Filter students with 2+ classes
    multi_class_students = {k: v for k, v in student_classes_map.items() if len(v) >= 2}
    print(f"\nFound {len(multi_class_students)} students enrolled in 2+ classes!")
    for code, classes in list(multi_class_students.items())[:20]:
        print(f"  • {code}: {', '.join(sorted(list(classes)))}")

    # Update DB
    session = db_session()
    updated_count = 0
    for code, classes in student_classes_map.items():
        st = session.query(Student).filter(Student.code == code).first()
        if st and classes:
            sorted_classes = sorted(list(classes))
            new_c_str = ', '.join(sorted_classes)
            if st.class_name != new_c_str:
                st.class_name = new_c_str
                if st.status != 'Bảo lưu' and st.status != 'Đã nghỉ':
                    st.status = 'Đang học'
                updated_count += 1

    session.commit()
    print(f"\n✅ SUCCESSFULLY AUTO-ASSIGNED MULTI-CLASS TAGS FOR {updated_count} STUDENTS IN DB!")

if __name__ == '__main__':
    scan_multi_classes()
