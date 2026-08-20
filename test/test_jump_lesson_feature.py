import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.db_service import (
    set_class_current_lesson_db,
    get_class_lesson_log_db,
    get_schedule_matrix_db
)

class TestJumpLessonFeature(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.class_name = 'Moon 5.1'

    def test_pin_and_unpin_flow(self):
        # 1. Pin Lesson 46 for Moon 5.1
        res = set_class_current_lesson_db(self.class_name, 46)
        self.assertTrue(res['success'])
        self.assertEqual(res['mode'], 'pinned')
        self.assertEqual(res['pinned_lesson_num'], 46)
        print("1. Set pinned lesson 46:", res)

        # 2. Check get_class_lesson_log_db
        log_res = get_class_lesson_log_db(self.class_name)
        self.assertTrue(log_res['success'])
        self.assertEqual(log_res['pinned_lesson_num'], 46)
        
        lesson_46 = next((l for l in log_res['lessons'] if l['buoi'] == 46), None)
        self.assertIsNotNone(lesson_46)
        self.assertTrue(lesson_46['is_pinned'])
        self.assertEqual(lesson_46['status_code'], 'today')
        self.assertIn('Đã ghim', lesson_46['status_label'])
        print("2. Verified lesson log for Buoi 46:", lesson_46['buoi'], lesson_46['status_label'], lesson_46['is_pinned'])

        # 3. Check get_schedule_matrix_db
        matrix_res = get_schedule_matrix_db()
        self.assertTrue(matrix_res['success'])
        found_card = None
        for row in matrix_res['matrix']:
            for s in [row['mt5'], row['mt6']]:
                if s and s.get('class_name') and self.class_name.lower() in s.get('class_name').lower():
                    found_card = s
                    break
            if found_card:
                break
        
        self.assertIsNotNone(found_card)
        self.assertEqual(found_card.get('current_buoi'), 46)
        self.assertTrue(found_card.get('is_pinned'))
        print("3. Verified Schedule Matrix card:", found_card.get('class_name'), "current_buoi=", found_card.get('current_buoi'), "is_pinned=", found_card.get('is_pinned'))

        # 4. Test API endpoint /api/schedule/jump-lesson
        api_res = self.app.post('/api/schedule/jump-lesson', json={'class_name': self.class_name, 'lesson_num': 47})
        self.assertEqual(api_res.status_code, 200)
        data = api_res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['pinned_lesson_num'], 47)
        print("4. API test jump to 47:", data['jump_res'])

        # 5. Test unpinning back to auto (lesson_num=None or 0 or toggle 47)
        unpin_res = set_class_current_lesson_db(self.class_name, 0)
        self.assertTrue(unpin_res['success'])
        self.assertEqual(unpin_res['mode'], 'auto')
        self.assertIsNone(unpin_res['pinned_lesson_num'])
        print("5. Reset to auto mode:", unpin_res)

        log_auto = get_class_lesson_log_db(self.class_name)
        self.assertIsNone(log_auto['pinned_lesson_num'])
        print("6. Verified back to auto date calculation successfully!")

if __name__ == '__main__':
    unittest.main()
