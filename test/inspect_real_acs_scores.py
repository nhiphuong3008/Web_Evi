import os
import sys
import sqlite3
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("SELECT DISTINCT report_type FROM kpi_monthly_reports")
print("kpi_monthly_reports types:", c.fetchall())

c.execute("SELECT cm_staff, report_type, raw_value, rate_percent FROM kpi_monthly_reports WHERE report_type LIKE '%acs%' OR raw_value LIKE '%acs%' OR cm_staff IS NOT NULL")
rows = c.fetchall()
print(f"kpi_monthly_reports rows count: {len(rows)}")
for r in rows[:15]:
    print(r)

conn.close()

# Also let's try google_sheets if API credentials/local cache exists
try:
    from services.google_sheets import get_sheets_service
    sheets = get_sheets_service()
    data = sheets.read_sheet('Báo cáo')
    from services.data_parser import DataParser
    p = DataParser(data)
    acs = p.parse_acs_stats()
    print("\nParsed REAL ACS stats from Google Sheet ('Báo cáo'):")
    print(json.dumps(acs, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"\nGoogle Sheets read error: {e}")
