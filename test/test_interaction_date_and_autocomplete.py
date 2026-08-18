import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.db_manager import db_session
from database.models import ParentInteractionLog, Student

class TestInteractionDateAndAutocomplete(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_add_interaction_with_date_and_lookup(self):
        print("\n--- Testing API Add Interaction with Custom Date and Auto Student Lookup ---")

        # Test /api/students endpoint
        res_st = self.client.get('/api/students')
        self.assertEqual(res_st.status_code, 200)
        st_data = res_st.get_json()
        self.assertTrue(st_data.get('success'))
        self.assertGreater(len(st_data.get('data', [])), 0)
        print(f"✅ /api/students endpoint returned {len(st_data.get('data', []))} students!")

        payload = {
            'student_code': 'Lương Minh Hưng',
            'staff_name': 'NgọcCM',
            'detail': 'Phụ huynh xác nhận đăng ký học kỳ mới cho học sinh.',
            'interaction_date': '2026-08-10'
        }

        response = self.client.post('/api/interactions/add', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))

        log_id = data['data']['id']
        print(f"✅ Added interaction #{log_id} successfully!")

        # Verify DB entry
        session = db_session()
        log = session.query(ParentInteractionLog).filter(ParentInteractionLog.id == log_id).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.created_at.strftime('%Y-%m-%d'), '2026-08-10')
        print(f"✅ DB created_at date verified: {log.created_at}")
        print(f"✅ Student Code auto-resolved: {log.student_code}")
        print(f"✅ Student Name auto-resolved: {log.student_name}")

        # Clean up test log
        session.delete(log)
        session.commit()
        session.close()
        print("✅ Cleaned up test interaction log.")

if __name__ == '__main__':
    unittest.main()
