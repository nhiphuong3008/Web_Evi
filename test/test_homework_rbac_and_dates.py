"""
Test script for Homework Search enhancements: Date Range filtering, Class filtering, and CM RBAC grouping.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import unittest
from services.db_service import get_homework_db

class TestHomeworkRbacAndDates(unittest.TestCase):
    def test_get_homework_all_records(self):
        res = get_homework_db()
        self.assertTrue(res['success'])
        self.assertIn('available_classes', res)
        self.assertIn('summary', res)

    def test_get_homework_with_class_filter(self):
        res = get_homework_db(class_name='Galax 1.4')
        self.assertTrue(res['success'])
        for r in res['data']:
            self.assertEqual(r['class_name'], 'Galax 1.4')

    def test_get_homework_with_cm_staff(self):
        res = get_homework_db(cm_staff='thucanh')
        self.assertTrue(res['success'])
        self.assertIn('cm_assigned_classes', res)
        self.assertIsInstance(res['cm_assigned_classes'], list)

    def test_get_homework_with_date_range(self):
        res = get_homework_db(start_date='01/06/2026', end_date='30/06/2026')
        self.assertTrue(res['success'])
        self.assertIsInstance(res['data'], list)

if __name__ == '__main__':
    unittest.main()
