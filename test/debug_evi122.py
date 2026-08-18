import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import Student

def debug():
    session = db_session()
    
    # Check EVI122 exact values
    evi122 = session.query(Student).filter(Student.code == 'EVI122').first()
    if evi122:
        d = evi122.to_dict()
        # Print key fields as ascii-safe
        for k in ['code', 'name', 'english_name', 'class_name', 'grammar_class', 'status']:
            v = str(d.get(k, '')).encode('ascii', 'ignore').decode('ascii')
            print(f"  EVI122.{k} = '{v}'")
    
    print("\n--- Simulating loadRosterForClass('Galax 1.3') ---")
    # Simulate the exact query from get_students_db
    from sqlalchemy import or_
    query = session.query(Student)
    clean_c = 'Galax 1.3'
    query = query.filter(or_(
        Student.class_name.ilike(f"%{clean_c}%"),
        Student.grammar_class.ilike(f"%{clean_c}%")
    ))
    students = query.all()
    print(f"Total results: {len(students)}")
    for s in students:
        d = s.to_dict()
        cn = str(d.get('name','')).encode('ascii','ignore').decode('ascii')
        cc = str(d.get('class_name','')).encode('ascii','ignore').decode('ascii')
        cs = str(d.get('status','')).encode('ascii','ignore').decode('ascii')
        print(f"  {d['code']:7s} | {cn:25s} | class='{cc}' | status='{cs}'")

    # Also check what to_dict() returns for the 'name' key since the JS uses s.name
    print("\n--- Check to_dict() key names ---")
    if students:
        keys = list(students[0].to_dict().keys())
        print(f"  to_dict() keys: {keys}")

    session.close()

if __name__ == '__main__':
    debug()
