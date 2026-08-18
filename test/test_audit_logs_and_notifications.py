"""
Automated Test Suite for Admin Audit Logs & Activity Notifications
EVI Dashboard - System Verification
"""

import sys
import os
import unittest
import json
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5001"

class TestAuditLogsAndNotifications(unittest.TestCase):
    """Test suite for activity logging and notification endpoints."""

    def test_01_activity_logs_api(self):
        """Test GET /api/admin/audit-logs returns valid logs structure."""
        url = f"{BASE_URL}/api/admin/audit-logs"
        r = requests.get(url, params={'limit': 10})
        self.assertEqual(r.status_code, 200, f"Expected 200, got {r.status_code}")
        data = r.json()
        self.assertTrue(data.get('success'), "Response success should be True")
        self.assertIn('data', data, "Response should contain 'data'")
        self.assertGreater(data.get('total', 0), 0, "Total activity logs count should be > 0")
        
        logs = data.get('data', [])
        self.assertGreater(len(logs), 0, "Logs array should not be empty")
        sample = logs[0]
        self.assertIn('username', sample)
        self.assertIn('action_type', sample)
        self.assertIn('description', sample)

    def test_02_notifications_api(self):
        """Test GET /api/admin/notifications returns notifications & unread count."""
        url = f"{BASE_URL}/api/admin/notifications"
        r = requests.get(url, params={'limit': 10})
        self.assertEqual(r.status_code, 200, f"Expected 200, got {r.status_code}")
        data = r.json()
        self.assertTrue(data.get('success'), "Response success should be True")
        self.assertIn('unread_count', data, "Response should contain 'unread_count'")
        self.assertIn('data', data, "Response should contain 'data'")

    def test_03_mark_read_api(self):
        """Test POST /api/admin/notifications/mark-read."""
        url = f"{BASE_URL}/api/admin/notifications/mark-read"
        r = requests.post(url, json={})
        self.assertEqual(r.status_code, 200, f"Expected 200, got {r.status_code}")
        data = r.json()
        self.assertTrue(data.get('success'), "Mark read response success should be True")

    def test_04_auto_logging_on_interaction(self):
        """Test auto-logging when adding a new parent interaction log."""
        # 1. Add interaction
        url_add = f"{BASE_URL}/api/interactions/add"
        payload = {
            'student_code': 'EVI266',
            'student_name': 'Dương Minh Khang',
            'class_name': 'Galax 1.3',
            'staff_name': 'NgọcCM',
            'note': 'Test auto-audit log feature',
            'detail': 'Chi tiết kiểm tra tự động ghi log hoạt động'
        }
        r1 = requests.post(url_add, json=payload)
        self.assertEqual(r1.status_code, 200)

        # 2. Verify audit log was created
        url_logs = f"{BASE_URL}/api/admin/audit-logs"
        r2 = requests.get(url_logs, params={'search': 'Dương Minh Khang'})
        self.assertEqual(r2.status_code, 200)
        logs = r2.json().get('data', [])
        self.assertGreater(len(logs), 0, "Should find at least 1 activity log for Dương Minh Khang")
        latest = logs[0]
        self.assertIn('Dương Minh Khang', latest.get('description', ''))


if __name__ == '__main__':
    unittest.main()
