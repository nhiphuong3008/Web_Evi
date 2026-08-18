import os, sys, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus

session = db_session()

# Find all LessonSyllabus rows where official_date has year 2024 or 2025
rows = session.query(LessonSyllabus).filter(LessonSyllabus.official_date.isnot(None)).all()
typo_count = 0

print("Scanning LessonSyllabus rows for year anomalies (< 2026)...")
print("="*80)

for r in rows:
    p = r.official_date.split('-') if '-' in r.official_date else r.official_date.split('/')
    if len(p) == 3:
        y = int(p[0]) if len(p[0]) == 4 else int(p[2])
        if y < 2026:
            typo_count += 1
            print(f"ID:{r.id:4d} | Class:{r.class_name or r.course_name:12s} | Lesson:{r.lesson_num:2d} | Old Date:{r.official_date:12s} | File:{r.file_source}")

print("="*80)
print(f"Total typo date rows found: {typo_count}")

session.close()
