import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import Student, StudentEnrollment

session = db_session()

students = session.query(Student).limit(10).all()
print("=== SAMPLE 10 STUDENTS IN DB ===")
for s in students:
    en = session.query(StudentEnrollment).filter_by(student_code=s.code).first()
    print(f"Code: {s.code} | Name: {s.full_name} | Parent: '{s.parent_name}' | Phone: '{s.phone}' | DOB: '{s.dob}'")
    if en:
        print(f"   -> Class: {en.class_name} | Total Sess: {en.total_sessions} | Rem Sess: {en.remaining_sessions} | Exp Date: '{en.expiry_date}' | Exp Month: '{en.expiry_month}'")
    else:
        print("   -> NO ENROLLMENT")

# Count missing fields
no_parent = session.query(Student).filter(or_(Student.parent_name == None, Student.parent_name == '')).count() if hasattr(Student, 'parent_name') else 0
print(f"\nTotal Students: {session.query(Student).count()}")
