"""
Unit tests for Auth, User Management, Attendance, and Grade Entry.
Run with: python -m unittest test/test_auth_and_cm.py
"""

import sys
import os
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.db_manager import init_db, db_session
from database.models import User, AttendanceRecord, UnitGrade


class TestAuthAndCMPortal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        init_db()

    def test_01_seed_users(self):
        """Test initial seed users exist in DB."""
        session = db_session()
        admin_user = session.query(User).filter_by(username='admin').first()
        cm_user = session.query(User).filter_by(username='cm_thucanh').first()
        session.close()

        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user.role, 'admin')
        self.assertIsNotNone(cm_user)
        self.assertIn(cm_user.cm_staff_name, ['Thục Anh', 'AnhPTT'])

    def test_02_login_api(self):
        """Test POST /api/auth/login endpoint."""
        # Valid login
        res = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'admin')

        # Invalid password
        res_fail = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        self.assertEqual(res_fail.status_code, 401)
        self.assertFalse(res_fail.get_json()['success'])

    def test_03_user_crud(self):
        """Test GET, POST, PUT, DELETE /api/users endpoint."""
        # Create new user
        res_create = self.client.post('/api/users', json={
            'username': 'test_cm_user',
            'password': 'password123',
            'full_name': 'Test CM User',
            'email': 'testcm@evi.edu.vn',
            'role': 'cm',
            'cm_staff_name': 'Thục Anh'
        })
        self.assertEqual(res_create.status_code, 201)
        created_user = res_create.get_json()['user']
        user_id = created_user['id']

        # Get users list
        res_list = self.client.get('/api/users')
        self.assertEqual(res_list.status_code, 200)
        users = res_list.get_json()['users']
        self.assertTrue(any(u['username'] == 'test_cm_user' for u in users))

        # Update user
        res_update = self.client.put(f'/api/users/{user_id}', json={
            'full_name': 'Test CM User Updated',
            'email': 'updated@evi.edu.vn'
        })
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.get_json()['user']['full_name'], 'Test CM User Updated')

        # Delete user
        res_delete = self.client.delete(f'/api/users/{user_id}')
        self.assertEqual(res_delete.status_code, 200)

    def test_04_attendance_api(self):
        """Test POST /api/attendance and GET /api/attendance."""
        res_save = self.client.post('/api/attendance', json={
            'class_name': 'TestClass101',
            'date': '2026-08-01',
            'created_by': 'cm_thucanh',
            'records': [
                {'student_code': 'EVI999', 'student_name': 'Học Sinh A', 'status': 'Có mặt', 'note': 'Đi học ngoan'},
                {'student_code': 'EVI998', 'student_name': 'Học Sinh B', 'status': 'Vắng có phép', 'note': 'Ốm nhẹ'}
            ]
        })
        self.assertEqual(res_save.status_code, 200)
        self.assertTrue(res_save.get_json()['success'])

        res_get = self.client.get('/api/attendance?class_name=TestClass101&date=2026-08-01')
        self.assertEqual(res_get.status_code, 200)
        att_data = res_get.get_json()['data']
        self.assertEqual(len(att_data), 2)

    def test_05_grade_save_api(self):
        """Test POST /api/grades/save endpoint."""
        res_grade = self.client.post('/api/grades/save', json={
            'grades': [
                {
                    'code': 'EVI999',
                    'name': 'Học Sinh A',
                    'class_name': 'TestClass101',
                    'test_name': 'Unit 1 Test',
                    'listening': 9.0,
                    'reading_writing': 11.0,
                    'speaking': 9.5,
                    'comment': 'Làm bài rất tốt!'
                }
            ]
        })
        self.assertEqual(res_grade.status_code, 200)
        self.assertTrue(res_grade.get_json()['success'])

        # Verify in DB
        session = db_session()
        g_rec = session.query(UnitGrade).filter_by(class_name='TestClass101', test_name='Unit 1 Test').first()
        session.close()

        self.assertIsNotNone(g_rec)
        self.assertEqual(g_rec.listening, 9.0)
        self.assertEqual(g_rec.total_score, 29.5)


if __name__ == '__main__':
    unittest.main()
