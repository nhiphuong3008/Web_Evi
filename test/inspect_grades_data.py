import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import UnitGrade, ClassSchedule

session = db_session()

# Check how many grades are in the DB
total = session.query(UnitGrade).count()
print(f"Total UnitGrade records: {total}")

# List all distinct classes in UnitGrade
classes = session.query(UnitGrade.class_name).distinct().order_by(UnitGrade.class_name).all()
print(f"\nDistinct classes in UnitGrade ({len(classes)}):")
for c in classes:
    count = session.query(UnitGrade).filter(UnitGrade.class_name == c[0]).count()
    print(f"  {c[0]}: {count} records")

# List all distinct test names
tests = session.query(UnitGrade.test_name).distinct().order_by(UnitGrade.test_name).all()
print(f"\nDistinct test names ({len(tests)}):")
for t in tests:
    print(f"  {t[0]}")

# Sample some records
print("\nSample records:")
samples = session.query(UnitGrade).limit(5).all()
for s in samples:
    print(f"  {s.student_code} | {s.student_name} | {s.class_name} | {s.test_name} | L:{s.listening} R:{s.reading_writing} S:{s.speaking} T:{s.total_score} | {s.comment[:50] if s.comment else ''}")

# List all active classes in ClassSchedule
active_classes = session.query(ClassSchedule).order_by(ClassSchedule.class_name).all()
print(f"\nAll ClassSchedule entries ({len(active_classes)}):")
for c in active_classes:
    print(f"  {c.class_name}: status={getattr(c, 'status', 'N/A')}")

session.close()
