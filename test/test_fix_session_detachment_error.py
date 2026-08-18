"""
Test script to verify fix for 'Instance is not bound to a Session' error in get_student_detail_db.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import unittest
from services.db_service import get_student_detail_db

class TestFixSessionDetachment(unittest.TestCase):
    def test_get_student_detail_no_detachment_error(self):
        # Fetch profile for student code EVI122 or similar
        res = get_student_detail_db('EVI122')
        if not res.get('success'):
            res = get_student_detail_db('EVI')
        
        self.assertTrue(res.get('success'), f"Expected success, got error: {res.get('error')}")
        self.assertIn('student', res)
        self.assertIn('homework', res)
        self.assertIn('grades', res)

if __name__ == '__main__':
    unittest.main()
