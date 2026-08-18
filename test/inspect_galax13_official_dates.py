import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import LessonSyllabus

session = db_session()

rows = session.query(LessonSyllabus).filter(LessonSyllabus.class_name.ilike('%Galax 1.3%')).all()
print(f"Total LessonSyllabus rows for Galax 1.3: {len(rows)}")

rows_with_dates = [r for r in rows if r.official_date]
print(f"Rows with official_date: {len(rows_with_dates)}")
for r in rows_with_dates:
    print(f"  Lesson {r.lesson_num:2d} | Date: {r.official_date:12s} | File: {r.file_source} | Title: {r.lesson_title}")

session.close()
