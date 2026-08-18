"""
Test script to verify syncing AttendanceRecord BTVN entries to HomeworkRecord.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import sqlite3
import unittest
from database.db_manager import db_session
from database.models import AttendanceRecord, HomeworkRecord, Student

def sync_attendance_hw_to_homework_records_db():
    """
    Đồng bộ tất cả dữ liệu BTVN từ nhật ký điểm danh hàng ngày (attendance_records)
    sang bảng HomeworkRecord (homework_records).
    """
    session = db_session()
    try:
        att_records = session.query(AttendanceRecord).all()
        synced_count = 0

        # Build map of student_code -> english_name from Student table
        students = session.query(Student).all()
        st_map = {s.code: (s.english_name or '') for s in students if s.code}

        for att in att_records:
            if not att.student_name:
                continue
            
            # Map status
            status_raw = (att.hw_submission_status or '').strip()
            if status_raw in ['Nộp đúng giờ', 'Đã nộp', 'Hoàn thành']:
                status_clean = 'Đã nộp'
            elif status_raw == 'Nộp muộn':
                status_clean = 'Nộp muộn'
            elif status_raw in ['Không làm', 'Chưa nộp BTVN', 'Không có BVN']:
                status_clean = 'Chưa nộp BTVN'
            elif status_raw:
                status_clean = status_raw
            else:
                status_clean = 'Chưa nộp BTVN'

            # Standardize date format: YYYY-MM-DD -> DD/MM/YYYY
            date_clean = att.attendance_date or ''
            if '-' in date_clean and len(date_clean.split('-')) == 3:
                parts = date_clean.split('-')
                date_clean = f"{parts[2]}/{parts[1]}/{parts[0]}"

            st_code = att.student_code or ''
            eng_name = st_map.get(st_code, '')

            # Check if record already exists in HomeworkRecord
            existing = session.query(HomeworkRecord).filter(
                HomeworkRecord.student_name == att.student_name,
                HomeworkRecord.class_name == att.class_name,
                HomeworkRecord.submission_date == date_clean
            ).first()

            score_str = f"{att.hw_score:.1f}" if att.hw_score is not None else ''

            if existing:
                existing.student_code = st_code or existing.student_code
                existing.english_name = eng_name or existing.english_name
                existing.status = status_clean
                existing.score = score_str
                existing.score_num = att.hw_score or 0.0
                existing.total_questions = str(att.hw_total_questions or '')
                existing.teacher_note = att.hw_comment or att.note or existing.teacher_note
            else:
                hw = HomeworkRecord(
                    student_code=st_code,
                    student_name=att.student_name,
                    english_name=eng_name,
                    class_name=att.class_name,
                    submission_date=date_clean,
                    status=status_clean,
                    score=score_str,
                    score_num=att.hw_score or 0.0,
                    total_questions=str(att.hw_total_questions or ''),
                    teacher_note=att.hw_comment or att.note or ''
                )
                session.add(hw)
                synced_count += 1

        session.commit()
        session.close()
        return {'success': True, 'synced_count': synced_count}
    except Exception as e:
        session.rollback()
        session.close()
        return {'success': False, 'error': str(e)}

class TestSyncAttendanceToHomework(unittest.TestCase):
    def test_sync_execution(self):
        res = sync_attendance_hw_to_homework_records_db()
        self.assertTrue(res['success'])
        print(f"Synced {res.get('synced_count')} attendance HW records to HomeworkRecords!")

if __name__ == '__main__':
    unittest.main()
