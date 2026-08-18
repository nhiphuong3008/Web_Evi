"""
Test script to verify CM term is defined as Class Manager across all UI templates and APIs.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class TestClassManagerTerm(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_sidebar_nav_term(self):
        """Verify index.html sidebar displays Class Manager (CM)."""
        with open(os.path.join(self.app.root_path, 'static', 'index.html'), 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('Class Manager (CM)', html)
        self.assertNotIn('Care Manager (CM)', html)
        print("\n✅ PASS: Sidebar nav label contains 'Class Manager (CM)'")

    def test_user_management_role_term(self):
        """Verify user management modal dropdown displays Class Manager (CM)."""
        with open(os.path.join(self.app.root_path, 'static', 'js', 'users.js'), 'r', encoding='utf-8') as f:
            js = f.read()
        self.assertIn('Class Manager (CM)', js)
        self.assertNotIn('Care Manager (CM)', js)
        print("✅ PASS: User management role option contains 'Class Manager (CM)'")

    def test_export_report_term(self):
        """Verify export student report displays Class Manager (CM)."""
        res = self.client.get('/api/students/EVI069/export?format=pdf')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('CLASS MANAGER (CM)', html)
        self.assertNotIn('CARE MANAGER (CM)', html)
        print("✅ PASS: Student report HTML contains 'CLASS MANAGER (CM)'")

if __name__ == '__main__':
    unittest.main()
