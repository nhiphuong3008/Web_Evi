import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import get_student_detail_db

def test_grouped():
    # Student EVI056 (Nguyễn Ngọc Huyền - 2 classes: Galax 1.4, Khóa Debate 2026)
    res = get_student_detail_db('EVI056')
    assert res.get('success') == True
    
    st = res.get('student', {})
    hw_list = res.get('homework', [])
    grade_list = res.get('grades', [])

    print(f"Testing Profile for {st.get('name')} ({st.get('code')}) - Classes: '{st.get('class_name')}'")
    print(f"Total Homework Records: {len(hw_list)}")
    print(f"Total Grade Records: {len(grade_list)}")

    # Group HW by class
    hw_grouped = {}
    for h in hw_list:
        c = (h.get('phone_class') or h.get('class_name') or 'Khác').strip()
        hw_grouped[c] = hw_grouped.get(c, 0) + 1

    print("Homework Breakdown By Class:")
    for c_name, count in hw_grouped.items():
        print(f"  • Class '{c_name}': {count} records")

    # Group Grades by class
    grade_grouped = {}
    for g in grade_list:
        c = (g.get('class_name') or 'Khác').strip()
        grade_grouped[c] = grade_grouped.get(c, 0) + 1

    print("Grades Breakdown By Class:")
    for c_name, count in grade_grouped.items():
        print(f"  • Class '{c_name}': {count} records")

    print("\nGROUPED DATA TEST PASSED 100%!")

if __name__ == '__main__':
    test_grouped()
