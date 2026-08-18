import os
import sys
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_cm_classes_db

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

# 1. Classes in ClassSchedule (Official 20 classes)
c.execute("SELECT DISTINCT class_name FROM class_schedules WHERE section = 'Chính thức'")
schedule_classes = set(r[0].strip() for r in c.fetchall() if r[0])
print(f"Official classes in ClassSchedule ({len(schedule_classes)} classes):")
print(sorted(list(schedule_classes)))

# 2. Classes returned by get_cm_classes_db() (23 classes)
cm_classes_res = get_cm_classes_db(include_ended=False)
cm_classes = cm_classes_res.get('data', [])
cm_class_names = set(c['class_name'] for c in cm_classes)

print(f"\nClasses in get_cm_classes_db() ({len(cm_class_names)} classes):")
print(sorted(list(cm_class_names)))

# 3. Find the 3 extra classes!
extra_classes = cm_class_names - schedule_classes
print(f"\nEXTRA 3 CLASSES ({len(extra_classes)}):")
for ec in sorted(list(extra_classes)):
    # Check origin in ClassMaster or Student table
    c.execute("SELECT class_name, teacher, cm_staff FROM classes WHERE LOWER(TRIM(class_name)) = LOWER(TRIM(?))", (ec,))
    cm_row = c.fetchone()
    c.execute("SELECT COUNT(*) FROM students WHERE (class_name LIKE ? OR grammar_class LIKE ?) AND status = 'Đang học'", (f"%{ec}%", f"%{ec}%"))
    st_cnt = c.fetchone()[0]
    print(f"  - '{ec}': ClassMaster = {cm_row}, Active Students in DB = {st_cnt}")

conn.close()
