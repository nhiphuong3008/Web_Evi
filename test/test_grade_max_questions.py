"""
Unit test to verify total max questions saving and live calculation.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.db_manager import db_session
from database.models import UnitGrade

class TestGradeMaxQuestions(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_save_and_retrieve_max_questions(self):
        """Test POST /api/grades/save saves listening_max, reading_writing_max, speaking_max."""
        test_payload = {
            'grades': [
                {
                    'code': 'EVI069',
                    'name': 'Hồ Minh Tú',
                    'class_name': 'GALAX 3.2',
                    'test_name': 'Midterm',
                    'listening': 21.0,
                    'reading_writing': 25.0,
                    'speaking': 8.5,
                    'listening_max': 25.0,
                    'reading_writing_max': 40.0,
                    'speaking_max': 10.0,
                    'comment': 'Kỹ năng nghe tốt'
                }
            ]
        }

        res = self.client.post('/api/grades/save', json=test_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))

        # Fetch via GET /api/grades
        get_res = self.client.get('/api/grades?class_name=GALAX+3.2&test_name=Midterm')
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.get_json()
        self.assertTrue(get_data.get('success'))
        
        grades = get_data.get('data', [])
        found = False
        for g in grades:
            if g.get('name') == 'Hồ Minh Tú' and g.get('test_name') == 'Midterm':
                found = True
                self.assertEqual(g.get('listening_max'), 25.0)
                self.assertEqual(g.get('reading_writing_max'), 40.0)
                self.assertEqual(g.get('speaking_max'), 10.0)
                print(f"\n✅ PASS: Successfully verified max scores for {g['name']}: Lis_max={g['listening_max']}, RW_max={g['reading_writing_max']}, Spk_max={g['speaking_max']}")
                break
        self.assertTrue(found, "Should find saved grade record")

if __name__ == '__main__':
    unittest.main()
