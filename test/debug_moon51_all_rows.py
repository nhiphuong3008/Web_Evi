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

lesson_dates, delayed_set = calculate_real_class_lesson_dates(schedules, clean_cname, matched_syllabuses, session)

for idx, (s, d) in enumerate(zip(matched_syllabuses, lesson_dates)):
    print(f"Row {idx+1} (Lesson {s.lesson_num}): DB_official='{s.official_date}' -> CalcDate={d.strftime('%Y-%m-%d')} ({d.strftime('%d/%m')})")

session.close()
