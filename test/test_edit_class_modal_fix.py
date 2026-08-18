"""
Test script to verify class editing and modal functionality.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import unittest
from services.db_service import get_schedule_matrix_db

class TestEditClassModalFix(unittest.TestCase):
    def test_get_schedule_matrix_contains_class(self):
        res = get_schedule_matrix_db()
        self.assertTrue(res.get('success'))
        self.assertIn('matrix', res)

if __name__ == '__main__':
    unittest.main()
