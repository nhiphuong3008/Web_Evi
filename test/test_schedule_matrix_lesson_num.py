import os, sys, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus
from services.db_service import get_class_lesson_log_db

session = db_session()
schedules = session.query(ClassSchedule).all()

print(f"Total schedule entries: {len(schedules)}")
print("="*80)

# Build cache of class_name -> current_lesson info
class_names = set(s.class_name for s in schedules)
lesson_info_map = {}

for cname in class_names:
    log_res = get_class_lesson_log_db(cname)
    lessons = log_res.get('lessons', [])
    
    current_buoi = None
    if lessons:
        # Find 'today' lesson or latest completed
        today_lessons = [l for l in lessons if l.get('status_code') == 'today']
        completed = [l for l in lessons if l.get('status_code') == 'completed']
        
        if today_lessons:
            current_buoi = today_lessons[-1].get('buoi')
        elif completed:
            current_buoi = completed[-1].get('buoi')
        else:
            current_buoi = lessons[0].get('buoi')
            
    lesson_info_map[cname] = {
        'buoi': current_buoi,
        'total': len(lessons)
    }

for s in schedules:
    info = lesson_info_map.get(s.class_name, {})
    buoi = info.get('buoi')
    total = info.get('total')
    display_str = f"Buổi {buoi}" if buoi else "Syllabus"
    print(f"ID:{s.id:2d} | Day:{s.day:12s} | Class:{s.class_name:12s} | Buổi hiện tại: {display_str:10s} (Tổng: {total} buổi)")

session.close()
