"""
Test Suite: Verify Fixed Endpoints (/api/classes, /api/classes/stats, /api/staff/acs, /api/student/lookup)
"""

import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


class TestFixedEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_classes_endpoint(self):
        res = self.client.get('/api/classes')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertGreater(len(data.get('data', [])), 0)

    def test_classes_stats_endpoint(self):
        res = self.client.get('/api/classes/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        stats = data.get('data', {})
        self.assertIn('by_schedule', stats)
        self.assertIn('by_room', stats)

    def test_staff_acs_endpoint(self):
        res = self.client.get('/api/staff/acs')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('average', data.get('data', {}))

    def test_student_lookup_endpoint(self):
        res = self.client.get('/api/student/lookup?query=Galax')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('homework', data)
        self.assertIn('grades', data)


if __name__ == '__main__':
    unittest.main()
