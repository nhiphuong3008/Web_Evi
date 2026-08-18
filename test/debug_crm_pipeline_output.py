import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_crm_renewal_pipeline_db

def test_pipeline():
    print("--- DEBUG CRM PIPELINE OUTPUT FOR MONTH 8/2026 ---")
    res = get_crm_renewal_pipeline_db(month=8, year=2026)
    print("kpi:", res.get('kpi'))
    print("cm_leaderboard:")
    for cm in res.get('cm_leaderboard', []):
        print("  ", cm)

if __name__ == '__main__':
    test_pipeline()
