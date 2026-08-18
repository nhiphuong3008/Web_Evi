import sys
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.google_sheets import GoogleSheetsService
from services.data_parser import DataParser, parse_number, parse_percentage
import config

cfg = config.get_config()
service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
service.connect()

ws = service.spreadsheet.worksheet('Báo cáo')
raw_data = ws.get_all_values()

def fixed_parse_renewal_monthly(raw_data):
    results = []
    i = 0

    while i < len(raw_data):
        row = raw_data[i]

        if len(row) > 0 and row[0] == 'Tháng:':
            month = parse_number(row[1]) if len(row) > 1 else 0
            year = parse_number(row[3]) if len(row) > 3 else 0

            if month == 0 or year == 0:
                i += 1
                continue

            i += 1
            if i < len(raw_data):
                i += 1

            staff_data = []
            total_data = None

            while i < len(raw_data):
                row = raw_data[i]

                if len(row) == 0 or (len(row) > 0 and row[0] == 'Tháng:'):
                    break

                cm_name = row[0].strip() if len(row) > 0 else ''

                due = parse_number(row[1]) if len(row) > 1 else 0
                success = parse_number(row[2]) if len(row) > 2 else 0
                pending = parse_number(row[3]) if len(row) > 3 else 0
                failed = parse_number(row[4]) if len(row) > 4 else 0
                rate = parse_percentage(row[5]) if len(row) > 5 else 0.0

                if cm_name == 'Tổng':
                    total_data = {
                        'name': 'Tổng', 'due': due, 'success': success,
                        'pending': pending, 'failed': failed, 'rate': rate
                    }
                elif cm_name and cm_name not in ['CM', '#REF!'] and (due > 0 or success > 0 or pending > 0 or failed > 0):
                    staff_data.append({
                        'name': cm_name, 'due': due, 'success': success,
                        'pending': pending, 'failed': failed, 'rate': rate
                    })

                i += 1

            if staff_data:
                # If total_data is missing, auto calculate!
                if not total_data:
                    tot_due = sum(s['due'] for s in staff_data)
                    tot_success = sum(s['success'] for s in staff_data)
                    tot_pending = sum(s['pending'] for s in staff_data)
                    tot_failed = sum(s['failed'] for s in staff_data)
                    tot_rate = round((tot_success / tot_due * 100), 2) if tot_due > 0 else 0.0
                    total_data = {
                        'name': 'Tổng', 'due': tot_due, 'success': tot_success,
                        'pending': tot_pending, 'failed': tot_failed, 'rate': tot_rate
                    }

                results.append({
                    'month': month,
                    'year': year,
                    'staff': staff_data,
                    'total': total_data,
                })
        else:
            i += 1

    return results

monthly = fixed_parse_renewal_monthly(raw_data)
print("FIXED MONTHLY RENEWALS:")
for m in monthly:
    tot = m['total']
    print(f"  Month {m['month']}/{m['year']}: Staff count={len(m['staff'])}, Total due={tot['due']}, success={tot['success']}, rate={tot['rate']}%")
