import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session, init_db
from database.models import Student, UnitGrade, ParentInteractionLog, ClassFeedbackLog
from database.migrate_sheets_to_db import run_migration

def check_evi056_in_db():
    print("Running migration...")
    run_migration()

    session = db_session()
    st = session.query(Student).filter(Student.code == 'EVI056').first()
    print(f"\nStudent EVI056: {st.full_name} ({st.english_name})")

    grades = session.query(UnitGrade).filter(or_(
        UnitGrade.student_code == 'EVI056',
        UnitGrade.student_name.ilike('%Nguyễn Ngọc Huyền%')
    )).all() if hasattr(UnitGrade, 'student_code') else []

    grades = session.query(UnitGrade).filter(UnitGrade.student_code == 'EVI056').all()
    print(f"Total UnitGrade records for EVI056 in SQLite DB: {len(grades)}")
    for g in grades:
        print(f"  - [{g.class_name}] {g.test_name}: L={g.listening}, RW={g.reading_writing}, S={g.speaking}, Tot={g.total_score} | Comment: {g.comment}")

if __name__ == '__main__':
    check_evi056_in_db()
