"""
Test script to audit all PDF and Printable report headers, center names, and logo paths.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class TestReportHeaders(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_unit_test_pdf_report_header(self):
        """Verify Sun/Galax unit test PDF report includes official logo and center name."""
        res = self.client.get('/api/students/EVI069/test-report-pdf?test_name=Midterm&class_name=GALAX+3.2')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('TRUNG TÂM ANH NGỮ VICARE', html)
        self.assertIn('VICARE ENGLISH CENTER', html)
        self.assertIn('/static/images/logo.jpg', html)
        self.assertIn('GALAX UNIT TEST', html)
        print("\n✅ PASS: Unit Test PDF report header contains 'TRUNG TÂM ANH NGỮ VICARE' & logo.jpg")

    def test_moon_unit_test_pdf_report_header(self):
        """Verify Moon unit test PDF report includes official logo and center name."""
        res = self.client.get('/api/students/EVI069/test-report-pdf?is_moon=1&test_name=Unit+01&class_name=MOON+1.1')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('TRUNG TÂM ANH NGỮ VICARE', html)
        self.assertIn('VICARE ENGLISH CENTER', html)
        self.assertIn('/static/images/logo.jpg', html)
        print("✅ PASS: Moon Unit Test PDF report header contains 'TRUNG TÂM ANH NGỮ VICARE' & logo.jpg")

    def test_comprehensive_student_report_header(self):
        """Verify 360 Student report export PDF includes official logo and center name."""
        res = self.client.get('/api/students/EVI069/export?format=pdf')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('TRUNG TÂM ANH NGỮ VICARE', html)
        self.assertIn('VICARE ENGLISH CENTER', html)
        self.assertIn('/static/images/logo.jpg', html)
        print("✅ PASS: Student 360 Comprehensive report contains 'TRUNG TÂM ANH NGỮ VICARE' & logo.jpg")

    def test_renewals_report_header(self):
        """Verify Renewals report PDF includes official logo and center name."""
        res = self.client.get('/api/renewals/report-pdf')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('TRUNG TÂM ANH NGỮ VICARE', html)
        self.assertIn('VICARE ENGLISH CENTER', html)
        self.assertIn('/static/images/logo.jpg', html)
        print("✅ PASS: Renewals report PDF contains 'TRUNG TÂM ANH NGỮ VICARE' & logo.jpg")

if __name__ == '__main__':
    unittest.main()
