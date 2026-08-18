import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import HolidayHistoryLog, ClassScheduleAdjustment

session = db_session()

print("--- Active HolidayHistoryLog entries ---")
holidays = session.query(HolidayHistoryLog).filter(HolidayHistoryLog.status == 'Active').all()
for h in holidays:
    print(f"ID={h.id} | type='{h.holiday_type}' | start='{h.start_date}' | end='{h.end_date}' | affected='{h.affected_classes}'")

print("\n--- ClassScheduleAdjustment entries ---")
adjs = session.query(ClassScheduleAdjustment).all()
for a in adjs:
    print(f"ID={a.id} | class_name='{a.class_name}' | delayed='{a.delayed_lessons}' | note='{a.note}'")

session.close()
