"""Verification script for grades sync and active class filtering."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import UnitGrade, ClassSchedule, Student

session = db_session()

print("=" * 80)
print("🔍 KIỂM TRA DỮ LIỆU SAU ĐỒNG BỘ")
print("=" * 80)

# 1. Total records
total = session.query(UnitGrade).count()
print(f"\n📊 Tổng bản ghi unit_grades: {total}")

# 2. Active classes from class_schedules
active_schedule = set()
for c in session.query(ClassSchedule.class_name).distinct().all():
    if c[0]:
        active_schedule.add(c[0])
print(f"\n🟢 Lớp đang hoạt động (class_schedules): {len(active_schedule)}")
for c in sorted(active_schedule):
    count = session.query(UnitGrade).filter(UnitGrade.class_name == c).count()
    print(f"   {c:20s}: {count} bản ghi điểm")

# 3. Archived classes
all_grade_classes = set(c[0] for c in session.query(UnitGrade.class_name).distinct().all() if c[0])
archived = all_grade_classes - active_schedule
print(f"\n📁 Lớp cũ (không có trong class_schedules): {len(archived)}")
for c in sorted(archived)[:15]:
    count = session.query(UnitGrade).filter(UnitGrade.class_name == c).count()
    print(f"   {c:20s}: {count} bản ghi điểm")
if len(archived) > 15:
    print(f"   ... và {len(archived) - 15} lớp nữa")

# 4. Check new data with comments
print("\n📝 Mẫu dữ liệu mới (có nhận xét):")
samples = session.query(UnitGrade).filter(
    UnitGrade.comment.isnot(None),
    UnitGrade.comment != '',
    UnitGrade.class_name.in_(list(active_schedule))
).limit(3).all()
for s in samples:
    print(f"   {s.student_code} | {s.student_name} | {s.class_name} | {s.test_name}")
    print(f"   L:{s.listening} R:{s.reading_writing} S:{s.speaking} T:{s.total_score}")
    print(f"   📝 {s.comment[:100]}...")
    print()

# 5. Test get_grades_db function
print("=" * 80)
print("🧪 Test get_grades_db(active_only=True):")
from services.db_service import get_grades_db
result = get_grades_db(active_only=True)
print(f"   Success: {result['success']}")
print(f"   Total records: {result['count']}")
print(f"   Active classes ({len(result['active_classes'])}): {result['active_classes']}")
print(f"   Archived classes ({len(result['archived_classes'])}): {result['archived_classes'][:10]}{'...' if len(result['archived_classes']) > 10 else ''}")
print(f"   Available classes (active_only=True): {len(result['available_classes'])}")

result2 = get_grades_db(active_only=False)
print(f"\n🧪 Test get_grades_db(active_only=False):")
print(f"   Available classes (all): {len(result2['available_classes'])}")

session.close()
print("\n✅ VERIFICATION COMPLETE!")
