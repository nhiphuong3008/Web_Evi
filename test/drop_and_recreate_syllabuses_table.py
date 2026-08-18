import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session, engine
from database.models import LessonSyllabus, Base

def recreate_table():
    LessonSyllabus.__table__.drop(engine, checkfirst=True)
    LessonSyllabus.__table__.create(engine, checkfirst=True)
    print("Successfully recreated lesson_syllabuses table with class_name & official_date columns!")

if __name__ == '__main__':
    recreate_table()
