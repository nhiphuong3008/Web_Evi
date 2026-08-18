import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import Student

def check_galax14():
    session = db_session()
    
    # 1. Query all students matching Galax 1.4
    all_st = session.query(Student).filter(Student.class_name.ilike("%Galax 1.4%")).all()
    print(f"Total Students matching 'Galax 1.4' in DB: {len(all_st)}")
    
    for idx, s in enumerate(all_st, 1):
        clean_name = s.full_name.encode('ascii', 'ignore').decode('ascii')
        clean_status = str(s.status).encode('ascii', 'ignore').decode('ascii')
        clean_class = str(s.class_name).encode('ascii', 'ignore').decode('ascii')
        print(f"  {idx:2d}. Code: {s.code:7s} | Name: {clean_name:25s} | Status: '{clean_status}' | Class: '{clean_class}'")

    session.close()

if __name__ == '__main__':
    check_galax14()
