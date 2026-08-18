import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import Student, StudentSubscription, StudentRenewal
from services.db_service import calculate_fee_expiry_date, get_student_detail_db

session = db_session()

st = session.query(Student).filter(Student.code == 'EVI299').first()
if st:
    print("--- Student EVI299 Record ---")
    print(f"Code: {st.code}")
    print(f"Name: {st.full_name}")
    print(f"Class Name: '{st.class_name}'")
    print(f"Schedule: '{st.schedule}'")
    print(f"Total Sessions: {st.total_sessions}")
    print(f"Remaining Sessions: {st.remaining_sessions}")
    print(f"Expiry Date in DB: '{st.expiry_date}'")
    print(f"Expiry Month in DB: '{st.expiry_month}'")
    print(f"Expiry Year in DB: '{st.expiry_year}'")
    print(f"Fee Package 1: '{st.fee_package_1}'")

    print("\n--- Testing calculate_fee_expiry_date for EVI299 ---")
    # Test calculate_fee_expiry_date with class_name, schedule, remaining_sessions
    exp_date, exp_m, exp_y = calculate_fee_expiry_date(st.class_name, st.schedule, st.remaining_sessions)
    print(f"Calculated Expiry Date: '{exp_date}' | Month: '{exp_m}' | Year: '{exp_y}'")

session.close()
