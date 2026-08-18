import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule, ClassMaster, Student

def fix_unicode():
    session = db_session()
    
    replacements = {
        'Vn Anh': 'Vân Anh',
        'NgcCM': 'NgọcCM',
        'Dyn': 'Duyên',
        'Lp n thi 9-10': 'Lớp ôn thi 9-10',
        'Th 2 (MON)': 'Thứ 2 (MON)',
        'Th 3 (TUE)': 'Thứ 3 (TUE)',
        'Th 4 (WED)': 'Thứ 4 (WED)',
        'Th 5 (THU)': 'Thứ 5 (THU)',
        'Th 6 (FRI)': 'Thứ 6 (FRI)',
        'Th 7 (SAT)': 'Thứ 7 (SAT)'
    }

    schedules = session.query(ClassSchedule).all()
    for sc in schedules:
        if sc.cm_staff in replacements:
            sc.cm_staff = replacements[sc.cm_staff]
        if sc.teacher in replacements:
            sc.teacher = replacements[sc.teacher]
        if sc.ta_staff in replacements:
            sc.ta_staff = replacements[sc.ta_staff]
        if sc.class_name in replacements:
            sc.class_name = replacements[sc.class_name]
        if sc.day in replacements:
            sc.day = replacements[sc.day]

    masters = session.query(ClassMaster).all()
    for cm in masters:
        if cm.cm_staff in replacements:
            cm.cm_staff = replacements[cm.cm_staff]
        if cm.teacher in replacements:
            cm.teacher = replacements[cm.teacher]
        if cm.class_name in replacements:
            cm.class_name = replacements[cm.class_name]

    students = session.query(Student).all()
    for st in students:
        if st.cm_staff in replacements:
            st.cm_staff = replacements[st.cm_staff]

    session.commit()
    print("✅ Đã chuẩn hóa 100% tiếng Việt có dấu cho Lịch học chính thức!")

    # Verify final schedule list
    all_s = session.query(ClassSchedule).order_by(ClassSchedule.day.asc()).all()
    print(f"\nTổng số {len(all_s)} ca học chính thức:")
    print(f"{'Ngày':<12} | {'Ca':<5} | {'Tên Lớp':<16} | {'Phòng':<10} | {'GV':<14} | {'CM':<10} | {'TA':<6}")
    print("-" * 82)
    for s in all_s:
        print(f"{s.day:<12} | {s.shift_code:<5} | {s.class_name:<16} | {s.room or '—':<10} | {s.teacher or '—':<14} | {s.cm_staff or '—':<10} | {s.ta_staff or '—':<6}")

    session.close()

if __name__ == "__main__":
    fix_unicode()
