import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import Student
from services.db_service import get_students_db

def debug_search():
    session = db_session()
    
    # 1. Search in DB directly
    print("1. Searching directly in Student table for 'Long' or 'Trần'...")
    students_long = session.query(Student).filter(Student.full_name.ilike('%Long%')).all()
    print(f"   Found {len(students_long)} students with 'Long' in name:")
    for s in students_long:
        print(f"   • Code: {s.code} | Name: '{s.full_name}' | English Name: '{s.english_name}' | Class: '{s.class_name}' | Status: '{s.status}'")

    # 2. Test get_students_db with search queries
    queries = ["trần đình long", "Trần Đình Long", "Long", "dinh long"]
    for q in queries:
        res = get_students_db(search_query=q)
        print(f"\n2. get_students_db(search_query='{q}'):")
        print(f"   Total matching: {res.get('total', 0)}")
        for st in res.get('data', [])[:5]:
            print(f"   -> {st['code']} - {st['name']} (Class: {st['class_name']}, Status: {st['status']})")

if __name__ == '__main__':
    debug_search()
