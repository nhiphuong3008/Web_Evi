import sys
import os
import sqlite3
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_student_detail_db

class TestZeroRemainingSessionsExpiry(unittest.TestCase):
    def test_inspect_evi305_data(self):
        profile = get_student_detail_db('EVI305')
        self.assertTrue(profile['success'])
        st = profile['student']
        
        self.assertEqual(st['code'], 'EVI305')
        self.assertEqual(st['remaining_sessions'], 0)
        self.assertEqual(st['expiry_date'], '10/08/2026')
        
        print("\n--- Student EVI305 (Lương Minh Hưng) Inspection ---")
        print("Name:", st.get('name'))
        print("Class Name:", st.get('class_name'))
        print("Total Sessions:", st.get('total_sessions'))
        print("Remaining Sessions:", st.get('remaining_sessions'))
        print("Theoretical Class Expiry Date:", st.get('expiry_date'))
        print("✅ Student inspection completed successfully!")

if __name__ == '__main__':
    unittest.main()
