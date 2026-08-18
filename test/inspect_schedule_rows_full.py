import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule

session = db_session()
rows = session.query(ClassSchedule).order_by(ClassSchedule.day, ClassSchedule.shift_code, ClassSchedule.id).all()
print(f"Total rows in ClassSchedule: {len(rows)}")
print("="*120)

current_day = None
for r in rows:
    if r.day != current_day:
        current_day = r.day
        print(f"\n--- {r.day} ---")
    print(f"  ID:{r.id:3d} | Shift:{r.shift_code:4s} | Class: {r.class_name:18s} | Room: {r.room:10s} | GV: {r.teacher:18s} | Sĩ số: {r.students_count:2d} | CM: {r.cm_staff:10s} | TA: {r.ta_staff or '—'}")

session.close()
