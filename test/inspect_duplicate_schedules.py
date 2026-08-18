import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule

def inspect_duplicates():
    session = db_session()
    all_sc = session.query(ClassSchedule).all()
    print(f"Total records in ClassSchedule: {len(all_sc)}")

    seen = {}
    duplicates = []
    for sc in all_sc:
        key = (sc.class_name.strip().lower(), (sc.day or '').strip().lower(), (sc.shift_code or '').strip().lower())
        if key in seen:
            duplicates.append((sc, seen[key]))
        else:
            seen[key] = sc

    print(f"Unique class-day-shift schedules: {len(seen)}")
    print(f"Duplicate schedule rows: {len(duplicates)}\n")

    for dup, orig in duplicates:
        print(f"DUPLICATE ID {dup.id}: Class '{dup.class_name}' | Day '{dup.day}' | Shift '{dup.shift_code}' | CM '{dup.cm_staff}' | GV '{dup.teacher}' (Original ID {orig.id}: CM '{orig.cm_staff}')")

    session.close()

if __name__ == "__main__":
    inspect_duplicates()
