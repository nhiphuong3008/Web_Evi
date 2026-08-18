import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from config import Config
from services.google_sheets import GoogleSheetsService
from database.db_manager import db_session
from database.models import ParentInteractionLog, Student

def parse_header_date(header_str):
    import re
    import datetime
    if not header_str:
        return datetime.datetime.now(), ''
    h = str(header_str).strip()
    if '2023-2025' in h or '2023' in h:
        return datetime.datetime(2025, 1, 1, 9, 0, 0), '2023-2025'
    m = re.search(r'tháng\s*(\d{1,2})[/\s]+(\d{4})', h, re.IGNORECASE)
    if not m:
        m = re.search(r'(\d{1,2})[/\s]+(\d{4})', h)
    if m:
        month = int(m.group(1))
        year = int(m.group(2))
        return datetime.datetime(year, month, 1, 9, 0, 0), str(month)
    m2 = re.search(r'tháng\s*(\d{1,2})', h, re.IGNORECASE)
    if m2:
        month = int(m2.group(1))
        return datetime.datetime(2026, month, 1, 9, 0, 0), str(month)
    return datetime.datetime.now(), ''


def reimport():
    print("==================================================================")
    print("🔄 THỰC HIỆN NẠP LẠI DỮ LIỆU CHUẨN TỪ SHEET 'NHẬT KÝ CHĂM SÓC VÀ TƯƠNG TÁC'")
    print("==================================================================")

    session = db_session()
    
    # Pre-map student code & CM staff from Student table
    students = session.query(Student).all()
    code_map = {}
    name_map = {}
    cm_map = {}
    for st in students:
        if st.code:
            code_map[st.code.strip().upper()] = st
        if st.full_name:
            name_map[st.full_name.strip().lower()] = st
        if st.code:
            cm_map[st.code.strip().upper()] = st.cm_staff or 'AnhNV'
        if st.full_name:
            cm_map[st.full_name.strip().lower()] = st.cm_staff or 'AnhNV'

    # Retry loop for Google Sheets API 429
    gs = GoogleSheetsService(Config.GOOGLE_SHEETS_CREDENTIALS_FILE, Config.GOOGLE_SHEETS_SPREADSHEET_ID)
    sp = None
    for attempt in range(5):
        try:
            if gs.connect():
                sp = gs.spreadsheet
                break
        except Exception as e:
            print(f"Waiting for API quota... attempt {attempt+1}/5 ({e})")
            time.sleep(5)

    if not sp:
        print("❌ Cannot connect to Google Sheets API right now.")
        session.close()
        return

    # Find worksheet
    ws = None
    for w in sp.worksheets():
        w_title = w.title.lower()
        if 'chăm sóc' in w_title or 'tương tác' in w_title:
            ws = w
            print(f"✅ Found Worksheet: '{w.title}'")
            break

    if not ws:
        print("❌ Worksheet 'Nhật ký chăm sóc và tương tác' not found!")
        session.close()
        return

    rows = ws.get_all_values()
    print(f"Total rows in sheet: {len(rows)}")

    if not rows:
        session.close()
        return

    header = rows[0]
    print(f"Header columns: {[f'{i}:{header[i]}' for i in range(min(20, len(header)))]}")

    # Clear current ParentInteractionLog table before re-importing clean sheet data
    session.query(ParentInteractionLog).delete()
    session.commit()

    added_count = 0

    for idx, r in enumerate(rows[1:]):
        if len(r) < 3:
            continue
        
        raw_code = r[1].strip().upper() if len(r) > 1 else ''
        raw_name = r[2].strip() if len(r) > 2 else ''
        raw_en = r[3].strip() if len(r) > 3 else ''
        raw_class = r[4].strip() if len(r) > 4 else ''
        
        if not raw_name or raw_name.lower() in ('tên học sinh', 'học sinh', 'stt'):
            continue

        # Ignore junk header rows
        if any(k in raw_name.lower() for k in ['handbook', 'activity book', 'chương trình hè', 'syllabus', 'no']):
            continue

        # Match student code
        matched_st = code_map.get(raw_code) or name_map.get(raw_name.lower())
        matched_code = matched_st.code if matched_st else (raw_code if raw_code.startswith('EVI') else None)
        final_name = matched_st.full_name if matched_st else raw_name
        final_en = matched_st.english_name if matched_st else raw_en
        final_class = matched_st.class_name if matched_st else raw_class
        staff = (matched_st.cm_staff if matched_st else None) or 'AnhNV'

        # Check all note columns (K onwards, index 10 to len(r))
        for col_idx in range(10, len(r)):
            note_val = r[col_idx].strip()
            if note_val:
                time_header = header[col_idx].strip() if col_idx < len(header) else ''
                combined_note = f"[{time_header}] {note_val}" if time_header else note_val
                dt_val, month_val = parse_header_date(time_header)
                
                log_obj = ParentInteractionLog(
                    student_code=matched_code,
                    student_name=final_name,
                    english_name=final_en,
                    class_name=final_class,
                    staff_name=staff,
                    note=combined_note,
                    interaction_detail=note_val,
                    created_at=dt_val,
                    month=month_val
                )
                session.add(log_obj)
                added_count += 1

    session.commit()
    session.close()

    print("==================================================================")
    print(f"🎉 ĐÃ NẠP THÀNH CÔNG {added_count} BẢN GHI NHẬT KÝ TƯƠNG TÁC TỪ SHEET CHUẨN KÈM NGÀY CHUẨN!")
    print("==================================================================")

if __name__ == '__main__':
    reimport()
