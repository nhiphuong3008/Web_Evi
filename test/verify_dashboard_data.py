import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_dashboard_summary, get_renewals_db, get_cm_classes_db

def run_tests():
    print("=== RUNNING DASHBOARD DATA VERIFICATION ===")

    # 1. Test get_dashboard_summary
    dash = get_dashboard_summary()
    assert dash.get('kpi') is not None, "KPI data is missing"
    assert dash.get('acs_stats') is not None, "ACS stats is missing"
    assert 'staff' in dash['acs_stats'], "ACS stats missing 'staff' array"
    assert len(dash['acs_stats']['staff']) > 0, "ACS staff array is empty"
    print("[TEST 1] ACS Stats with 'staff' key: PASS!")

    # 2. Test classes student_count & students keys
    classes = dash.get('classes', [])
    assert len(classes) > 0, "Classes data is empty"
    sample_cls = classes[0]
    assert 'students' in sample_cls, "Class missing 'students' property"
    assert 'student_count' in sample_cls, "Class missing 'student_count' property"
    print(f"[TEST 2] Classes student count property ({sample_cls['class_name']}: {sample_cls['students']} HS): PASS!")

    # 3. Test renewal_monthly entries count
    renewal_monthly = dash.get('renewal_monthly', [])
    print(f"[TEST 3] Monthly renewals count: {len(renewal_monthly)} months returned")
    assert len(renewal_monthly) >= 5, f"Expected at least 5 months with renewals, found {len(renewal_monthly)}"
    print("  -> PASS!")

    # 4. Test get_renewals_db available_months
    ren_res = get_renewals_db()
    assert ren_res.get('success') is True, f"get_renewals_db failed: {ren_res.get('error')}"
    avail_m = ren_res.get('available_months', [])
    print(f"[TEST 4] get_renewals_db available_months count: {len(avail_m)}")
    assert len(avail_m) >= 5, f"Expected available_months >= 5, found {len(avail_m)}"
    print("  -> PASS!")

    print("\nALL 4 DASHBOARD DATA VERIFICATION TESTS PASSED 100%! 🚀")

if __name__ == '__main__':
    run_tests()
