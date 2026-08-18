import sys
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
from services.data_parser import parse_float_vn
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)

def parse_all_units_from_worksheet(rows, tab_title):
    if len(rows) < 6:
        return []

    class_name = tab_title
    course_name = "KID'S BOX"

    # Header inspection in top rows
    for r in rows[:4]:
        for cell in r:
            cell_str = str(cell)
            if 'LỚP:' in cell_str:
                parts = cell_str.split('LỚP:')
                if len(parts) > 1:
                    c_found = parts[1].split('TÊN')[0].strip()
                    if c_found:
                        class_name = c_found
            if 'CHƯƠNG TRÌNH' in cell_str:
                parts = cell_str.split('CHƯƠNG TRÌNH')
                if len(parts) > 1 and parts[1].strip():
                    course_name = parts[1].strip()

    # Row 4 contains test/unit titles (e.g. UNIT 2, UNIT 4, MID - TERM TEST...)
    # Row 5 contains skill headers (Nghe, Đọc - Viết, Nói, Nhận xét...)
    unit_row = rows[3] if len(rows) > 3 else []
    skill_row = rows[4] if len(rows) > 4 else []

    # Detect test blocks: map column index -> {test_name, listening_col, reading_col, speaking_col, comment_col}
    test_blocks = []
    current_test = ""
    current_block = None

    for col_idx in range(3, max(len(unit_row), len(skill_row))):
        u_header = unit_row[col_idx].strip() if col_idx < len(unit_row) else ''
        s_header = skill_row[col_idx].strip() if col_idx < len(skill_row) else ''

        if u_header:
            current_test = u_header
            current_block = {
                'test_name': u_header,
                'start_col': col_idx,
                'listening_col': -1, 'listening_max': 10,
                'reading_col': -1, 'reading_max': 20,
                'speaking_col': -1, 'speaking_max': 10,
                'comment_col': -1
            }
            test_blocks.append(current_block)

        if not current_block and test_blocks:
            current_block = test_blocks[-1]

        if current_block:
            s_upper = s_header.upper()
            if 'NGHE' in s_upper:
                current_block['listening_col'] = col_idx
                # Extract max score from header e.g. Nghe (.../15)
                if '/15' in s_header: current_block['listening_max'] = 15
                elif '/20' in s_header: current_block['listening_max'] = 20
                elif '/25' in s_header: current_block['listening_max'] = 25
                elif '/10' in s_header: current_block['listening_max'] = 10
            elif 'ĐỌC' in s_upper or 'VIẾT' in s_upper:
                current_block['reading_col'] = col_idx
                if '/12' in s_header: current_block['reading_max'] = 12
                elif '/20' in s_header: current_block['reading_max'] = 20
                elif '/35' in s_header: current_block['reading_max'] = 35
                elif '/22' in s_header: current_block['reading_max'] = 22
            elif 'NÓI' in s_upper:
                current_block['speaking_col'] = col_idx
                if '/26' in s_header: current_block['speaking_max'] = 26
            elif 'NHẬN XÉT' in s_upper:
                current_block['comment_col'] = col_idx

    print(f"\nTab '{tab_title}' (Class: {class_name}) - Detected Test Blocks ({len(test_blocks)}):")
    for tb in test_blocks:
        print(f"  Test: '{tb['test_name']}' | Listen col:{tb['listening_col']} | Read col:{tb['reading_col']} | Speak col:{tb['speaking_col']} | Comment col:{tb['comment_col']}")

    # Parse students for each test block
    all_student_grades = []
    for r_idx in range(5, len(rows)):
        r = rows[r_idx]
        if len(r) < 3 or not any(r):
            continue

        stt = r[0].strip() if len(r) > 0 else ''
        name = r[1].strip() if len(r) > 1 else ''
        en_name = r[2].strip() if len(r) > 2 else ''

        if not name and not en_name:
            continue
        if name.upper() in ['STT', 'TÊN', 'CHƯƠNG TRÌNH', 'LỚP']:
            continue

        displayName = name or en_name

        for tb in test_blocks:
            listening = parse_float_vn(r[tb['listening_col']]) if tb['listening_col'] != -1 and tb['listening_col'] < len(r) and r[tb['listening_col']].strip() else None
            reading_writing = parse_float_vn(r[tb['reading_col']]) if tb['reading_col'] != -1 and tb['reading_col'] < len(r) and r[tb['reading_col']].strip() else None
            speaking = parse_float_vn(r[tb['speaking_col']]) if tb['speaking_col'] != -1 and tb['speaking_col'] < len(r) and r[tb['speaking_col']].strip() else None
            comment = r[tb['comment_col']].strip() if tb['comment_col'] != -1 and tb['comment_col'] < len(r) else ''

            if listening is None and reading_writing is None and speaking is None and not comment:
                continue

            total_score = 0
            max_score = 0
            if listening is not None:
                total_score += listening
                max_score += tb['listening_max']
            if reading_writing is not None:
                total_score += reading_writing
                max_score += tb['reading_max']
            if speaking is not None:
                total_score += speaking
                max_score += tb['speaking_max']

            all_student_grades.append({
                'class_name': class_name,
                'course': course_name,
                'test_name': tb['test_name'],
                'stt': stt,
                'name': displayName,
                'english_name': en_name,
                'listening': listening,
                'listening_max': tb['listening_max'],
                'reading_writing': reading_writing,
                'reading_writing_max': tb['reading_max'],
                'speaking': speaking,
                'speaking_max': tb['speaking_max'],
                'comment': comment,
                'total_score': total_score,
                'max_score': max_score or 22,
            })

    return all_student_grades

total_parsed = 0
for w in s3.worksheets():
    if w.title == 'Data DSHS':
        continue
    g_parsed = parse_all_units_from_worksheet(w.get_all_values(), w.title)
    total_parsed += len(g_parsed)

print(f"\n✅ TOTAL UNIT GRADE RECORDS PARSED ACROSS ALL TABS: {total_parsed}")
