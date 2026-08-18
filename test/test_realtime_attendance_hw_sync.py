"""
Test script to verify real-time sync of daily attendance BTVN to HomeworkRecords and Student Profile.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import unittest
from services.db_service import save_attendance_db, get_homework_db

class TestRealtimeAttendanceHwSync(unittest.TestCase):
    def test_save_attendance_syncs_homework(self):
        records = [
            {
                'student_code': 'TEST999',
                'student_name': 'Học Sinh Test BTVN',
                'status': 'Có mặt',
                'hw_total_questions': 10,
                'hw_correct_answers': 9,
                'hw_score': 9.0,
                'hw_submission_status': 'Nộp đúng giờ',
                'hw_comment': 'Làm bài rất tốt'
            }
        ]
        
        # Save attendance
        res = save_attendance_db('Galax 1.5', '2026-08-16', records, created_by='test_admin')
        self.assertTrue(res['success'])

        # Check get_homework_db
        hw_res = get_homework_db(search='TEST999')
        self.assertTrue(hw_res['success'])
        self.assertGreater(len(hw_res['data']), 0)
        found = any(h['code'] == 'TEST999' or 'Học Sinh Test BTVN' in h['name'] for h in hw_res['data'])
        self.assertTrue(found, "Newly saved attendance HW record should be found in get_homework_db")

if __name__ == '__main__':
    unittest.main()
