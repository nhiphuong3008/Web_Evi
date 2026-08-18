import sys
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
from services.data_parser import DataParser, parse_float_vn, parse_number
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

ws = service.spreadsheet.worksheet('Báo cáo')
raw_data = ws.get_all_values()

def fixed_parse_acs_stats(raw_data):
    result = {
        'staff': [],
        'average': 0.0,
        'total_students': 0,
    }

    for i, row in enumerate(raw_data):
        if len(row) > 18 and row[17] == 'CM' and row[18] == 'ACS':
            # Read next 15 rows regardless of empty lines
            for j in range(i + 1, min(i + 15, len(raw_data))):
                r = raw_data[j]
                if len(r) <= 17:
                    continue

                name = r[17].strip()
                score_str = r[18].strip() if len(r) > 18 else ''

                if not name:
                    continue

                score = parse_float_vn(score_str)

                if name == 'TB':
                    result['average'] = score
                elif name == 'Tổng số HS':
                    result['total_students'] = parse_number(score_str)
                elif name not in ['CM', 'ACS']:
                    result['staff'].append({
                        'name': name,
                        'score': score,
                    })

            break

    return result

acs = fixed_parse_acs_stats(raw_data)
print("FIXED ACS STATS:", json.dumps(acs, ensure_ascii=False, indent=2))
