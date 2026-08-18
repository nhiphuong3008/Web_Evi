"""
Unit test to verify automatic resolution of teacher, CM, schedule, and room for students based on their class name.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import unittest
from services.db_service import get_student_detail_db, resolve_class_info_from_schedule_db

class TestStudentClassInfoAutoResolve(unittest.TestCase):
    def test_evi442_auto_resolve(self):
        res = get_student_detail_db('EVI442')
        self.assertTrue(res.get('success'))
        st = res.get('student', {})
        self.assertEqual(st.get('name'), 'Nguyễn Thanh Sơn')
        self.assertEqual(st.get('class_name'), 'Moon 1.1')
        self.assertEqual(st.get('teacher'), 'Andrew')
        self.assertEqual(st.get('cm'), 'AnhPTT')

    def test_resolve_class_info_function(self):
        info = resolve_class_info_from_schedule_db('Moon 1.1')
        self.assertIn('Andrew', info['teacher'])
        self.assertIn('AnhPTT', info['cm_staff'])

if __name__ == '__main__':
    unittest.main()
