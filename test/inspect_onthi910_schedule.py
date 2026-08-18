import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import Student, ClassSchedule
from services.db_service import calculate_fee_expiry_date

session = db_session()

print("--- ClassSchedule for 'Lớp ôn thi 9-10' ---")
cs_list = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike('%ôn thi 9-10%')).all()
for cs in cs_list:
    print(f"ID={cs.id} | class_name='{cs.class_name}' | day='{cs.day}' | shift_code='{cs.shift_code}' | shift_name='{cs.shift_name}'")

print("\n--- Student EVI299 record ---")
st = session.query(Student).filter(Student.code == 'EVI299').first()
if st:
    print(f"Code: {st.code} | Name: {st.full_name} | Class: '{st.class_name}' | Schedule: '{st.schedule}' | Rem: {st.remaining_sessions}")
    print(f"Current DB expiry_date: '{st.expiry_date}' (Month {st.expiry_month})")

session.close()
