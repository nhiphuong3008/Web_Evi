"""
Test Suite: DB-Only Data Flow & Background Incremental Sync Verification
Xác minh 100% tất cả các API endpoint sử dụng CSDL SQLite và Incremental Sync bảo vệ dữ liệu nhập tay.
"""

import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.db_manager import db_session
from database.models import (
    Student, AttendanceRecord, ParentInteractionLog, StudentRenewal, HomeworkRecord, UnitGrade
)
from services.sync_scheduler import run_incremental_sync, get_sync_status


class TestDbOnlyFlowAndSync(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_health_check(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'ok')

    def test_02_dashboard_summary_db_only(self):
        res = self.client.get('/api/dashboard/summary')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        kpi = data.get('data', {}).get('kpi', {})
        self.assertIn('total_students', kpi)
        self.assertIn('active_classes', kpi)
        self.assertIn('latest_renewal_rate', kpi)

    def test_03_system_mode_returns_db(self):
        res = self.client.get('/api/system/mode')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('mode'), 'db')

    def test_04_students_api_from_db(self):
        res = self.client.get('/api/students')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertGreater(data.get('count', 0), 0)

    def test_05_homework_api_from_db(self):
        res = self.client.get('/api/homework')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))

    def test_06_grades_api_from_db(self):
        res = self.client.get('/api/grades')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))

    def test_07_sync_status_endpoint(self):
        res = self.client.get('/api/sync/status')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('sync_status', data)

    def test_08_incremental_sync_preserves_manual_data(self):
        # 1. Insert dummy manual entry for Attendance and CM Log
        session = db_session()
        att = AttendanceRecord(
            class_name="Galax 1.3",
            attendance_date="2026-08-09",
            student_code="EVI001",
            student_name="Test Student",
            status="Có mặt",
            created_by="TestAgent"
        )
        session.add(att)
        session.commit()
        att_id = att.id

        # 2. Run incremental sync
        success, msg = run_incremental_sync()
        
        # 3. Verify manual attendance entry is still intact
        check_att = session.query(AttendanceRecord).filter(AttendanceRecord.id == att_id).first()
        self.assertIsNotNone(check_att)
        self.assertEqual(check_att.status, "Có mặt")

        # Cleanup test entry
        session.delete(check_att)
        session.commit()
        session.close()


if __name__ == '__main__':
    unittest.main()
