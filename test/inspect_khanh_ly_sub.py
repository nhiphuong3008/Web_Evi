import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import StudentSubscription, StudentRenewal

def check():
    session = db_session()
    print("--- Checking Bùi Khánh Ly (EVI241) ---")
    subs = session.query(StudentSubscription).filter(StudentSubscription.student_code == 'EVI241').all()
    print("Subscriptions for EVI241:")
    for s in subs:
        print(f"  ID:{s.id} | Name:{s.student_name} | Orig:{s.original_end_date} | Cur:{s.current_end_date} | Stage:{s.pipeline_stage} | Status:{s.renewal_status}")

    ren = session.query(StudentRenewal).filter(StudentRenewal.student_code == 'EVI241').all()
    print("\nStudentRenewals for EVI241:")
    for r in ren:
        print(f"  ID:{r.id} | Month:{r.month}/{r.year} | Expiry:{r.expected_expiry_date} | Status:{r.status}")

    session.close()

if __name__ == '__main__':
    check()
