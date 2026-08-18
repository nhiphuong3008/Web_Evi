import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import get_student_detail_db, update_student_status_db
from database.db_manager import db_session
from database.models import Student

def test_status_update_flow():
    session = db_session()
    # Find a test student
    st = session.query(Student).filter(Student.class_name != '').first()
    if not st:
        print("No active student with class found for testing.")
        return

    code = st.code
    original_class = st.class_name
    print(f"Testing status update flow for student {st.full_name} ({code}) currently in class '{original_class}'...")

    # 1. Change status to 'Bảo lưu'
    res_baoluu = update_student_status_db(code, 'Bảo lưu')
    print("1. Update to 'Bảo lưu':", res_baoluu.get('message'))
    
    st_check1 = session.query(Student).filter(Student.code == code).first()
    print(f"   Status: {st_check1.status}, Class: '{st_check1.class_name}', Last Class: '{st_check1.last_class_name}'")
    assert st_check1.status == 'Bảo lưu'
    assert st_check1.class_name == ''
    assert st_check1.last_class_name == original_class

    # 2. Restore to 'Đang học'
    res_danghoc = update_student_status_db(code, 'Đang học')
    print("2. Restore to 'Đang học':", res_danghoc.get('message'))
    
    st_check2 = session.query(Student).filter(Student.code == code).first()
    print(f"   Status: {st_check2.status}, Class: '{st_check2.class_name}', Last Class: '{st_check2.last_class_name}'")
    assert st_check2.status == 'Đang học'
    assert st_check2.class_name == original_class

    # 3. Change status to 'Đã nghỉ'
    res_danghi = update_student_status_db(code, 'Đã nghỉ')
    print("3. Update to 'Đã nghỉ':", res_danghi.get('message'))
    
    st_check3 = session.query(Student).filter(Student.code == code).first()
    print(f"   Status: {st_check3.status}, Class: '{st_check3.class_name}', Last Class: '{st_check3.last_class_name}'")
    assert st_check3.status == 'Đã nghỉ'
    assert st_check3.class_name == ''
    assert st_check3.last_class_name == original_class

    # 4. Cleanup/Restore back to original state
    update_student_status_db(code, 'Đang học')
    print("ALL TESTS PASSED SUCCESSFULLY! Restored original state.")

if __name__ == '__main__':
    test_status_update_flow()
