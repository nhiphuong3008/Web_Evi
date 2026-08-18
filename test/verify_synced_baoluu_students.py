import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import Student

def verify_baoluu():
    session = db_session()
    codes = [
        "EVI030", "EVI070", "EVI132", "EVI149", "EVI173", "EVI188", 
        "EVI201", "EVI204", "EVI234", "EVI275", "EVI310", "EVI299", 
        "EVI312", "EVI316", "EVI319", "EVI325", "EVI117", "EVI335", 
        "EVI336", "EVI337", "EVI344", "EVI350", "EVI355", "EVI405", 
        "EVI340", "EVI371", "EVI389", "EVI303", "EVI302"
    ]

    baoluu_count = session.query(Student).filter(Student.status == 'Bảo lưu').count()
    print(f"Total students with status 'Bảo lưu' in DB: {baoluu_count}")

    matched = 0
    for code in codes:
        st = session.query(Student).filter(Student.code == code).first()
        if st:
            print(f"  • {st.code} - {st.full_name} | Status: {st.status}")
            if st.status == 'Bảo lưu':
                matched += 1
        else:
            print(f"  • {code} - NOT FOUND IN DB")

    print(f"\nResult: Matched {matched}/{len(codes)} sample Bảo lưu students!")
    assert matched == len(codes)

if __name__ == '__main__':
    verify_baoluu()
