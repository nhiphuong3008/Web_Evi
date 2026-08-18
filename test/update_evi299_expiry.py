import sys
import os
import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import Student, StudentSubscription, StudentRenewal, ClassSchedule
from services.db_service import calculate_fee_expiry_date

session = db_session()

print("--- Recalculating & Updating Expiry Date for Nguyễn Minh Phong (EVI299) ---")

st = session.query(Student).filter(Student.code == 'EVI299').first()
if st:
    st.class_name = 'Lớp ôn thi 9-10'
    st.schedule = 'W5'  # 1 buổi/tuần vào Thứ 4
    st.remaining_sessions = 8
    
    # Recalculate expiry date from 14/08/2026 for 8 Wednesdays
    new_exp = calculate_fee_expiry_date(8, 'W5', datetime.date(2026, 8, 14))
    print(f"New calculated expiry date: '{new_exp}'")
    
    st.expiry_date = new_exp  # '07/10/2026'
    st.expiry_month = '10'
    st.expiry_year = '2026'
    
    # Synchronize linked StudentSubscription
    sub = session.query(StudentSubscription).filter(StudentSubscription.student_code == 'EVI299').first()
    if sub:
        sub.class_name = 'Lớp ôn thi 9-10'
        sub.current_end_date = new_exp
        sub.original_end_date = new_exp
        sub.remaining_sessions = 8

    # Synchronize linked StudentRenewal
    ren = session.query(StudentRenewal).filter(StudentRenewal.student_code == 'EVI299').first()
    if ren:
        ren.class_name = 'Lớp ôn thi 9-10'
        ren.expected_expiry_date = new_exp
        ren.month = 10
        ren.year = 2026

    # Remove extra Saturday row from ClassSchedule for Lớp ôn thi 9-10 if present
    extra_cs = session.query(ClassSchedule).filter(
        ClassSchedule.class_name.ilike('%ôn thi 9-10%'),
        ClassSchedule.day.ilike('%Thứ 7%')
    ).first()
    if extra_cs:
        print(f"Removing duplicate Saturday ClassSchedule row ID={extra_cs.id}")
        session.delete(extra_cs)

    # Update main Wednesday ClassSchedule shift_code to W5
    main_cs = session.query(ClassSchedule).filter(
        ClassSchedule.class_name.ilike('%ôn thi 9-10%'),
        ClassSchedule.day.ilike('%Thứ 4%')
    ).first()
    if main_cs:
        main_cs.shift_code = 'W5'

    session.commit()
    print("✅ Successfully updated EVI299 and synchronized 100% CSDL SQLite!")

session.close()
