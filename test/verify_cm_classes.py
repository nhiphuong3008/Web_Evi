import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_cm_classes_db

def test_cm():
    res = get_cm_classes_db(cm_staff_name=None)
    data = res.get('data', [])
    print(f"Total CM Classes returned: {len(data)}")
    for c in data:
        print(f"  Class: {c['class_name']:12s} | Students: {c.get('student_count', 0):2d} | Teacher: {c.get('teacher', '---')}")

if __name__ == '__main__':
    test_cm()
