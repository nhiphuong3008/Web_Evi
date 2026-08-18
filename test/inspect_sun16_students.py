import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import Student, ClassMaster
from services.db_service import get_attendance_db

def inspect_sun16():
    session = db_session()
    print("==================================================")
    print("INSPECT CLASS SUN 1.6 STUDENTS IN SQLITE DB")
    print("==================================================")

    # 1. Search ClassMaster for Sun 1.6
    cm = session.query(ClassMaster).filter(ClassMaster.class_name.like('%Sun 1.6%')).all()
    print("ClassMaster matching 'Sun 1.6':")
    for c in cm:
        print(f"  ID: {c.id} | Name: '{c.class_name}' | Count: {c.student_count}")

    # 2. Search Students with class_name matching Sun 1.6
    students = session.query(Student).filter(Student.class_name.like('%Sun 1.6%')).all()
    print(f"\nStudents in SQLite matching '%Sun 1.6%' (Total: {len(students)}):")
    for s in students:
        print(f"  Code: {s.code} | Name: '{s.full_name}' | Class: '{s.class_name}' | Status: '{s.status}'")

    # 3. All distinct student class_names in DB
    print("\nDistinct class_names in Student table:")
    classes = session.query(Student.class_name).distinct().all()
    for cl in sorted([c[0] for c in classes if c[0]]):
        print(f"  '{cl}'")

    # 4. Test get_attendance_db('Sun 1.6', '08/08/2026')
    print("\nTest get_attendance_db('Sun 1.6', '08/08/2026'):")
    res = get_attendance_db('Sun 1.6', '08/08/2026')
    print("  Success:", res.get('success'))
    print("  Students count in response:", len(res.get('students', [])))

    session.close()

if __name__ == '__main__':
    inspect_sun16()
