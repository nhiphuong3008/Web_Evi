import sys
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
from services.data_parser import DataParser
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

ws = service.spreadsheet.worksheet('Báo cáo')
raw_data = ws.get_all_values()

parser = DataParser(raw_data)
monthly = parser.parse_renewal_monthly()

print("ALL MONTHLY RENEWALS:")
for m in monthly:
    tot = m.get('total') or {}
    print(f"Month {m['month']}/{m['year']}: Total due={tot.get('due', 0)}, success={tot.get('success', 0)}, rate={tot.get('rate', 0)}%")
