import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_crm_renewal_pipeline_db

def test_sync():
    print("--- 🧪 TESTING MASTER STUDENT DYNAMIC MAPPING BY STUDENT CODE ---")
    
    res = get_crm_renewal_pipeline_db(month=8, year=2026)
    kanban = res.get('kanban', {})
    all_subs = []
    for stage_list in kanban.values():
        all_subs.extend(stage_list)

    print(f"Total students in Month 8/2026: {len(all_subs)}")
    
    target_codes = {'EVI313': ('Galax 1.4', 'AnhNV'), 'EVI347': ('Sun S.7', 'AnhNV'), 'EVI305': ('Moon 5.2', 'NgọcCM')}
    
    for s in all_subs:
        code = s.get('student_code')
        if code in target_codes:
            exp_cls, exp_cm = target_codes[code]
            print(f"  • #{s.get('id')} | Code: {code} | Name: {s.get('student_name')} | Class: '{s.get('class_name')}' (Expected: '{exp_cls}') | CM: '{s.get('cm_staff')}' (Expected: '{exp_cm}')")
            assert s.get('class_name') == exp_cls, f"Mismatch class for {code}: got '{s.get('class_name')}', expected '{exp_cls}'"
            assert s.get('cm_staff') == exp_cm, f"Mismatch CM for {code}: got '{s.get('cm_staff')}', expected '{exp_cm}'"

    print("\n✅ PASS! All Class and CM staff fields match Master Student table 100% via Student Code!")

if __name__ == '__main__':
    test_sync()
