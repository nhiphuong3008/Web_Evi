"""
Rà soát cấu trúc dữ liệu toàn bộ 4 Google Sheets:
  1. Sheet Tổng (1TfI4...)  - Dashboard chính
  2. Sheet BTVN (1wKcm...)  - Bài tập về nhà
  3. Sheet Grades (1UzeC...) - Điểm số (cũ)
  4. Sheet New Grades (1BkNj...) - Điểm số (mới)
"""
import sys, os, time, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import config
from services.google_sheets import GoogleSheetsService

def inspect_all_sheets():
    cfg = config.get_config()
    svc = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not svc.connect():
        print("FAILED to connect to Google Sheets API")
        return

    sheets_info = [
        ("SHEET 1 - Tổng EVI Academy", cfg.GOOGLE_SHEETS_SPREADSHEET_ID),
        ("SHEET 2 - BTVN", cfg.GOOGLE_SHEETS_BTVN_ID),
        ("SHEET 3 - Grades (Cũ)", cfg.GOOGLE_SHEETS_GRADES_ID),
        ("SHEET 4 - Grades (Mới)", cfg.GOOGLE_SHEETS_NEW_GRADES_ID),
    ]

    for sheet_name, sheet_id in sheets_info:
        print(f"\n{'='*80}")
        print(f"📄 {sheet_name} (ID: {sheet_id})")
        print(f"{'='*80}")
        try:
            sp = svc.client.open_by_key(sheet_id)
            worksheets = sp.worksheets()
            print(f"  Tổng số Tab: {len(worksheets)}")
            for idx, ws in enumerate(worksheets):
                print(f"  [{idx}] Tab: '{ws.title}' | Rows: {ws.row_count} | Cols: {ws.col_count}")
                # Đọc 3 dòng đầu (header) để hiểu cấu trúc
                try:
                    sample = ws.get_all_values()
                    actual_rows = len(sample)
                    actual_cols = max(len(r) for r in sample) if sample else 0
                    print(f"       Actual data: {actual_rows} rows x {actual_cols} cols")
                    for r_idx in range(min(3, actual_rows)):
                        row_preview = sample[r_idx][:15]  # First 15 cols
                        print(f"       Row {r_idx}: {row_preview}")
                except Exception as e_ws:
                    print(f"       Error reading: {e_ws}")
                time.sleep(1.5)  # Rate limit throttle
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(2)

if __name__ == '__main__':
    inspect_all_sheets()
