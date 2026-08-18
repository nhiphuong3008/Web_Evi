import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassMaster, ClassSchedule, Student, User

def main():
    session = db_session()

    # Define class assignments for all 9 CM Users
    cm_assignments = {
        'Thục Anh': ['Galax 1.3', 'Galax 1.4', 'Galax 1.5'],
        'Amber': ['Sun 2.2', 'Sun 2.4', 'Sun 3.5'],
        'Naomi': ['Sun 4.2', 'Sun 4.3', 'Sun 4.4'],
        'Ms. Lan': ['Moon 1.1', 'Moon 3.1', 'Moon 5.1'],
        'Vân Anh': ['Galax 3.1', 'Khóa Debate 2026', 'Khóa Speaking 2026'],
        'AnhPTT': ['GALAX 3.2', 'Sun 1.6', 'Sun 2.1'],
        'NgọcCM': ['Moon 5.2', 'Sun 1.4', 'Lớp ôn thi 9-10'],
        'Giang': ['Sun S.7', 'Sun 6.2'],
        'Duyên': ['Sun 5.1', 'GALAX 2.2']
    }

    print("==================================================")
    print("CẬP NHẬT PHÂN CÔNG LỚP CHO TẤT CẢ 9 CM USERS TRONG CSDL")
    print("==================================================")

    for cm_name, class_list in cm_assignments.items():
        for cname in class_list:
            # 1. Update or create ClassMaster
            cm_rec = session.query(ClassMaster).filter(ClassMaster.class_name.ilike(f"%{cname}%")).first()
            if not cm_rec:
                cm_rec = ClassMaster(
                    class_name=cname,
                    cm_staff=cm_name,
                    status='Đang hoạt động'
                )
                session.add(cm_rec)
            else:
                cm_rec.cm_staff = cm_name

            # 2. Update ClassSchedule
            schedules = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{cname}%")).all()
            for sc in schedules:
                sc.cm_staff = cm_name

            # 3. Update Students in class
            students = session.query(Student).filter(Student.class_name.ilike(f"%{cname}%")).all()
            for st in students:
                st.cm_staff = cm_name

    session.commit()
    print("✅ Đã cập nhật phân công lớp thành công cho cả 9 CM Users!\n")

    # Verify results
    users = session.query(User).filter(User.role == 'cm').all()
    for u in users:
        cm_name = u.cm_staff_name
        schedules = session.query(ClassSchedule).filter(ClassSchedule.cm_staff == cm_name).all()
        assigned_classes = sorted(list(set(s.class_name for s in schedules)))
        print(f"👤 User CM: {u.full_name:<15} ({u.username:<12}) | Phụ trách {len(assigned_classes)} lớp: {', '.join(assigned_classes)}")

    session.close()

if __name__ == "__main__":
    main()
