import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import save_attendance_db, get_attendance_db

def test_hw():
    test_records = [
        {
            'student_code': 'EVI048',
            'student_name': 'Phạm Hoàng Anh',
            'status': 'Có mặt',
            'note': 'Học đầy đủ',
            'is_guest': False,
            'hw_correct_answers': 8,
            'hw_total_questions': 10,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Hoàn thành tốt bài viết'
        },
        {
            'student_code': 'EVI122',
            'student_name': 'Khuất Phạm Minh Anh',
            'status': 'Có mặt',
            'note': '',
            'is_guest': False,
            'hw_correct_answers': 6,
            'hw_total_questions': 10,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Cần ôn lại từ vựng Unit 2'
        }
    ]

    res_save = save_attendance_db(class_name='Galax 1.3', attendance_date='2026-08-06', records=test_records, created_by='test_admin')
    print("SAVE ATTENDANCE & HW RESULT:", str(res_save).encode('ascii', 'ignore').decode('ascii'))

    res_get = get_attendance_db(class_name='Galax 1.3', attendance_date='2026-08-06')
    print("\nGET ATTENDANCE & HW RESULT:")
    for r in res_get.get('data', []):
        clean_name = r['student_name'].encode('ascii', 'ignore').decode('ascii')
        clean_comm = r.get('hw_comment', '').encode('ascii', 'ignore').decode('ascii')
        clean_stat = r.get('hw_submission_status', '').encode('ascii', 'ignore').decode('ascii')
        print(f"  {r['student_code']} | {clean_name:20s} | Score: {r['hw_score']} pts ({r['hw_correct_answers']}/{r['hw_total_questions']}) | Status: {clean_stat} | Comment: {clean_comm}")

if __name__ == '__main__':
    test_hw()
