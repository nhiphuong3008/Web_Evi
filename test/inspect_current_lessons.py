import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_class_lesson_log_db

test_classes = ["Galax 1.3", "Moon 5.2", "GALAX 3.2", "Sun 2.4", "Sun 4.2", "Moon 1.1"]

for cname in test_classes:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    today_lesson = None
    completed_lessons = [l for l in lessons if l.get('status_code') in ['completed', 'today']]
    if completed_lessons:
        today_lesson = completed_lessons[-1]
    elif lessons:
        today_lesson = lessons[0]
    
    buoi_num = today_lesson.get('buoi') if today_lesson else '?'
    title = today_lesson.get('lesson_title') if today_lesson else 'Syllabus'
    unit = today_lesson.get('unit_name') if today_lesson else ''
    date_str = today_lesson.get('date') if today_lesson else ''
    
    print(f"Class: {cname:12s} | Buổi hiện tại: {buoi_num:2} | Title: {title} | Unit: {unit[:30]} | Date: {date_str}")
