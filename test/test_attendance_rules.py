import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import Student
from services.db_service import save_attendance_db

def test_rules():
    session = db_session()
    
    # Create test student EVI048 status check
    st = session.query(Student).filter(Student.code == 'EVI048').first()
    if not st:
        print("Test student EVI048 not found")
        return

    init_rem = st.remaining_sessions or 24
    st.remaining_sessions = init_rem
    session.commit()

    print(f"Initial remaining sessions for EVI048: {st.remaining_sessions}")

    # Test 1: 'Có mặt' -> should deduct 1
    save_attendance_db('Galax 1.3', '2026-08-01', [{'student_code': 'EVI048', 'student_name': st.full_name, 'status': 'Có mặt'}])
    session.refresh(st)
    print(f"  After 'Co mat': remaining = {st.remaining_sessions} (Deducted 1)")

    # Test 2: 'Vắng có phép' -> should NOT deduct
    rem_before = st.remaining_sessions
    save_attendance_db('Galax 1.3', '2026-08-02', [{'student_code': 'EVI048', 'student_name': st.full_name, 'status': 'Vắng có phép'}])
    session.refresh(st)
    print(f"  After 'Vang co phep': remaining = {st.remaining_sessions} (Kept {rem_before})")

    # Test 3: 'Vắng không phép' -> should deduct 1
    rem_before = st.remaining_sessions
    save_attendance_db('Galax 1.3', '2026-08-03', [{'student_code': 'EVI048', 'student_name': st.full_name, 'status': 'Vắng không phép'}])
    session.refresh(st)
    print(f"  After 'Vang khong phep': remaining = {st.remaining_sessions} (Deducted 1)")

    # Test 4: 'Lý do khác' -> should NOT deduct
    rem_before = st.remaining_sessions
    save_attendance_db('Galax 1.3', '2026-08-04', [{'student_code': 'EVI048', 'student_name': st.full_name, 'status': 'Lý do khác'}])
    session.refresh(st)
    print(f"  After 'Ly do khac': remaining = {st.remaining_sessions} (Kept {rem_before})")

    session.close()

if __name__ == '__main__':
    test_rules()
