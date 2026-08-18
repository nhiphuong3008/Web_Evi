import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import Student, StudentSubscription, StudentRenewal

def audit_and_sync_all():
    session = db_session()
    print("==================================================================")
    print("🔍 RÀ SOÁT VÀ ĐỒNG BỘ 100% DỮ LIỆU HỌC SINH ĐANG HỌC THEO MÃ HS")
    print("==================================================================")

    # 1. Fetch all Master Students
    master_students = session.query(Student).all()
    master_dict = {st.code: st for st in master_students if st.code}
    print(f"Tổng số học sinh trong Bảng Master (Student): {len(master_students)}")
    
    active_students = [st for st in master_students if st.status == 'Đang học']
    print(f"Số học sinh đang học (status == 'Đang học'): {len(active_students)}")

    # 2. Audit StudentSubscription records
    subs = session.query(StudentSubscription).all()
    print(f"\n📋 Tổng số bản ghi Gói Tái Phí (StudentSubscription): {len(subs)}")

    sub_mismatches = []
    sub_updated_count = 0

    for sub in subs:
        st_master = master_dict.get(sub.student_code)
        if not st_master:
            continue

        needs_update = False
        mismatch_details = []

        # Check Class
        if st_master.class_name and sub.class_name != st_master.class_name:
            mismatch_details.append(f"Lớp: '{sub.class_name}' -> '{st_master.class_name}'")
            sub.class_name = st_master.class_name
            needs_update = True

        # Check CM
        if st_master.cm_staff and sub.cm_staff != st_master.cm_staff:
            mismatch_details.append(f"CM: '{sub.cm_staff}' -> '{st_master.cm_staff}'")
            sub.cm_staff = st_master.cm_staff
            needs_update = True

        # Check Name
        if st_master.full_name and sub.student_name != st_master.full_name:
            mismatch_details.append(f"Tên: '{sub.student_name}' -> '{st_master.full_name}'")
            sub.student_name = st_master.full_name
            needs_update = True

        # Check English Name
        if st_master.english_name and sub.english_name != st_master.english_name:
            sub.english_name = st_master.english_name
            needs_update = True

        if needs_update:
            sub_updated_count += 1
            sub_mismatches.append({
                'code': sub.student_code,
                'name': st_master.full_name,
                'changes': mismatch_details
            })

    # 3. Audit StudentRenewal records
    ren_records = session.query(StudentRenewal).all()
    print(f"\n📋 Tổng số bản ghi Đợt Tái Phí Lịch Sử (StudentRenewal): {len(ren_records)}")
    ren_updated_count = 0

    for ren in ren_records:
        st_master = master_dict.get(ren.student_code)
        if not st_master:
            continue

        needs_update = False
        if st_master.class_name and ren.class_name != st_master.class_name:
            ren.class_name = st_master.class_name
            needs_update = True
        if st_master.cm_staff and ren.cm_staff != st_master.cm_staff:
            ren.cm_staff = st_master.cm_staff
            needs_update = True
        if st_master.full_name and ren.student_name != st_master.full_name:
            ren.student_name = st_master.full_name
            needs_update = True

        if needs_update:
            ren_updated_count += 1

    session.commit()

    print("\n" + "=" * 66)
    print(f"📊 KẾT QUẢ RÀ SOÁT TỔNG THỂ:")
    print(f"  • Phát hiện và đã sửa lỗi lệch cho: {sub_updated_count} bản ghi Subscription")
    print(f"  • Phát hiện và đã sửa lỗi lệch cho: {ren_updated_count} bản ghi StudentRenewal")
    print("=" * 66)

    if sub_mismatches:
        print("\n📝 CHI TIẾT CÁC HỌC SINH ĐÃ ĐƯỢC CHUẨN HÓA LỚP & CM THÀNH CÔNG:")
        for idx, item in enumerate(sub_mismatches, 1):
            print(f"  {idx}. [{item['code']}] {item['name']} ➔ {', '.join(item['changes'])}")

    session.close()

if __name__ == '__main__':
    audit_and_sync_all()
