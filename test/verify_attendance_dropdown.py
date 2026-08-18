import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_cm_classes_db, get_dashboard_summary

classes_res = get_cm_classes_db(include_ended=False)
classes_list = classes_res.get('data', [])

print(f"Total active classes returned by get_cm_classes_db: {len(classes_list)}")
print("Class names:")
for c in classes_list:
    print(f"  - {c['class_name']} (Schedule: {c['schedule']}, CM: {c.get('cm_staff')})")

class_names = [c['class_name'] for c in classes_list]
assert 'Khóa Debate 2026' in class_names, "Khóa Debate 2026 missing from dropdown!"
assert 'Khóa Speaking 2026' in class_names, "Khóa Speaking 2026 missing from dropdown!"
assert 'Sun 5.1' not in class_names, "Ended class Sun 5.1 must NOT be in active dropdown!"

dash = get_dashboard_summary()
kpi = dash.get('kpi', {})
print(f"\nDashboard KPI Active Classes: {kpi.get('active_classes')}")

print("\nALL VERIFICATION TESTS PASSED 100%! 🚀")
