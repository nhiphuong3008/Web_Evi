import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_dashboard_summary, get_cm_classes_db

dash = get_dashboard_summary()
kpi = dash.get('kpi', {})
classes = dash.get('classes', [])

print(f"Active classes count in KPI: {kpi.get('active_classes')}")
print(f"Total classes count in KPI: {kpi.get('total_classes')}")
print(f"Classes list length in Dashboard: {len(classes)}")

class_names = [c['class_name'] for c in classes]
print("\nDashboard Classes List (20 classes):")
print(sorted(class_names))

assert len(classes) == 20, f"Expected 20 classes, got {len(classes)}"
assert kpi.get('active_classes') == 20, f"Expected active_classes=20, got {kpi.get('active_classes')}"
assert kpi.get('total_classes') == 20, f"Expected total_classes=20, got {kpi.get('total_classes')}"

print("\nALL TESTS PASSED PERFECTLY! 🚀")
