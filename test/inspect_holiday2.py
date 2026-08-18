import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import HolidayHistoryLog

session = db_session()

print("--- All HolidayHistoryLog entries ---")
rows = session.query(HolidayHistoryLog).all()
for r in rows:
    print(f"ID={r.id} | holiday_type='{r.holiday_type}' | start='{r.start_date}' | end='{r.end_date}' | status='{r.status}' | note='{r.note}'")

session.close()
