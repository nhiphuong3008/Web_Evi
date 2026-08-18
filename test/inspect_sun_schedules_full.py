import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus
from services.db_service import get_class_lesson_log_db

session = db_session()

print("--- ClassSchedule entries for Sun 4.3 & Sun 3.5 ---")
for cname in ['Sun 4.3', 'Sun 3.5']:
    schedules = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{cname}%")).all()
    print(f"\nClass '{cname}' schedules ({len(schedules)} rows):")
    for s in schedules:
        print(f"  ID={s.id} | day='{s.day}' | shift_code='{s.shift_code}' | shift_name='{s.shift_name}' | room='{s.room}'")

print("\n--- get_class_lesson_log_db output ---")
for cname in ['Sun 4.3', 'Sun 3.5']:
    log_res = get_class_lesson_log_db(cname)
    lessons = log_res.get('lessons', [])
    print(f"\nClass '{cname}' total lessons generated: {len(lessons)}")
    # Find lessons with status 'today' or around 2026-08-14
    for l in lessons:
        b_num = l.get('buoi')
        if 48 <= b_num <= 56:
            print(f"  Buổi {b_num}: date={l.get('date')} | status={l.get('status_code')} | title={l.get('lesson_title')}")

session.close()
