import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule, ClassMaster

def inspect_days():
    session = db_session()
    schedules = session.query(ClassSchedule).all()
    
    # Map class_name -> list of days
    class_days_map = {}
    for s in schedules:
        cname = s.class_name
        if cname not in class_days_map:
            class_days_map[cname] = []
        if s.day and s.day not in class_days_map[cname]:
            class_days_map[cname].append(s.day)
            
    print(f"Total classes in ClassSchedule: {len(class_days_map)}")
    print("\nClass Schedule Days Mapping Preview:")
    for cname in sorted(class_days_map.keys())[:15]:
        clean_cname = cname.encode('ascii', 'ignore').decode('ascii')
        clean_days = [d.encode('ascii', 'ignore').decode('ascii') for d in class_days_map[cname]]
        print(f"  Class '{clean_cname}': {clean_days}")
        
    # Also check ClassMaster
    print("\nChecking ClassMaster schedule column:")
    masters = session.query(ClassMaster).all()
    for m in masters[:10]:
        print(f"  Master Class '{m.class_name}' -> schedule: '{m.schedule}'")

    session.close()

if __name__ == '__main__':
    inspect_days()
