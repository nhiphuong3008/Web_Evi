import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import Student, ClassSchedule

def fix_data():
    session = db_session()

    # 1. Standardize ClassSchedule name for 'Lp n thi 9-10' -> 'Lớp ôn thi 9-10'
    sc_onthi = session.query(ClassSchedule).filter(
        (ClassSchedule.class_name.ilike("%n thi%")) | (ClassSchedule.class_name.ilike("%9-10%"))
    ).all()
    for sc in sc_onthi:
        sc.class_name = 'Lớp ôn thi 9-10'
    print(f"Updated {len(sc_onthi)} ClassSchedule records to 'Lop on thi 9-10'")

    # 2. Fix Galax 1.3 students
    # EVI122: Khuat Pham Minh Anh -> Galax 1.3 & Lớp ôn thi 9-10
    evi122 = session.query(Student).filter(Student.code == 'EVI122').first()
    if evi122:
        evi411_gram = 'Lớp ôn thi 9-10'
        evi122.class_name = 'Galax 1.3'
        evi122.grammar_class = 'Lớp ôn thi 9-10'
        evi122.status = 'Đang học'
        print("Updated EVI122 => Class='Galax 1.3', Grammar='Lop on thi 9-10'")

    # EVI126: Pham Hoang Ha Phuong -> Remove from Galax 1.3 if not in class
    evi126 = session.query(Student).filter(Student.code == 'EVI126').first()
    if evi126 and 'Galax 1.3' in (evi126.class_name or ''):
        evi126.class_name = 'Lop khac'
        print("Updated EVI126 => Class='Lop khac'")

    # 3. Update all students in Lớp ôn thi 9-10
    onthi_codes = ['EVI122', 'EVI147', 'EVI299', 'EVI393']
    for code in onthi_codes:
        st = session.query(Student).filter(Student.code == code).first()
        if st:
            st.grammar_class = 'Lớp ôn thi 9-10'
            st.status = 'Đang học'
            if code == 'EVI299':
                st.class_name = 'Lớp ôn thi 9-10'
            print(f"Ensured {code} ({st.full_name.encode('ascii','ignore').decode('ascii')}) has grammar_class='Lop on thi 9-10'")

    session.commit()

    # 4. Recount exact student count for all schedules
    all_schedules = session.query(ClassSchedule).all()
    for sc in all_schedules:
        cname = sc.class_name.strip()
        count = session.query(Student).filter(
            (Student.class_name.ilike(f"%{cname}%")) | (Student.grammar_class.ilike(f"%{cname}%")),
            Student.status == 'Đang học'
        ).count()
        sc.students_count = count
        clean_cname = cname.encode('ascii', 'ignore').decode('ascii')
        print(f"  Schedule '{clean_cname:16s}': students_count = {count}")

    session.commit()
    print("\nSUCCESSFULLY FIXED GALAX 1.3 AND LOP ON THI 9-10 DATA!")
    session.close()

if __name__ == '__main__':
    fix_data()
