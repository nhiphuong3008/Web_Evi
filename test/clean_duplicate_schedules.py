import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session, init_db
from database.models import ClassSchedule

init_db()
session = db_session()

# Count before
total_before = session.query(ClassSchedule).count()
print(f"Trước khi xóa: {total_before} bản ghi")

# Delete extra entries (ID 41-60)
deleted = session.query(ClassSchedule).filter(ClassSchedule.id >= 41).delete()
session.commit()

total_after = session.query(ClassSchedule).count()
print(f"Đã xóa: {deleted} bản ghi dư thừa")
print(f"Sau khi xóa: {total_after} bản ghi chính thức")

# Verify remaining entries
remaining = session.query(ClassSchedule).order_by(ClassSchedule.day, ClassSchedule.shift_code, ClassSchedule.id).all()
print(f"\n{'='*100}")
print(f"DANH SÁCH 38 BẢN GHI CHÍNH THỨC CÒN LẠI:")
print(f"{'='*100}")

current_day = None
for r in remaining:
    if r.day != current_day:
        current_day = r.day
        print(f"\n--- {r.day} ---")
    print(f"  ID:{r.id:3d} | {r.shift_code:4s} | {r.class_name:18s} | {r.room:10s} | GV: {r.teacher:18s} | SS:{r.students_count:2d} | CM: {r.cm_staff:10s} | TA: {r.ta_staff or '—'}")

session.close()
print(f"\n✅ HOÀN TẤT! Đã khôi phục chính xác {total_after} bản ghi thời khóa biểu chính thức.")
