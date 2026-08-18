import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import LessonSyllabus

def check():
    session = db_session()
    records = session.query(LessonSyllabus).filter(LessonSyllabus.class_name == 'Moon 5.2').order_by(LessonSyllabus.lesson_num.asc()).all()
    print(f"Exact match 'Moon 5.2' records: {len(records)}")
    for r in records[:10]:
        print(f"  Buoi {r.lesson_num}: Date='{r.official_date}' | Title='{r.lesson_title}' | Unit='{r.unit_name}' | Source='{r.file_source}'")
    session.close()

if __name__ == '__main__':
    check()
