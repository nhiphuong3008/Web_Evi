import os, sys, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus
from services.db_service import get_class_lesson_log_db

session = db_session()

# Find all distinct classes in ClassSchedule and LessonSyllabus
schedule_classes = sorted(list(set(s.class_name for s in session.query(ClassSchedule).all())))
syllabus_classes = sorted(list(set(s.class_name for s in session.query(LessonSyllabus).filter(LessonSyllabus.class_name.isnot(None)).all())))

all_classes = sorted(list(set(schedule_classes + syllabus_classes)))

print(f"Total classes to audit: {len(all_classes)}")
print("="*120)

today = datetime.date.today()
print(f"Today's date: {today.strftime('%Y-%m-%d')}")
print("="*120)

issues_found = []

for cname in all_classes:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    
    if not lessons:
        print(f"⚠️ {cname:20s} | NO LESSONS FOUND!")
        continue
        
    # Check if there are date anomalies (e.g., years in 2024/2025, or non-monotonic dates, or completed status far in future/past)
    syl_rows = session.query(LessonSyllabus).filter(LessonSyllabus.class_name.ilike(f"%{cname}%")).all()
    off_dates = [r.official_date for r in syl_rows if r.official_date]
    years_in_db = set()
    for od in off_dates:
        p = od.split('-') if '-' in od else od.split('/')
        if len(p) == 3:
            y = int(p[0]) if len(p[0]) == 4 else int(p[2])
            years_in_db.add(y)
            
    # Find current lesson according to status
    today_lessons = [l for l in lessons if l.get('status_code') == 'today']
    completed = [l for l in lessons if l.get('status_code') == 'completed']
    pending = [l for l in lessons if l.get('status_code') == 'pending']
    
    last_comp_buoi = completed[-1]['buoi'] if completed else None
    last_comp_date = completed[-1]['date'] if completed else None
    
    first_pend_buoi = pending[0]['buoi'] if pending else None
    first_pend_date = pending[0]['date'] if pending else None
    
    # Check for date jumps or year 2025 issues
    has_issue = False
    notes = []
    
    if years_in_db and any(y < 2026 for y in years_in_db):
        has_issue = True
        notes.append(f"DB has past years {sorted(list(years_in_db))}")
        
    # Check if last completed lesson is unexpectedly high or at the end of course
    if last_comp_buoi and last_comp_buoi > len(lessons) - 5 and len(lessons) > 24:
        has_issue = True
        notes.append(f"Auto-positioned at Buổi {last_comp_buoi}/{len(lessons)} (End of level)")
        
    status_icon = "❌" if has_issue else "✅"
    print(f"{status_icon} {cname:20s} | Total: {len(lessons):2d} | Last Completed: Buổi {str(last_comp_buoi):4s} ({last_comp_date or '—'}) | First Pending: Buổi {str(first_pend_buoi):4s} ({first_pend_date or '—'}) | Notes: {', '.join(notes)}")
    
    if has_issue:
        issues_found.append((cname, notes, lessons))

session.close()
