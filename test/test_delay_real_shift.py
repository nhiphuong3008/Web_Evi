import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.db_service import toggle_delay_class_lesson_db, get_class_lesson_log_db, get_next_study_date, get_prev_study_date
import sqlite3, datetime

class TestDelayLessonRealShift(unittest.TestCase):
    def setUp(self):
        self.class_name = 'Moon 5.1'
        # Reset to base schedule: Lesson 47 = 19/08, Lesson 48 = 22/08
        self._reset_moon51()

    def _reset_moon51(self):
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
        # Clear delayed_lessons
        cursor.execute("UPDATE class_schedule_adjustments SET delayed_lessons = '[]' WHERE class_name LIKE '%Moon 5.1%'")
        conn.commit()
        conn.close()

    def test_delay_lesson_48_shifts_dates(self):
        # 1. Before delay: Buoi 48 is 22/08
        log_before = get_class_lesson_log_db(self.class_name)
        l48_before = next(l for l in log_before['lessons'] if l['buoi'] == 48)
        self.assertEqual(l48_before['date'], '22/08')

        # 2. Toggle delay at Buoi 48 -> Should shift Buoi 48 to 26/08 (+1 study date)
        res = toggle_delay_class_lesson_db(self.class_name, 48)
        self.assertTrue(res['success'])
        self.assertTrue(res['is_delayed'])

        log_after = get_class_lesson_log_db(self.class_name)
        l48_after = next(l for l in log_after['lessons'] if l['buoi'] == 48)
        self.assertEqual(l48_after['date'], '26/08')
        self.assertTrue(l48_after['is_delayed'])
        print("✅ Tested Lùi Lịch: Buoi 48 moved from 22/08 ->", l48_after['date'])

        # 3. Toggle again (Hủy Lùi) -> Should shift Buoi 48 back to 22/08 (-1 study date)
        res_undo = toggle_delay_class_lesson_db(self.class_name, 48)
        self.assertTrue(res_undo['success'])
        self.assertFalse(res_undo['is_delayed'])

        log_undo = get_class_lesson_log_db(self.class_name)
        l48_undo = next(l for l in log_undo['lessons'] if l['buoi'] == 48)
        self.assertEqual(l48_undo['date'], '22/08')
        self.assertFalse(l48_undo['is_delayed'])
        print("✅ Tested Hủy Lùi: Buoi 48 returned back to", l48_undo['date'])

if __name__ == '__main__':
    unittest.main()
