import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session, init_db
from database.models import Student
from services.db_service import get_students_db

def verify():
    init_db()
    res = get_students_db()
    print("Success:", res['success'])
    print("Total students count:", res['count'])

    data = res['data']
    print("\nVerifying first 10 students data:")
    for s in data[:10]:
        print(f"  - [{s['code']}] {s['name']} ({s['english_name']}) | Class: '{s['class_name']}' | Phone: '{s['phone']}' | Parent: '{s['parent_name']}' | Rem Sessions: {s.get('remaining_sessions')}")

    has_parent = len([s for s in data if s.get('parent_name')])
    has_phone = len([s for s in data if s.get('phone')])
    has_class = len([s for s in data if s.get('class_name')])

    print(f"\nStats across {len(data)} students:")
    print(f"  • Students with Parent Name: {has_parent} / {len(data)}")
    print(f"  • Students with Phone Number: {has_phone} / {len(data)}")
    print(f"  • Students with Enrolled Class: {has_class} / {len(data)}")

if __name__ == '__main__':
    verify()
