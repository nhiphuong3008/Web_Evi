import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import Student

def inspect_classes():
    session = db_session()
    
    print("=== 1. CHECK GALAX 1.3 STUDENTS ===")
    st_g13 = session.query(Student).filter(Student.class_name.ilike("%Galax 1.3%")).all()
    print(f"Total students matched 'Galax 1.3': {len(st_g13)}")
    for s in st_g13:
        clean_name = s.full_name.encode('ascii', 'ignore').decode('ascii')
        clean_class = str(s.class_name).encode('ascii', 'ignore').decode('ascii')
        clean_status = str(s.status).encode('ascii', 'ignore').decode('ascii')
        print(f"  Code: {s.code:7s} | Name: {clean_name:25s} | Status: {clean_status:10s} | Class: {clean_class}")

    print("\n=== 2. CHECK EVI122 (Khuat Pham Minh Anh) ===")
    evi122 = session.query(Student).filter((Student.code == 'EVI122') | (Student.full_name.ilike("%Minh Anh%"))).all()
    for s in evi122:
        clean_name = s.full_name.encode('ascii', 'ignore').decode('ascii')
        clean_class = str(s.class_name).encode('ascii', 'ignore').decode('ascii')
        clean_status = str(s.status).encode('ascii', 'ignore').decode('ascii')
        print(f"  Code: {s.code:7s} | Name: {clean_name:25s} | Status: {clean_status:10s} | Class: {clean_class}")

    print("\n=== 3. CHECK LOP ON THI 9-10 STUDENTS ===")
    st_onthi = session.query(Student).filter(
        (Student.class_name.ilike("%n thi%")) | 
        (Student.class_name.ilike("%9-10%")) |
        (Student.grammar_class.ilike("%n thi%")) |
        (Student.grammar_class.ilike("%9-10%"))
    ).all()
    print(f"Total students matched 'Lop on thi 9-10': {len(st_onthi)}")
    for s in st_onthi:
        clean_name = s.full_name.encode('ascii', 'ignore').decode('ascii')
        clean_class = str(s.class_name).encode('ascii', 'ignore').decode('ascii')
        clean_status = str(s.status).encode('ascii', 'ignore').decode('ascii')
        print(f"  Code: {s.code:7s} | Name: {clean_name:25s} | Status: {clean_status:10s} | Class: {clean_class}")

    session.close()

if __name__ == '__main__':
    inspect_classes()
