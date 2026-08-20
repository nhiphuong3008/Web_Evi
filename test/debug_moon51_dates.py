import sqlite3
import datetime
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus
from services.db_service import calculate_real_class_lesson_dates

session = db_session()
class_name = 'Moon 5.1'
clean_cname = class_name.strip()
schedules = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{clean_cname}%")).all()
matched_syllabuses = session.query(LessonSyllabus).filter(
    LessonSyllabus.class_name.ilike(f"%{clean_cname}%")
).order_by(LessonSyllabus.lesson_num.asc()).all()

print(f"Total matched: {len(matched_syllabuses)}")
for s in matched_syllabuses:
    if s.lesson_num in range(40, 52):
        print(f"DB Row - Lesson {s.lesson_num}: official_date='{s.official_date}'")

lesson_dates, delayed_set = calculate_real_class_lesson_dates(schedules, clean_cname, matched_syllabuses, session)

print("\nResulting lesson_dates:")
for idx, d in enumerate(lesson_dates):
    buoi = matched_syllabuses[idx].lesson_num if idx < len(matched_syllabuses) else idx + 1
    if buoi in range(40, 52):
        print(f"Lesson {buoi}: Calculated Date = {d.strftime('%Y-%m-%d')} ({d.strftime('%d/%m')})")

session.close()
