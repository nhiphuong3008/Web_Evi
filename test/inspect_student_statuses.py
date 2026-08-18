import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import Student

def inspect_statuses():
    session = db_session()
    all_students = session.query(Student).all()
    print(f"Total students in DB: {len(all_students)}")

    statuses = {}
    baoluu_list = []
    danghi_list = []
    class_is_baoluu = []

    for s in all_students:
        st = s.status or 'Unknown'
        statuses[st] = statuses.get(st, 0) + 1
        
        if s.class_name and 'bảo lưu' in s.class_name.lower():
            class_is_baoluu.append((s.code, s.full_name, s.class_name, s.status))

        if s.status == 'Bảo lưu':
            baoluu_list.append((s.code, s.full_name, s.class_name, s.last_class_name))

        if s.status == 'Đã nghỉ':
            danghi_list.append((s.code, s.full_name, s.class_name, s.last_class_name))

    print("\n--- STATUS COUNTS IN DB ---")
    for st, cnt in statuses.items():
        print(f"  • Status '{st}': {cnt} students")

    print(f"\nStudents with status 'Bảo lưu' ({len(baoluu_list)}):")
    for b in baoluu_list[:15]:
        print(f"  {b[0]} - {b[1]} | Class: '{b[2]}' | Last Class: '{b[3]}'")

    print(f"\nStudents where class_name column contains 'Bảo lưu' ({len(class_is_baoluu)}):")
    for c in class_is_baoluu:
        print(f"  {c[0]} - {c[1]} | Class: '{c[2]}' | Status: '{c[3]}'")

if __name__ == '__main__':
    inspect_statuses()
