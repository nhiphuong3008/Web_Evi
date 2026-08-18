import sys
import json
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

s1 = service.spreadsheet
s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)

print("=== DEEP DATA AUDIT ACROSS ALL 3 SPREADSHEETS ===")

# 1. Audit Sheet 1: DATA HS FULL PHÍ
try:
    ws = s1.worksheet('DATA HS FULL PHÍ')
    rows = ws.get_all_values()
    print(f"\n[Sheet 1] 'DATA HS FULL PHÍ' - Rows: {len(rows)}")
    codes_s1 = {}
    for r in rows[1:]:
        if len(r) > 1 and r[1].strip():
            code = r[1].strip().upper()
            name = r[2].strip() if len(r) > 2 else ''
            en = r[3].strip() if len(r) > 3 else ''
            dob = r[4].strip() if len(r) > 4 else ''
            parent = r[5].strip() if len(r) > 5 else ''
            phone = r[6].strip() if len(r) > 6 else ''
            status = r[8].strip() if len(r) > 8 else ''
            codes_s1[code] = {'name': name, 'en': en, 'dob': dob, 'parent': parent, 'phone': phone, 'status': status}
    print(f"  -> Total Unique Codes in DATA HS FULL PHÍ: {len(codes_s1)}")
except Exception as e:
    print(f"Error reading DATA HS FULL PHÍ: {e}")

# 2. Audit Sheet 2: Data DSHS
try:
    ws = s2.worksheet('Data DSHS')
    rows = ws.get_all_values()
    print(f"\n[Sheet 2] 'Data DSHS' - Rows: {len(rows)}")
    codes_s2 = {}
    for r in rows[3:]:
        if len(r) > 0 and r[0].strip():
            code = r[0].strip().upper()
            name = r[1].strip() if len(r) > 1 else ''
            en = r[2].strip() if len(r) > 2 else ''
            cname = r[5].strip() if len(r) > 5 else ''
            codes_s2[code] = {'name': name, 'en': en, 'class': cname}
    print(f"  -> Total Unique Codes in Sheet 2 Data DSHS: {len(codes_s2)}")
except Exception as e:
    print(f"Error reading Sheet 2 Data DSHS: {e}")

# 3. Audit Sheet 3: Data DSHS
try:
    ws = s3.worksheet('Data DSHS')
    rows = ws.get_all_values()
    print(f"\n[Sheet 3] 'Data DSHS' - Rows: {len(rows)}")
    codes_s3 = {}
    for r in rows[3:]:
        if len(r) > 0 and r[0].strip():
            code = r[0].strip().upper()
            name = r[1].strip() if len(r) > 1 else ''
            en = r[2].strip() if len(r) > 2 else ''
            cname = r[5].strip() if len(r) > 5 else ''
            codes_s3[code] = {'name': name, 'en': en, 'class': cname}
    print(f"  -> Total Unique Codes in Sheet 3 Data DSHS: {len(codes_s3)}")
except Exception as e:
    print(f"Error reading Sheet 3 Data DSHS: {e}")

# 4. Compare Codes across Sheet 1 vs Sheet 2/3
all_codes = set(codes_s1.keys()) | set(codes_s2.keys()) | set(codes_s3.keys())
s1_only = set(codes_s1.keys()) - set(codes_s2.keys())
s2_only = set(codes_s2.keys()) - set(codes_s1.keys())
print(f"\n=== CODE CONSOLIDATION SUMMARY ===")
print(f"Total Unique Student Codes across all sheets: {len(all_codes)}")
print(f"Codes in Sheet 1 (Full): {len(codes_s1)}")
print(f"Codes in Sheet 2 (BTVN active): {len(codes_s2)}")
print(f"Codes in Sheet 1 but NOT in Sheet 2 (likely withdrawn/inactive): {len(s1_only)}")
print(f"Codes in Sheet 2 but NOT in Sheet 1 (new students): {len(s2_only)}")

if s2_only:
    print(f"Sample new codes in Sheet 2 not in Sheet 1: {list(s2_only)[:5]}")
    for c in list(s2_only)[:5]:
        print(f"  {c}: {codes_s2[c]}")
