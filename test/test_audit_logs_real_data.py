"""
Test script to verify real audit logs data rendering and APIs.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import unittest
from services.db_service import get_activity_logs_db, get_admin_notifications_db

class TestAuditLogsRealData(unittest.TestCase):
    def test_get_activity_logs_returns_real_records(self):
        res = get_activity_logs_db()
        self.assertTrue(res.get('success'))
        self.assertGreater(res.get('total', 0), 0, "Expected at least 1 real activity log record")
        self.assertIn('data', res)
        self.assertGreater(len(res['data']), 0)
        
        # Check first log format
        first_log = res['data'][0]
        self.assertIn('username', first_log)
        self.assertIn('user_fullname', first_log)
        self.assertIn('description', first_log)
        self.assertIn('created_at', first_log)

    def test_get_admin_notifications(self):
        res = get_admin_notifications_db()
        self.assertTrue(res.get('success'))
        self.assertIn('data', res)

if __name__ == '__main__':
    unittest.main()
