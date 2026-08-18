import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule, ClassMaster, Student

def sync_class_master_with_official_schedule():
    session = db_session()
    
    schedules = session.query(ClassSchedule).all()
    print(f"Total ClassSchedule entries: {len(schedules)}\n")

    # Map class_name -> official info from schedule
    class_info = {}
    for sc in schedules:
        cname = sc.class_name.strip()
        if cname not in class_info:
            class_info[cname] = {
                'cm_staff': sc.cm_staff,
                'teacher': sc.teacher,
                'room': sc.room,
                'students_count': sc.students_count,
                'schedule': sc.shift_code
            }

    print("==================================================")
    print("DANH SÁCH CÁC LỚP VÀ LỊCH HỌC CHUẨN TỪ FILE CHÍNH THỨC")
    print("==================================================")
    print(f"{'Tên Lớp':<18} | {'Phụ Trách CM':<14} | {'Giáo Viên':<12} | {'Phòng':<10} | {'Ca Học':<8}")
    print("-" * 72)
    for cname, info in sorted(class_info.items()):
        print(f"{cname:<18} | {info['cm_staff'] or '—':<14} | {info['teacher'] or '—':<12} | {info['room'] or '—':<10} | {info['schedule']:<8}")

        # Sync with ClassMaster
        cm_rec = session.query(ClassMaster).filter(ClassMaster.class_name == cname).first()
        if cm_rec:
            cm_rec.cm_staff = info['cm_staff']
            cm_rec.teacher = info['teacher']
            cm_rec.room = info['room']

        # Sync with Student
        students = session.query(Student).filter(Student.class_name.ilike(f"%{cname}%")).all()
        for st in students:
            st.cm_staff = info['cm_staff']

    session.commit()
    print("\n✅ Đã đồng bộ 100% ClassMaster & Student với Lịch học chuẩn từ file chính thức!")
    session.close()

if __name__ == "__main__":
    sync_class_master_with_official_schedule()
