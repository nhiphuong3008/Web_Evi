import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import Student, ClassMaster, ClassSchedule, StudentSubscription, StudentRenewal, ParentInteractionLog, User

def normalize_cm_codes():
    session = db_session()
    print("==================================================================")
    print("🔄 THỰC HIỆN CHUẨN HÓA MÃ CM TRÊN TOÀN BỘ CSDL SQLITE (evi_center.db)")
    print("==================================================================")

    # Mapping rules
    cm_map = {
        'Vân Anh': 'AnhNV',
        'Vn Anh': 'AnhNV',
        'Amber': 'AnhNV',
        'Nguyễn Vân Anh': 'AnhNV',
        'Naomi': 'NgọcCM',
        'Cao Minh Ngọc': 'NgọcCM',
        'Thục Anh': 'AnhPTT',
        'Phạm Trần Thục Anh': 'AnhPTT',
        'Giang': 'NgọcCM',
        'Duyên': 'AnhPTT',
        'Ms. Lan': 'AnhNV'
    }

    # 1. Update Student table
    students = session.query(Student).all()
    st_count = 0
    for st in students:
        if st.cm_staff in cm_map:
            st.cm_staff = cm_map[st.cm_staff]
            st_count += 1

    # 2. Update ClassMaster table
    classes = session.query(ClassMaster).all()
    cls_count = 0
    for c in classes:
        if c.cm_staff in cm_map:
            c.cm_staff = cm_map[c.cm_staff]
            cls_count += 1

    # 3. Update ClassSchedule table
    scheds = session.query(ClassSchedule).all()
    sc_count = 0
    for sc in scheds:
        if sc.cm_staff in cm_map:
            sc.cm_staff = cm_map[sc.cm_staff]
            sc_count += 1

    # 4. Update StudentSubscription table
    subs = session.query(StudentSubscription).all()
    sub_count = 0
    for sub in subs:
        if sub.cm_staff in cm_map:
            sub.cm_staff = cm_map[sub.cm_staff]
            sub_count += 1

    # 5. Update StudentRenewal table
    rens = session.query(StudentRenewal).all()
    ren_count = 0
    for ren in rens:
        if ren.cm_staff in cm_map:
            ren.cm_staff = cm_map[ren.cm_staff]
            ren_count += 1

    # 6. Update ParentInteractionLog table
    logs = session.query(ParentInteractionLog).all()
    log_count = 0
    for log in logs:
        if log.staff_name in cm_map:
            log.staff_name = cm_map[log.staff_name]
            log_count += 1

    # 7. Update User table
    users = session.query(User).all()
    usr_count = 0
    for u in users:
        if u.cm_staff_name in cm_map:
            u.cm_staff_name = cm_map[u.cm_staff_name]
            usr_count += 1

    session.commit()
    session.close()

    print(f"  • Đã chuẩn hóa {st_count} bản ghi trong Bảng Student")
    print(f"  • Đã chuẩn hóa {cls_count} bản ghi trong Bảng ClassMaster")
    print(f"  • Đã chuẩn hóa {sc_count} bản ghi trong Bảng ClassSchedule (Thời khóa biểu)")
    print(f"  • Đã chuẩn hóa {sub_count} bản ghi trong Bảng StudentSubscription")
    print(f"  • Đã chuẩn hóa {ren_count} bản ghi trong Bảng StudentRenewal")
    print(f"  • Đã chuẩn hóa {log_count} bản ghi trong Bảng ParentInteractionLog")
    print(f"  • Đã chuẩn hóa {usr_count} bản ghi trong Bảng User")
    print("==================================================================")
    print("✅ TOÀN BỘ CSDL SQLITE ĐÃ ĐƯỢC ĐỒNG BỘ NGHỆ AN VỀ 3 MÃ CM: NgọcCM, AnhPTT, AnhNV!")

if __name__ == '__main__':
    normalize_cm_codes()
