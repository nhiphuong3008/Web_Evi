import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from database.db_manager import db_session, init_db

class TestMatrixAndPopup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        init_db()

    def test_01_api_matrix(self):
        response = self.client.get('/api/schedule/matrix')
        json_data = response.get_json()
        print(f"\n[TEST 1] GET /api/schedule/matrix success: {json_data.get('success')}, rows: {len(json_data.get('matrix', []))}")
        self.assertTrue(json_data.get('success'))
        self.assertGreater(len(json_data.get('matrix', [])), 0)

    def test_02_api_class_detail_popup(self):
        response = self.client.get('/api/schedule/class-detail?class_name=Sun 2.4')
        json_data = response.get_json()
        print(f"[TEST 2] GET /api/schedule/class-detail?class_name=Sun 2.4 lessons count: {len(json_data.get('lessons', []))}")
        self.assertTrue(json_data.get('success'))
        self.assertEqual(json_data.get('class_name'), 'Sun 2.4')
        self.assertEqual(len(json_data.get('lessons', [])), 24)

if __name__ == '__main__':
    unittest.main()
