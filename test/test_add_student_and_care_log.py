import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import Student, ParentInteractionLog
from services.db_service import (
    add_new_student_db, update_student_class_db, 
    add_parent_interaction_log_db, get_student_detail_db
)

def test_new_features():
    # Cleanup previous test data
    session = db_session()
    session.query(ParentInteractionLog).filter(ParentInteractionLog.student_code == 'EVI999').delete()
    session.query(Student).filter(Student.code == 'EVI999').delete()
    session.commit()

    print("1. Testing add_new_student_db...")
    st_payload = {
        'code': 'EVI999',
        'name': 'Nguyễn Văn Test',
        'english_name': 'Tommy',
        'dob': '01/01/2015',
        'parent_name': 'Nguyễn Văn A',
        'phone': '0912345678',
        'class_name': 'Sun 2.2',
        'status': 'Đang học',
        'total_sessions': 48,
        'remaining_sessions': 48
    }

    res_add = add_new_student_db(st_payload)
    print("   Add Result:", res_add.get('message'))
    assert res_add.get('success') == True

    print("\n2. Testing update_student_class_db (Manual class selection)...")
    res_class = update_student_class_db('EVI999', 'Galax 1.3')
    print("   Class Update Result:", res_class.get('message'))
    assert res_class.get('success') == True

    print("\n3. Testing add_parent_interaction_log_db (Care Log entry)...")
    res_log1 = add_parent_interaction_log_db('EVI999', 'CM Thục Anh', 'Lần 1: Học sinh làm bài tập về nhà đầy đủ.')
    print("   Log 1 Result:", res_log1.get('message'))

    res_log2 = add_parent_interaction_log_db('EVI999', 'CM Thục Anh', 'Lần 2 (Mới nhất): Phụ huynh xin nghỉ học buổi tới.')
    print("   Log 2 Result:", res_log2.get('message'))

    print("\n4. Verifying detail profile and newest-first order of care logs...")
    res_detail = get_student_detail_db('EVI999')
    assert res_detail.get('success') == True
    
    logs = res_detail.get('cm_notes', [])
    print(f"   Total care logs found: {len(logs)}")
    assert len(logs) >= 2
    # Verify newest log is at index 0
    print("   Index 0 Note (Newest):", logs[0].get('note'))
    assert "Lần 2 (Mới nhất)" in logs[0].get('note')

    print("\nALL AUTOMATED TESTS FOR NEW FEATURES PASSED 100%!")

if __name__ == '__main__':
    test_new_features()
