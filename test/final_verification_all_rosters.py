import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_cm_classes_db, get_students_db

def verify_all():
    print("=== FINAL ROSTER VERIFICATION ===")
    res = get_cm_classes_db()
    classes = res.get('data', [])
    
    print(f"Total Classes in CM Portal: {len(classes)}")
    print("-" * 65)
    
    for c in classes:
        cname = c['class_name']
        st_res = get_students_db(class_name=cname, status='Đang học')
        st_list = st_res.get('data', [])
        clean_cname = cname.encode('ascii', 'ignore').decode('ascii')
        print(f"  Class '{clean_cname:16s}': Dropdown Count = {c['student_count']:2d} HS | Actual Roster Count = {len(st_list):2d} HS")
        if c['student_count'] != len(st_list):
            print(f"    [WARNING] MISMATCH DETECTED FOR CLASS {clean_cname}!")
        else:
            print(f"    [SUCCESS] PERFECT MATCH!")

if __name__ == '__main__':
    verify_all()
