import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import AttendanceRecord, Student

def seed_hw_data():
    session = db_session()

    # Dữ liệu đối soát từ file Excel chính thức ngày 06/08/2026 & 05/08/2026
    hw_excel_records = [
        # --- LỚP GALAX 1.3 (Ngày 06/08/2026) ---
        {
            'class_name': 'Galax 1.3',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI048',
            'student_name': 'Phạm Hoàng Anh',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 16,
            'hw_total_questions': 16,
            'hw_score': 10.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành tốt BTVN'
        },
        {
            'class_name': 'Galax 1.3',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI377',
            'student_name': 'Đinh Gia Huy Hoàng',
            'status': 'Vắng có phép',
            'note': 'Nghỉ học',
            'hw_correct_answers': None,
            'hw_total_questions': 16,
            'hw_score': None,
            'hw_submission_status': 'Nghỉ học',
            'hw_comment': ''
        },
        {
            'class_name': 'Galax 1.3',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI420',
            'student_name': 'Nguyễn Khánh Diệp',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 14,
            'hw_total_questions': 16,
            'hw_score': 8.8,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành tốt BTVN'
        },
        {
            'class_name': 'Galax 1.3',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI434',
            'student_name': 'Cao Phương Anh',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 15,
            'hw_total_questions': 16,
            'hw_score': 9.4,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành tốt BTVN'
        },
        {
            'class_name': 'Galax 1.3',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI122',
            'student_name': 'Khuất Phạm Minh Anh',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': None,
            'hw_total_questions': 16,
            'hw_score': None,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con nghỉ buổi hôm trước, con cần làm bù BT trang 41+42+43'
        },

        # --- LỚP SUN 2.4 (Ngày 06/08/2026) ---
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI189',
            'student_name': 'Phạm Như Hoàng Dương',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 10,
            'hw_total_questions': 10,
            'hw_score': 10.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành bài đầy đủ'
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI200',
            'student_name': 'Nguyễn Trường Hải',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 10,
            'hw_total_questions': 10,
            'hw_score': 10.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành bài đầy đủ'
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI240',
            'student_name': 'Nguyễn Ngọc Khải Nguyên',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 10,
            'hw_total_questions': 10,
            'hw_score': 10.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành bài đầy đủ'
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI274',
            'student_name': 'Phạm Hoàng Hà My',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 10,
            'hw_total_questions': 10,
            'hw_score': 10.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành bài đầy đủ, con luyện chữ nắn nót hơn nhé'
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI323',
            'student_name': 'Trần Bảo Anh',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 10,
            'hw_total_questions': 10,
            'hw_score': 10.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành bài đầy đủ'
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI333',
            'student_name': 'Phạm Như Bảo Anh',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': None,
            'hw_total_questions': None,
            'hw_score': None,
            'hw_submission_status': 'Không có BVN',
            'hw_comment': 'Con quên sách, buổi sau cô sẽ kiểm tra bù cho con nhé'
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI361',
            'student_name': 'Nguyễn Văn Tuệ',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 10,
            'hw_total_questions': 10,
            'hw_score': 10.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành bài đầy đủ'
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI385',
            'student_name': 'Trần Hoàng Anh',
            'status': 'Vắng có phép',
            'note': 'Nghỉ học',
            'hw_correct_answers': None,
            'hw_total_questions': None,
            'hw_score': None,
            'hw_submission_status': 'Nghỉ học',
            'hw_comment': ''
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI394',
            'student_name': 'Nguyễn Phương Vy',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': None,
            'hw_total_questions': None,
            'hw_score': None,
            'hw_submission_status': 'Không làm',
            'hw_comment': 'Con chưa hoàn thành bài lesson 26 và 27, về nhà con cần hoàn thiện bù nhé'
        },
        {
            'class_name': 'Sun 2.4',
            'attendance_date': '2026-08-06',
            'student_code': 'EVI422',
            'student_name': 'Lê Thị Ngân Hà',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 10,
            'hw_total_questions': 10,
            'hw_score': 10.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con hoàn thành bài đầy đủ'
        },

        # --- LỚP GALAX 1.5 (Ngày 05/08/2026) ---
        {
            'class_name': 'Galax 1.5',
            'attendance_date': '2026-08-05',
            'student_code': 'EVI242',
            'student_name': 'Nguyễn Đăng Minh',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': 69,
            'hw_total_questions': 86,
            'hw_score': 8.0,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con ôn lại cấu trúc "Like/ d like" và cấu trúc viết ngày tháng vì con sai ở các phần này nhiều.'
        },
        {
            'class_name': 'Galax 1.5',
            'attendance_date': '2026-08-05',
            'student_code': 'EVI362',
            'student_name': 'Trần Quốc Bảo',
            'status': 'Có mặt',
            'note': '',
            'hw_correct_answers': None,
            'hw_total_questions': None,
            'hw_score': None,
            'hw_submission_status': 'Nộp đúng giờ',
            'hw_comment': 'Con nghỉ 2 buổi trước, cần chú ý bổ sung BT trang 8'
        },
        {
            'class_name': 'Galax 1.5',
            'attendance_date': '2026-08-05',
            'student_code': 'EVI393',
            'student_name': 'Lê Thị Thùy Dương',
            'status': 'Vắng có phép',
            'note': 'Nghỉ học',
            'hw_correct_answers': None,
            'hw_total_questions': None,
            'hw_score': None,
            'hw_submission_status': 'Nghỉ học',
            'hw_comment': ''
        }
    ]

    updated_count = 0
    for rec in hw_excel_records:
        # Check if record exists
        att = session.query(AttendanceRecord).filter(
            AttendanceRecord.class_name == rec['class_name'],
            AttendanceRecord.attendance_date == rec['attendance_date'],
            AttendanceRecord.student_code == rec['student_code']
        ).first()

        if not att:
            att = AttendanceRecord(
                class_name=rec['class_name'],
                attendance_date=rec['attendance_date'],
                student_code=rec['student_code'],
                student_name=rec['student_name']
            )
            session.add(att)

        att.status = rec['status']
        att.note = rec['note']
        att.hw_correct_answers = rec['hw_correct_answers']
        att.hw_total_questions = rec['hw_total_questions']
        att.hw_score = rec['hw_score']
        att.hw_submission_status = rec['hw_submission_status']
        att.hw_comment = rec['hw_comment']
        updated_count += 1

    session.commit()
    print(f"SUCCESS: Seeded and synced {updated_count} official BTVN records into database!")
    session.close()

if __name__ == '__main__':
    seed_hw_data()
