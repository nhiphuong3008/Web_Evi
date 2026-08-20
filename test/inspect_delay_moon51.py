import sqlite3
import datetime
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus, ClassScheduleAdjustment
from services.db_service import calculate_real_class_lesson_dates, get_class_lesson_log_db

session = db_session()
cname = 'Moon 5.1'
adj = session.query(ClassScheduleAdjustment).filter(ClassScheduleAdjustment.class_name.ilike(f"%{cname}%")).first()
print("Adjustment in DB:", adj.to_dict() if adj else None)

log_res = get_class_lesson_log_db(cname)
for l in log_res['lessons']:
    if l['buoi'] in range(46, 52):
        print(f"Buoi {l['buoi']}: Date={l['date']} | Status={l['status_label']} (is_delayed={l['is_delayed']})")

session.close()
