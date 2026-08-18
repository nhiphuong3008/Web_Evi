import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_students_db, get_cm_classes_db

def test_final():
    print("=== 1. VERIFY GALAX 1.3 ===")
    res1 = get_students_db(class_name="Galax 1.3", status="Đang học")
    st1 = res1.get('data', [])
    print(f"Galax 1.3 Total Roster Count: {len(st1)} HS")
    for s in st1:
        clean_name = s['name'].encode('ascii', 'ignore').decode('ascii')
        clean_eng = s.get('english_name', '').encode('ascii', 'ignore').decode('ascii')
        print(f"  Code: {s['code']:7s} | Name: {clean_name:25s} | EngName: {clean_eng}")

    print("\n=== 2. VERIFY LOP ON THI 9-10 ===")
    res2 = get_students_db(class_name="Lớp ôn thi 9-10", status="Đang học")
    st2 = res2.get('data', [])
    print(f"Lop on thi 9-10 Total Roster Count: {len(st2)} HS")
    for s in st2:
        clean_name = s['name'].encode('ascii', 'ignore').decode('ascii')
        clean_eng = s.get('english_name', '').encode('ascii', 'ignore').decode('ascii')
        print(f"  Code: {s['code']:7s} | Name: {clean_name:25s} | EngName: {clean_eng}")

if __name__ == '__main__':
    test_final()
