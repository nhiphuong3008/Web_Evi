import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import LessonSyllabus

session = db_session()

# Find all distinct classes in LessonSyllabus
classes = sorted(list(set(s.class_name for s in session.query(LessonSyllabus).filter(LessonSyllabus.class_name.isnot(None)).all())))

print(f"Fixing and harmonizing LESSON titles for all {len(classes)} classes in SQLite...")
print("="*100)

fixed_classes_count = 0
total_rows_fixed = 0

for cname in classes:
    rows = session.query(LessonSyllabus).filter(LessonSyllabus.class_name.ilike(f"%{cname.strip()}%")).order_by(LessonSyllabus.lesson_num.asc()).all()
    
    needs_fix = False
    for idx, r in enumerate(rows):
        expected_title = f"LESSON {r.lesson_num}"
        if r.lesson_title != expected_title:
            needs_fix = True
            r.lesson_title = expected_title
            total_rows_fixed += 1
            
    if needs_fix:
        fixed_classes_count += 1
        print(f"  🔧 Fixed class '{cname}': updated {len(rows)} lesson titles to LESSON 1..{len(rows)}")

session.commit()
print("="*100)
print(f"✅ SUCCESS! Harmonized {total_rows_fixed} lesson title records across {fixed_classes_count} classes.")

# Verify Galax 1.3 rows 23..27
print("\nVerification for Galax 1.3 (Buổi 23 to 27):")
g13_rows = session.query(LessonSyllabus).filter(LessonSyllabus.class_name.ilike('%Galax 1.3%')).order_by(LessonSyllabus.lesson_num.asc()).all()
for r in g13_rows[22:27]:
    print(f"  Buổi {r.lesson_num:2d} | Title: {r.lesson_title:12s} | Date: {r.official_date or '—'} | Unit: {r.unit_name[:40]}")

session.close()
