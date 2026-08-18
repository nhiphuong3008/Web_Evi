import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import StudentRenewal, RenewalDetailLog

def inspect():
    session = db_session()
    
    print("--- 1. student_renewals (Current DB table powering Web UI) for Month 8/2026 ---")
    st_ren = session.query(StudentRenewal).filter(StudentRenewal.month == 8, StudentRenewal.year == 2026).all()
    print(f"Total count in student_renewals: {len(st_ren)}")
    for r in st_ren:
        print(f"  ID:{r.id} | Code:{r.student_code} | Name:{r.student_name} | Class:{r.class_name} | Expiry:{r.expected_expiry_date} | Status:{r.status}")

    print("\n--- 2. renewal_detail_logs (Raw imports from Google Sheets) for Month 8/2026 ---")
    detail_logs = session.query(RenewalDetailLog).filter(RenewalDetailLog.expiry_month == '8', RenewalDetailLog.expiry_year == '2026').all()
    print(f"Total count in renewal_detail_logs: {len(detail_logs)}")
    for d in detail_logs:
        print(f"  ID:{d.id} | Code:{d.student_code} | Name:{d.student_name} | Class:{d.class_name} | Tab:{d.source_tab} | Status:{d.renewal_status} | Expiry:{d.expiry_date}")

    session.close()

if __name__ == '__main__':
    inspect()
