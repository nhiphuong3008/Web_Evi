import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.db_service import get_class_lesson_log_db, get_schedule_matrix_db

class TestMoon51AndAdvanceFeature(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.class_name = 'Moon 5.1'

    def tearDown(self):
        # Restore Moon 5.1 exact schedule
        from services.db_service import get_next_study_date, get_prev_study_date
        import sqlite3, datetime
        conn = sqlite3.connect('database/evi_center.db')
        cursor = conn.cursor()
        sorted_weekdays = [2, 5]
        dates = {47: datetime.date(2026, 8, 19)}
        for l_num in range(46, 0, -1):
            dates[l_num] = get_prev_study_date(dates[l_num + 1], sorted_weekdays)
        for l_num in range(48, 71):
            dates[l_num] = get_next_study_date(dates[l_num - 1], sorted_weekdays)
        for l_num, dt in dates.items():
            cursor.execute("UPDATE lesson_syllabuses SET official_date = ? WHERE class_name = 'Moon 5.1' AND lesson_num = ?", (dt.strftime('%Y-%m-%d'), l_num))
        conn.commit()
        conn.close()

    def test_moon51_lesson47_on_19_08(self):
        # Verify Moon 5.1 has Lesson 47 on 19/08 (completed) and Lesson 48 on 22/08 (pending)
        log_res = get_class_lesson_log_db(self.class_name)
        self.assertTrue(log_res['success'])

        lesson_47 = next((l for l in log_res['lessons'] if l['buoi'] == 47), None)
        self.assertIsNotNone(lesson_47)
        self.assertEqual(lesson_47['date'], '19/08')
        self.assertEqual(lesson_47['status_code'], 'completed')
        print("✅ Verified Moon 5.1 Lesson 47:", lesson_47['buoi'], lesson_47['date'], lesson_47['status_label'])

        lesson_48 = next((l for l in log_res['lessons'] if l['buoi'] == 48), None)
        self.assertIsNotNone(lesson_48)
        self.assertEqual(lesson_48['date'], '22/08')
        self.assertEqual(lesson_48['status_code'], 'pending')
        print("✅ Verified Moon 5.1 Lesson 48:", lesson_48['buoi'], lesson_48['date'], lesson_48['status_label'])

        # Verify Schedule Matrix
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
        self.assertEqual(found_card.get('current_buoi'), 47)
        print("✅ Verified Schedule Matrix for Moon 5.1 current_buoi:", found_card.get('current_buoi'), found_card.get('current_title'))

    def test_advance_lesson_api(self):
        # Test advance-lesson API endpoint
        res = self.app.post('/api/schedule/advance-lesson', json={'class_name': self.class_name, 'lesson_num': 48})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        print("✅ API advance-lesson tested successfully:", data['advance_res'])

if __name__ == '__main__':
    unittest.main()
