import sys
import json
import logging

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

print("=== SHEET 1: Dashboard ===")
s1 = service.spreadsheet
for w in s1.worksheets():
    print(f"  [ID: {w.id}] Title: '{w.title}' ({w.row_count} rows, {w.col_count} cols)")

print("\n=== SHEET 2: BTVN ===")
s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
for w in s2.worksheets():
    print(f"  [ID: {w.id}] Title: '{w.title}' ({w.row_count} rows, {w.col_count} cols)")

print("\n=== SHEET 3: Grades ===")
s3 = service.client.open_by_key(cfg.GOOGLE_SHEETS_GRADES_ID)
for w in s3.worksheets():
    print(f"  [ID: {w.id}] Title: '{w.title}' ({w.row_count} rows, {w.col_count} cols)")
