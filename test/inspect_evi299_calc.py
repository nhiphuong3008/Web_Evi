import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import Student, StudentSubscription, StudentRenewal
from services.db_service import calculate_fee_expiry_date

session = db_session()

st = session.query(Student).filter(Student.code == 'EVI299').first()

print("--- Testing calculate_fee_expiry_date for EVI299 ---")
res = calculate_fee_expiry_date(st.class_name, st.schedule, st.remaining_sessions)
print(f"calculate_fee_expiry_date return: {res}")

session.close()
