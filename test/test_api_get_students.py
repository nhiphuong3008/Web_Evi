import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_students_db

def test_api():
    res = get_students_db(class_name='Galax 1.3')
    data = res.get('data', [])
    print(f"get_students_db(class_name='Galax 1.3') returned {len(data)} students:")
    for s in data:
        clean_name = s['name'].encode('ascii', 'ignore').decode('ascii')
        clean_class = str(s.get('class_name')).encode('ascii', 'ignore').decode('ascii')
        clean_status = str(s.get('status')).encode('ascii', 'ignore').decode('ascii')
        print(f"  Code: {s['code']:7s} | Name: {clean_name:25s} | Class: '{clean_class}' | Status: '{clean_status}'")

if __name__ == '__main__':
    test_api()
