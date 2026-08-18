import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')


from database.db_manager import db_session
from services.db_service import (
    preview_holiday_shift_db,
    create_holiday_shift_db,
    cancel_holiday_shift_db,
    get_holiday_history_logs_db,
    calculate_real_class_lesson_dates,
    get_class_lesson_log_db
)
from database.models import ClassSchedule, LessonSyllabus, Student, HolidayHistoryLog

def test_holiday_shift_flow():
    # Clean up prior test runs
    session = db_session()
    session.query(HolidayHistoryLog).delete()
    session.commit()
    session.close()

    print("--- 1. Testing Preview Holiday Shift ---")
    prev_res = preview_holiday_shift_db('2026-09-01', '2026-09-03', ['ALL'])
    print("Preview result:", prev_res)
    assert prev_res.get('success') is True
    assert prev_res.get('holiday_days') == 3

    print("\n--- 2. Testing Create Holiday Shift ---")
    create_res = create_holiday_shift_db(
        title="Test Nghỉ lễ Quốc Khánh 2/9",
        holiday_type="Nghỉ lễ cố định",
        start_date="2026-09-01",
        end_date="2026-09-03",
        affected_classes=["ALL"],
        note="Test nghỉ lễ 3 ngày",
        created_by="Admin"
    )
    print("Create result:", create_res)
    assert create_res.get('success') is True
    holiday_id = create_res.get('holiday_id')

    print("\n--- 3. Testing Syllabus Skipping Holiday ---")
    lesson_log = get_class_lesson_log_db('Galax 1.3')
    if lesson_log and lesson_log.get('lessons'):
        for l in lesson_log.get('lessons')[:6]:
            print(f"Lesson {l.get('buoi')}: {l.get('date')} ({l.get('title')})")

    print("\n--- 4. Testing Get Holiday History ---")
    hist_res = get_holiday_history_logs_db()
    print(f"History count: {hist_res.get('count')}")
    assert hist_res.get('count') > 0

    print("\n--- 5. Testing Cancel Holiday Shift (Rollback) ---")
    cancel_res = cancel_holiday_shift_db(holiday_id)
    print("Cancel result:", cancel_res)
    assert cancel_res.get('success') is True

    print("\n✅ ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_holiday_shift_flow()
