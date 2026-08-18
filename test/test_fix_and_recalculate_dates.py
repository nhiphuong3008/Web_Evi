import os, sys, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import LessonSyllabus, ClassSchedule
from services.db_service import get_class_lesson_log_db, calculate_real_class_lesson_dates

session = db_session()

# Fix the 30 typo rows in SQLite
typo_rows = session.query(LessonSyllabus).filter(LessonSyllabus.official_date.isnot(None)).all()
fixed_count = 0

for r in typo_rows:
    od = r.official_date
    if od:
        p = od.split('-') if '-' in od else od.split('/')
        if len(p) == 3:
            y_str = p[0] if len(p[0]) == 4 else p[2]
            try:
                y = int(y_str)
                if y < 2026:
                    # Replace year with 2026
                    if len(p[0]) == 4:
                        new_od = f"2026-{p[1]:>02s}-{p[2]:>02s}"
                    else:
                        new_od = f"{p[0]:>02s}/{p[1]:>02s}/2026"
                    print(f"Fixing ID {r.id:4d} ({r.class_name or r.course_name}): {od} -> {new_od}")
                    r.official_date = new_od
                    fixed_count += 1
            except:
                pass

session.commit()
print(f"Successfully fixed {fixed_count} typo dates in SQLite!")
print("="*100)

# Now test Galax 1.3, Galax 1.4, Galax 1.5, Moon 2.3, Galax 2.1, Sun 2.3
test_classes = ["Galax 1.3", "Galax 1.4", "Galax 1.5", "Moon 2.3", "Galax 2.1", "Sun 2.3"]

for cname in test_classes:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    today_lessons = [l for l in lessons if l.get('status_code') == 'today']
    completed = [l for l in lessons if l.get('status_code') == 'completed']
    pending = [l for l in lessons if l.get('status_code') == 'pending']
    
    last_comp = completed[-1] if completed else None
    first_pend = pending[0] if pending else None
    
    print(f"\n--- {cname} ---")
    if last_comp:
        print(f"  Last Completed: Buổi {last_comp['buoi']:2d} ({last_comp['date']}) | Title: {last_comp['lesson_title']}")
    if first_pend:
        print(f"  First Pending:   Buổi {first_pend['buoi']:2d} ({first_pend['date']}) | Title: {first_pend['lesson_title']}")

session.close()
