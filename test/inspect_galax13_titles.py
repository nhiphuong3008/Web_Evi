import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import LessonSyllabus

session = db_session()
rows = session.query(LessonSyllabus).filter(LessonSyllabus.class_name.ilike('%Galax 1.3%')).order_by(LessonSyllabus.lesson_num.asc()).all()

print(f"Total rows for Galax 1.3 in DB: {len(rows)}")
print("="*100)

for r in rows:
    if r.lesson_num in [22, 23, 24, 25, 26, 27, 70, 71, 72, 73] or r.lesson_num <= 5:
        print(f"ID:{r.id:4d} | DB lesson_num:{r.lesson_num:2d} | Title:{r.lesson_title:15s} | Unit:{r.unit_name[:40]}")

session.close()
