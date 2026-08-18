import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_crm_renewal_pipeline_db

def test_active_only():
    print("--- 🧪 TESTING CRM PIPELINE ACTIVE STUDENTS FILTER ---")
    
    # Month 9/2026
    res = get_crm_renewal_pipeline_db(month=9, year=2026)
    kpi = res.get('kpi', {})
    kanban = res.get('kanban', {})
    print("Month 9/2026 total due:", kpi.get('total_due'))
    
    all_due = []
    for stage_list in kanban.values():
        all_due.extend(stage_list)

    print(f"Total active due students in Month 9/2026: {len(all_due)}")
    inactive_found = []
    for st in all_due:
        cls = st.get('class_name', '').strip()
        print(f"  • #{st.get('id')} | {st.get('student_code')} | {st.get('student_name')} | Class: '{cls}' | Stage: {st.get('pipeline_stage')}")
        if cls in ['Bảo lưu', 'Đã nghỉ', 'Nghỉ học', '—', '']:
            inactive_found.append(st)

    assert len(inactive_found) == 0, f"Found inactive students in active pipeline: {inactive_found}"
    print("\n✅ PASS! No inactive/Bảo lưu students in active Renewal Pipeline!")

if __name__ == '__main__':
    test_active_only()
