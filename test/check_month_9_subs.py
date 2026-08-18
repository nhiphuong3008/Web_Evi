import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_crm_renewal_pipeline_db

def check_m9():
    res = get_crm_renewal_pipeline_db(month=9, year=2026)
    print("--- Month 9/2026 CRM Pipeline ---")
    print("Total due:", res.get('kpi', {}).get('total_due'))
    d30_list = res.get('kanban', {}).get('d30', [])
    print(f"D-30 list count in Month 9/2026: {len(d30_list)}")
    for s in d30_list:
        print(f"  • #{s.get('id')} | Code:{s.get('student_code')} | Name:{s.get('student_name')} | Class:{s.get('class_name')} | Expiry:{s.get('current_end_date')}")

if __name__ == '__main__':
    check_m9()
