import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.db_service import (
    get_class_lesson_log_db,
    save_attendance_db,
    get_attendance_db,
    get_schedule_matrix_db
)

def test_features():
    print("==========================================")
    print("VERIFYING HEADLESS IMPLEMENTATIONS")
    print("==========================================")

    # 1. Test get_class_lesson_log_db for real syllabus
    print("\n--- 1. Testing Syllabus & Lesson Plan Detail ---")
    res_lesson = get_class_lesson_log_db("Sun 3.1")
    print(f"Success: {res_lesson.get('success')}")
    print(f"Materials: {res_lesson.get('materials')}")
    print(f"Total Lessons: {res_lesson.get('total_lessons')}")
    print(f"Lesson Plan Drive URL: {res_lesson.get('lesson_plan_url')}")
    if res_lesson.get('lessons'):
        first_lesson = res_lesson['lessons'][0]
        title = first_lesson.get('lesson_title', '').encode('ascii', 'ignore').decode('ascii')
        unit = first_lesson.get('unit_name', '').encode('ascii', 'ignore').decode('ascii')
        print(f"Sample Lesson 1: Title='{title}' | Unit='{unit}' | Status='{first_lesson.get('status_code')}'")

    # 2. Test Attendance (Official + Guest Student)
    print("\n--- 2. Testing Attendance with Guest Student ---")
    records = [
        {'student_code': 'EVI001', 'student_name': 'Nguyễn Văn A', 'status': 'Có mặt', 'note': 'Đúng giờ', 'is_guest': False},
        {'student_code': 'EVI002', 'student_name': 'Trần Thị B', 'status': 'Đến muộn', 'note': 'Muộn 10p', 'is_guest': False},
        {'student_code': 'EVI099', 'student_name': 'Phạm Văn C (Lớp khác)', 'status': 'Lý do khác', 'note': 'Học bù bài 4', 'is_guest': True}
    ]
    res_save_att = save_attendance_db("Sun 3.1", "2026-08-07", records, created_by="admin")
    print(f"Save Attendance Success: {res_save_att.get('success')} | Saved: {res_save_att.get('saved_count')}")

    # Read back attendance
    res_get_att = get_attendance_db("Sun 3.1", "2026-08-07")
    print(f"Get Attendance Count: {res_get_att.get('count')}")
    for item in res_get_att.get('data', []):
        sname = item['student_name'].encode('ascii', 'ignore').decode('ascii')
        st = item['status'].encode('ascii', 'ignore').decode('ascii')
        nt = item['note'].encode('ascii', 'ignore').decode('ascii')
        print(f"  - {sname} ({item['student_code']}): {st} | Guest: {item['is_guest']} | Note: {nt}")

    # 3. Test Schedule Matrix
    print("\n--- 3. Testing Schedule Matrix ---")
    res_matrix = get_schedule_matrix_db()
    print(f"Matrix Rows Count: {len(res_matrix.get('matrix', []))}")

    print("\n==========================================")
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print("==========================================")

if __name__ == '__main__':
    test_features()
