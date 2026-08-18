import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus, ClassScheduleAdjustment
from services.db_service import get_schedule_matrix_db, get_class_lesson_log_db

session = db_session()

print("==========================================")
print("INSPECTING Sun 4.3 AND Sun 3.5 SYLLABUS & SCHEDULE")
print("==========================================")

# 1. Check ClassSchedule entries
for cname in ['Sun 4.3', 'Sun 3.5']:
    cs = session.query(ClassSchedule).filter(ClassSchedule.class_name == cname).first()
    if cs:
        print(f"\nClass: {cs.class_name}")
        print(f"  ID: {cs.id}")
        print(f"  Day: {cs.day} | Shift: {cs.shift_name}")
        print(f"  Teacher: {cs.teacher}")
        print(f"  Room: {cs.room}")
    else:
        print(f"\nClass {cname} NOT found in ClassSchedule!")

# 2. Check Schedule Matrix output for FRI / Today
matrix_res = get_schedule_matrix_db()
print("\n--- Schedule Matrix output for Sun 4.3 and Sun 3.5 ---")
for row in matrix_res.get('matrix', []):
    for shift in row.get('shifts', []):
        for cls in shift.get('classes', []):
            if cls.get('class_name') in ['Sun 4.3', 'Sun 3.5']:
                print(f"Row Day: {row.get('day_name')} | Class: {cls.get('class_name')} | Lesson Num: {cls.get('current_lesson_num')} | Lesson Title: {cls.get('current_lesson_title')}")

# 3. Inspect LessonSyllabus entries and official dates for Sun 4.3 & Sun 3.5
for cname in ['Sun 4.3', 'Sun 3.5']:
    syllabuses = session.query(LessonSyllabus).filter(LessonSyllabus.class_name == cname).order_by(LessonSyllabus.lesson_num).all()
    print(f"\nSyllabus count for {cname}: {len(syllabuses)}")
    if syllabuses:
        print(f"  First lesson: num={syllabuses[0].lesson_num}, official_date={syllabuses[0].official_date}")
        print(f"  Last lesson: num={syllabuses[-1].lesson_num}, official_date={syllabuses[-1].official_date}")
        
        print("  Lessons 48..56:")
        for s in syllabuses:
            if 48 <= s.lesson_num <= 56:
                print(f"    Lesson {s.lesson_num}: official_date={s.official_date}, title={s.lesson_title}")

session.close()
