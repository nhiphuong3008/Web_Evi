import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class TestPdfReportSync(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_renewals_pdf_report(self):
        print("\n--- Testing Renewals PDF Report Endpoint ---")
        res = self.client.get('/api/renewals/report-pdf?month=8&year=2026')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn("TRUNG TÂM ANH NGỮ VICARE", html)
        self.assertIn("/static/images/logo.jpg", html)
        self.assertIn("Thiết kế bởi:", html)
        self.assertIn("Nhi Phương", html)
        print("✅ Renewals PDF Report contains Vicare logo, title and Nhi Phương watermark credit!")

    def test_student_report_pdf(self):
        print("\n--- Testing Student Printable Report PDF ---")
        from services.export_service import generate_printable_html_report
        sample_student = {'full_name': 'Lương Minh Hưng', 'code': 'EVI198', 'class_name': 'Moon 5.2'}
        html = generate_printable_html_report(sample_student)

        self.assertIn("TRUNG TÂM ANH NGỮ VICARE", html)
        self.assertIn("/static/images/logo.jpg", html)
        self.assertIn("Thiết kế bởi:", html)
        self.assertIn("Nhi Phương", html)
        print("✅ Student Report PDF contains Vicare logo, title and Nhi Phương watermark credit!")

if __name__ == '__main__':
    unittest.main()
