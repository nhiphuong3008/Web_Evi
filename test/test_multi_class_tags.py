import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import Student
from services.db_service import add_student_class_db, remove_student_class_db

def test_class_tags():
    session = db_session()
    # Pick a student: EVI068 (Nguyễn Ngọc Minh)
    st = session.query(Student).filter(Student.code == 'EVI068').first()
    if not st:
        print("Student EVI068 not found.")
        return

    original_classes = st.class_name
    print(f"Testing Class Tag Manager for {st.full_name} ({st.code}). Initial classes: '{original_classes}'")

    # 1. Add a 2nd class: 'Sun 2.1'
    res1 = add_student_class_db('EVI068', 'Sun 2.1')
    print("1. Add class 'Sun 2.1':", res1.get('message'))
    assert res1.get('success') == True
    
    st_check1 = session.query(Student).filter(Student.code == 'EVI068').first()
    print("   Updated classes in DB:", repr(st_check1.class_name))
    assert 'Sun 2.1' in st_check1.class_name

    # 2. Remove 'Sun 2.1'
    res2 = remove_student_class_db('EVI068', 'Sun 2.1')
    print("2. Remove class 'Sun 2.1':", res2.get('message'))
    assert res2.get('success') == True

    st_check2 = session.query(Student).filter(Student.code == 'EVI068').first()
    print("   Final classes in DB:", repr(st_check2.class_name))
    assert 'Sun 2.1' not in st_check2.class_name

    print("\nALL CLASS TAG MANAGER TESTS PASSED 100%!")

if __name__ == '__main__':
    test_class_tags()
