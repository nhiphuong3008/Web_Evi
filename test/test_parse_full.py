import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
if not service.connect():
    print("Failed to connect!")
    sys.exit(1)

print("=== PARSING ALL GRADES WORKSHEETS ===")
s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)
all_grades = []

for w in s3.worksheets():
    if w.title == 'Data DSHS':
        continue
    
    rows = w.get_all_values()
    if len(rows) < 5:
        continue
        
    class_name = w.title
    # Check if header contains LỚP:
    for r in rows[:4]:
        for cell in r:
            if 'LỚP:' in cell:
                parts = cell.split('LỚP:')
                if len(parts) > 1:
                    parsed_c = parts[1].split('TÊN')[0].strip()
                    if parsed_c:
                        class_name = parsed_c

    # Find table header (STT, TÊN, English name...)
    header_idx = -1
    for idx, r in enumerate(rows):
        row_str = ' '.join(r).upper()
        if 'STT' in row_str or 'ENGLISH NAME' in row_str or 'TÊN' in row_str:
            header_idx = idx
            break
            
    if header_idx != -1:
        headers = rows[header_idx]
        for r in rows[header_idx+1:]:
            if len(r) < 3 or not any(r):
                continue
            stt = r[0].strip()
            name = r[1].strip() if len(r) > 1 else ''
            en_name = r[2].strip() if len(r) > 2 else ''
            
            if not name and not en_name:
                continue
            if name.upper() in ['STT', 'TÊN', 'CHƯƠNG TRÌNH']:
                continue
                
            listening = r[3].strip() if len(r) > 3 else ''
            reading_writing = r[4].strip() if len(r) > 4 else ''
            speaking = r[5].strip() if len(r) > 5 else ''
            comment = r[6].strip() if len(r) > 6 else ''
            
            all_grades.append({
                'class_name': class_name,
                'tab_name': w.title,
                'stt': stt,
                'name': name,
                'english_name': en_name,
                'listening': listening,
                'reading_writing': reading_writing,
                'speaking': speaking,
                'comment': comment
            })

print(f"Total Grade Records Parsed across all tabs: {len(all_grades)}")
for g in all_grades[:5]:
    print(" ", g)

print("\n=== PARSING BTVN 'Nhập KQ BVN' WORKSHEET ===")
s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
w_btvn = s2.worksheet('Nhập KQ BVN')
btvn_rows = w_btvn.get_all_values()

all_btvn = []
for r in btvn_rows[3:]: # Skip headers
    if len(r) < 6 or not any(r):
        continue
    date_val = r[0].strip()
    code = r[1].strip()
    name = r[2].strip()
    en_name = r[3].strip()
    phone = r[4].strip()
    class_name = r[5].strip()
    teacher = r[6].strip() if len(r) > 6 else ''
    schedule = r[7].strip() if len(r) > 7 else ''
    score = r[8].strip() if len(r) > 8 else ''
    total_q = r[9].strip() if len(r) > 9 else ''
    
    if code or name or en_name:
        status = 'Đã nộp'
        if not score or score == '0,0' or score == '0':
            status = 'Chưa nộp BTVN'
            
        all_btvn.append({
            'date': date_val,
            'code': code,
            'name': name,
            'english_name': en_name,
            'phone': phone,
            'class_name': class_name,
            'teacher': teacher,
            'schedule': schedule,
            'score': score,
            'total_q': total_q,
            'status': status
        })

print(f"Total BTVN Records Parsed: {len(all_btvn)}")
for b in all_btvn[:5]:
    print(" ", b)
