import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassMaster, Student, StudentSubscription
from services.db_service import add_class_db

def test_class_creation_and_editing():
    print("==================================================================")
    print("🧪 KIỂM THỬ TÍNH NĂNG TẠO LỚP MỚI & CHỈNH SỬA LỚP ĐỘNG (CM / GV)")
    print("==================================================================")

    session = db_session()

    # 1. Create new class "Sun 1.5"
    test_class_data = {
        'class_name': 'Sun 1.5',
        'curriculum': 'Sun',
        'schedule': 'MT6 (17:30-19:00) • T3/T6',
        'start_date': '2026-08-17',
        'teacher': 'Andrew',
        'cm_staff': 'AnhNV',
        'room': 'Mars',
        'status': 'Đang hoạt động'
    }

    print("\n1. Thử nghiệm tạo lớp mới 'Sun 1.5'...")
    res = add_class_db(test_class_data)
    print(f"  Result: {res}")
    assert res.get('success') is True, "Failed to create class 'Sun 1.5'"

    # Verify ClassMaster in DB
    cls_obj = session.query(ClassMaster).filter(ClassMaster.class_name == 'Sun 1.5').first()
    assert cls_obj is not None, "Class 'Sun 1.5' not found in ClassMaster table"
    assert cls_obj.cm_staff == 'AnhNV', f"Expected CM 'AnhNV', got '{cls_obj.cm_staff}'"
    assert cls_obj.teacher == 'Andrew', f"Expected Teacher 'Andrew', got '{cls_obj.teacher}'"
    print("  ✅ Tạo lớp mới 'Sun 1.5' thành công!")

    # 2. Add a dummy student in Sun 1.5 for sync test
    dummy_student = session.query(Student).filter(Student.code == 'TEST_EVI_999').first()
    if not dummy_student:
        dummy_student = Student(
            code='TEST_EVI_999',
            full_name='Học Sinh Test Sun 1.5',
            class_name='Sun 1.5',
            cm_staff='AnhNV',
            teacher='Andrew',
            status='Đang học'
        )
        session.add(dummy_student)
        session.commit()

    # 3. Edit class "Sun 1.5" -> Change CM to 'NgọcCM' & Teacher to 'Jacob'
    print("\n2. Thử nghiệm chỉnh sửa Lớp 'Sun 1.5' (Đổi CM sang 'NgọcCM' & GV sang 'Jacob')...")
    edit_class_data = {
        'original_class_name': 'Sun 1.5',
        'class_name': 'Sun 1.5',
        'curriculum': 'Sun',
        'schedule': 'MT6 (17:30-19:00) • T3/T6',
        'start_date': '2026-08-17',
        'teacher': 'Jacob',
        'cm_staff': 'NgọcCM',
        'room': 'Jupiter',
        'status': 'Đang hoạt động'
    }
    res_edit = add_class_db(edit_class_data)
    print(f"  Result: {res_edit}")
    assert res_edit.get('success') is True, "Failed to edit class 'Sun 1.5'"

    # 4. Verify Student sync
    st_updated = session.query(Student).filter(Student.code == 'TEST_EVI_999').first()
    assert st_updated.cm_staff == 'NgọcCM', f"Student CM sync failed: expected 'NgọcCM', got '{st_updated.cm_staff}'"
    assert st_updated.teacher == 'Jacob', f"Student Teacher sync failed: expected 'Jacob', got '{st_updated.teacher}'"
    print("  ✅ Chỉnh sửa lớp và đồng bộ tự động 100% CM & GV cho học sinh thành công!")

    # 5. Clean up test data
    session.query(Student).filter(Student.code == 'TEST_EVI_999').delete()
    session.query(ClassMaster).filter(ClassMaster.class_name == 'Sun 1.5').delete()
    session.commit()
    session.close()
    print("\n==================================================================")
    print("🎉 TẤT CẢ CÁC BÀI KIỂM THỬ DỰ ÁN ĐÃ PASS 100%!")
    print("==================================================================")

if __name__ == '__main__':
    test_class_creation_and_editing()
