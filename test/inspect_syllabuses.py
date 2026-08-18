import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import LessonSyllabus

session = db_session()

print("--- Distinct Course Names in LessonSyllabus ---")
courses = session.query(LessonSyllabus.course_name).distinct().all()
for c in courses:
    cnt = session.query(LessonSyllabus).filter(LessonSyllabus.course_name == c[0]).count()
    print(f"Course Name: '{c[0]}' | Count: {cnt}")

print("\n--- Class-Specific Syllabuses ---")
class_sylls = session.query(LessonSyllabus.class_name).filter(LessonSyllabus.class_name.isnot(None)).distinct().all()
for cs in class_sylls:
    cnt = session.query(LessonSyllabus).filter(LessonSyllabus.class_name == cs[0]).count()
    print(f"Class Name: '{cs[0]}' | Count: {cnt}")

session.close()
