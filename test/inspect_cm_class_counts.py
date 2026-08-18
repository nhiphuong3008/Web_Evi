import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import User, ClassSchedule, Student, ClassMaster
from services.db_service import get_cm_classes_db

def main():
    session = db_session()
    users = session.query(User).filter(User.role == 'cm').all()
    
    print("==================================================")
    print("THỐNG KÊ SỐ LƯỢNG LỚP THEO TỪNG CM USER TRONG DB")
    print("==================================================")

    res = get_cm_classes_db('', include_ended=False)
    all_classes = res.get('data', [])
    print(f"Tổng số lớp đang hoạt động: {len(all_classes)}\n")

    for u in users:
        cm_name = u.cm_staff_name
        cm_clean = cm_name.lower()
        matched_classes = [c['class_name'] for c in all_classes if cm_clean in (c.get('cm_staff') or '').lower()]
        print(f"👤 User CM: {u.full_name:<15} | CM Name: '{cm_name}' -> Đang phụ trách {len(matched_classes)} lớp:")
        print(f"   Lớp: {', '.join(matched_classes) if matched_classes else '(Chưa có lớp nào)'}")

    session.close()

if __name__ == "__main__":
    main()
