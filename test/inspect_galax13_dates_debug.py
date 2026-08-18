import os, sys, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus
from services.db_service import calculate_real_class_lesson_dates, get_class_lesson_log_db

session = db_session()

# Check Galax 1.3 syllabus rows in DB
rows = session.query(LessonSyllabus).filter(LessonSyllabus.class_name.ilike('%Galax 1.3%')).order_by(LessonSyllabus.lesson_num.asc()).all()
print(f"Galax 1.3 explicit syllabus rows in DB: {len(rows)}")
for r in rows[:5]:
    print(f"  Lesson {r.lesson_num} | Date: {r.official_date} | Source: {r.file_source} | Title: {r.lesson_title}")
if len(rows) > 5:
    print("  ...")
    for r in rows[-3:]:
        print(f"  Lesson {r.lesson_num} | Date: {r.official_date} | Source: {r.file_source} | Title: {r.lesson_title}")

# Test full log
res = get_class_lesson_log_db("Galax 1.3")
lessons = res.get('lessons', [])
print(f"\nTotal lessons calculated: {len(lessons)}")
print(f"Today is: {datetime.date.today().strftime('%d/%m/%Y')}")

for l in lessons:
    if l['buoi'] in [1, 2, 3, 35, 36, 37, 70, 71, 72, 73]:
        print(f"  Lesson {l['buoi']:2d} | Date: {l['date']} | Status: {l['status_code']:10s} | Label: {l['status_label']}")

session.close()
