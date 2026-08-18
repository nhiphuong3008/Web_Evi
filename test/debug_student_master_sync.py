import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import Student, StudentSubscription, StudentRenewal

def check_master():
    session = db_session()
    print("--- Inspecting Master Student vs Subscription Data ---")
    codes = ['EVI313', 'EVI347', 'EVI038', 'EVI305']
    for code in codes:
        st = session.query(Student).filter(Student.code == code).first()
        sub = session.query(StudentSubscription).filter(StudentSubscription.student_code == code).first()
        print(f"\n📌 Code: {code}")
        if st:
            print(f"  [Master Student] Name: {st.full_name} | Class: {st.class_name} | CM: {st.cm_staff} | Status: {st.status}")
        else:
            print("  [Master Student] NOT FOUND")
        if sub:
            print(f"  [Subscription  ] Name: {sub.student_name} | Class: {sub.class_name} | CM: {sub.cm_staff} | Status: {sub.renewal_status}")
        else:
            print("  [Subscription  ] NOT FOUND")

    session.close()

if __name__ == '__main__':
    check_master()
