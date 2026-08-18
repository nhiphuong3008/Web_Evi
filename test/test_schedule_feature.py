import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from database.db_manager import db_session, init_db
from database.models import ClassSchedule

class TestScheduleFeature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        init_db()

    def test_01_db_schedules_count(self):
        session = db_session()
        count = session.query(ClassSchedule).count()
        print(f"\n[TEST 1] SQLite ClassSchedule total records count: {count}")
        self.assertGreaterEqual(count, 60, "Database should contain at least 60 schedule records")

    def test_02_api_get_schedule(self):
        response = self.client.get('/api/schedule')
        json_data = response.get_json()
        print(f"[TEST 2] GET /api/schedule success: {json_data.get('success')}, count: {json_data.get('count')}")
        self.assertTrue(json_data.get('success'))
        self.assertGreaterEqual(json_data.get('count', 0), 60)

    def test_03_api_cm_van_anh_schedule(self):
        response = self.client.get('/api/schedule?cm_staff_name=Vân Anh')
        json_data = response.get_json()
        cm_count = json_data.get('cm_classes_count', 0)
        print(f"[TEST 3] GET /api/schedule?cm_staff_name=Vân Anh cm_classes_count: {cm_count}")
        self.assertGreaterEqual(cm_count, 10, "CM Vân Anh should manage at least 10 classes")

    def test_04_api_cm_ngoc_schedule(self):
        response = self.client.get('/api/schedule?cm_staff_name=NgọcCM')
        json_data = response.get_json()
        cm_count = json_data.get('cm_classes_count', 0)
        print(f"[TEST 4] GET /api/schedule?cm_staff_name=NgọcCM cm_classes_count: {cm_count}")
        self.assertGreaterEqual(cm_count, 10, "CM NgọcCM should manage at least 10 classes")

if __name__ == '__main__':
    unittest.main()
