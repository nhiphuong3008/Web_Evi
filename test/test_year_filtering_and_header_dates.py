import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.db_manager import db_session
from database.models import ParentInteractionLog

class TestYearFilteringAndHeaderDates(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_distinct_dates_in_db(self):
        print("\n--- Verifying Distinct Dates in DB ---")
        session = db_session()
        logs = session.query(ParentInteractionLog).all()
        self.assertGreater(len(logs), 0)

        distinct_dates = set(l.created_at.strftime('%Y-%m-%d') for l in logs if l.created_at)
        print(f"✅ Distinct dates found in DB: {sorted(list(distinct_dates))}")
        
        # Verify 2025-01-01 (for 2023-2025) and 2026 dates exist
        self.assertIn('2025-01-01', distinct_dates)
        self.assertIn('2026-03-01', distinct_dates)
        session.close()

    def test_api_year_filtering(self):
        print("\n--- Testing API Year Filtering ---")
        # 1. Filter year=2026
        res2026 = self.client.get('/api/interactions/all?year=2026')
        self.assertEqual(res2026.status_code, 200)
        data2026 = res2026.get_json()
        self.assertTrue(data2026['success'])
        count2026 = data2026['count']
        print(f"✅ Year 2026 returned {count2026} records.")

        # 2. Filter year=2023-2025
        res_old = self.client.get('/api/interactions/all?year=2023-2025')
        self.assertEqual(res_old.status_code, 200)
        data_old = res_old.get_json()
        self.assertTrue(data_old['success'])
        count_old = data_old['count']
        print(f"✅ Year 2023-2025 returned {count_old} records.")

        self.assertGreater(count2026, 0)
        self.assertGreater(count_old, 0)

if __name__ == '__main__':
    unittest.main()
