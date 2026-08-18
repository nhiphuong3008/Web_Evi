"""
Test script to verify reverse chronological date sorting for BTVN records.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import unittest
from services.db_service import get_student_detail_db, get_homework_db

class TestDateSortingOrder(unittest.TestCase):
    def test_student_detail_homework_date_sorting(self):
        res = get_student_detail_db('EVI122')
        if not res.get('success'):
            res = get_student_detail_db('EVI')
        
        self.assertTrue(res.get('success'))
        hw_list = res.get('homework', [])

        # Function to parse DD/MM/YYYY to tuple (YYYY, MM, DD)
        def parse_d(d_str):
            if not d_str: return (0, 0, 0)
            parts = d_str.split('/')
            if len(parts) == 3:
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            return (0, 0, 0)

        # Verify each adjacent pair is sorted descending (newer >= older)
        for i in range(len(hw_list) - 1):
            d1 = parse_d(hw_list[i].get('date', ''))
            d2 = parse_d(hw_list[i+1].get('date', ''))
            if d1 != (0,0,0) and d2 != (0,0,0):
                self.assertGreaterEqual(d1, d2, f"Expected {hw_list[i]['date']} >= {hw_list[i+1]['date']}")

if __name__ == '__main__':
    unittest.main()
