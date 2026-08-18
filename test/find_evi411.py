import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import Student

def find_st():
    session = db_session()
    matches = session.query(Student).filter(
        (Student.code.ilike("%EVI411%")) | (Student.full_name.ilike("%Ngô Bảo Vy%")) | (Student.full_name.ilike("%Bảo Vy%"))
    ).all()
    
    print(f"Found {len(matches)} matches for EVI411 / Bao Vy:")
    for s in matches:
        c_name = s.full_name.encode('ascii', 'ignore').decode('ascii')
        c_class = str(s.class_name).encode('ascii', 'ignore').decode('ascii')
        c_status = str(s.status).encode('ascii', 'ignore').decode('ascii')
        print(f"  Code: {s.code} | Name: {c_name} | Class: {c_class} | Status: {c_status}")

if __name__ == '__main__':
    find_st()
