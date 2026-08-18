import sys
import json
import os

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

print("==========================================================================")
print("🔍 AUDIT TOÀN BỘ CÁC TAB TRÊN 3 GOOGLE SHEETS DỰ ÁN EVI VIỆT HƯNG")
print("==========================================================================")

def audit_spreadsheet(sp_obj, name):
    print(f"\n📁 SPREADSHEET: '{sp_obj.title}' ({name})")
    for ws in sp_obj.worksheets():
        try:
            rows = ws.get_all_values()
            non_empty_rows = [r for r in rows if any(c.strip() for c in r)]
            print(f"  • Tab: '{ws.title:<30}' | Tổng dòng: {len(rows):<5} | Dòng có data: {len(non_empty_rows):<5}")
            if non_empty_rows:
                h = [c.strip().replace('\n', ' ') for c in non_empty_rows[0] if c.strip()]
                print(f"    Headers ({len(h)} cols): {h[:8]}")
        except Exception as e:
            print(f"  • Tab: '{ws.title}' - Error: {e}")

audit_spreadsheet(s1, "Sheet 1 - Tổng 2025 & Dashboard")
audit_spreadsheet(s2, "Sheet 2 - Quản lý BTVN & Nhận xét")
audit_spreadsheet(s3, "Sheet 3 - Quản lý Điểm số")
