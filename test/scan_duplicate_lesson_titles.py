import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import LessonSyllabus, ClassSchedule

session = db_session()

# Find all distinct classes in LessonSyllabus
classes = sorted(list(set(s.class_name for s in session.query(LessonSyllabus).filter(LessonSyllabus.class_name.isnot(None)).all())))

print(f"Scanning {len(classes)} classes for duplicate or misaligned LESSON titles in CSDL...")
print("="*100)

corrupted_classes = []

for cname in classes:
    rows = session.query(LessonSyllabus).filter(LessonSyllabus.class_name.ilike(f"%{cname.strip()}%")).order_by(LessonSyllabus.lesson_num.asc()).all()
    
    titles = [r.lesson_title for r in rows if r.lesson_title]
    
    # Check for duplicate titles (e.g. two LESSON 24)
    seen = set()
    dupes = []
    for idx, t in enumerate(titles):
        t_clean = t.strip().upper()
        if t_clean in seen:
            dupes.append((idx + 1, t_clean))
        else:
            seen.add(t_clean)
            
    # Check if lesson_title matches lesson_num (e.g., Buổi 25 has LESSON 24)
    mismatches = []
    for r in rows:
        import re
        m = re.search(r'LESSON\s*(\d+)', r.lesson_title.upper()) if r.lesson_title else None
        if m:
            t_num = int(m.group(1))
            if t_num != r.lesson_num:
                mismatches.append((r.lesson_num, r.lesson_title))
                
    if dupes or mismatches:
        corrupted_classes.append((cname, len(rows), dupes, len(mismatches)))
        print(f"❌ {cname:20s} | Total Rows: {len(rows):2d} | Duplicates: {len(dupes)} {dupes} | Mismatches: {len(mismatches)}")
    else:
        print(f"✅ {cname:20s} | Total Rows: {len(rows):2d} | Perfect sequence 1..{len(rows)}!")

session.close()
