import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import ClassMaster, ClassSchedule, Student
from services.db_service import get_cm_classes_db, get_dashboard_summary

session = db_session()

print("--- ClassMaster table count ---")
cm_count = session.query(ClassMaster).filter(ClassMaster.status == 'Đang hoạt động').count()
print(f"ClassMaster 'Đang hoạt động' count: {cm_count}")

print("\n--- get_cm_classes_db(include_ended=False) count ---")
res_classes = get_cm_classes_db(include_ended=False)
if res_classes.get('success'):
    classes = res_classes.get('data', [])
    print(f"Total active classes from get_cm_classes_db: {len(classes)}")
    for c in classes[:5]:
        print(f"  Class: {c.get('class_name')} | Status: {c.get('status')} | CM: {c.get('cm_staff')}")

print("\n--- ClassSchedule table count ---")
cs_count = session.query(ClassSchedule).filter(ClassSchedule.status != 'Đã kết thúc').count()
print(f"ClassSchedule non-ended count: {cs_count}")

print("\n--- get_dashboard_summary KPI ---")
dash = get_dashboard_summary()
print("Dashboard KPI:", dash.get('kpi'))

session.close()
