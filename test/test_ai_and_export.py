import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from database.db_manager import init_db

app = create_app()

class TestAIAndExport(unittest.TestCase):

    def setUp(self):
        init_db()
        self.client = app.test_client()

    def test_01_student_360_detail_with_ai(self):
        res = self.client.get('/api/students/EVI056')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('ai_assessment', data)
        ai = data['ai_assessment']
        self.assertIn('summary', ai)
        self.assertIn('strengths', ai)
        self.assertIn('improvements', ai)
        self.assertIn('recommendations', ai)
        print("\n[TEST 1] AI Assessment generated successfully for EVI056:")
        print(f"  - Level: {ai.get('level_evaluation')}")
        print(f"  - Summary: {ai.get('summary')}")
        print(f"  - Strengths: {ai.get('strengths')}")

    def test_02_export_pdf_html(self):
        res = self.client.get('/api/students/EVI056/export?format=pdf')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/html', res.content_type)
        content = res.data.decode('utf-8')
        self.assertIn('BÁO CÁO KẾT QUẢ HỌC TẬP HỌC SINH', content)
        self.assertIn('Nguyễn Ngọc Huyền', content)
        print("\n[TEST 2] Printable PDF/HTML report generated successfully (length: ", len(content), ")")

    def test_03_export_word(self):
        res = self.client.get('/api/students/EVI056/export?format=word')
        self.assertEqual(res.status_code, 200)
        self.assertIn('msword', res.content_type)
        print("\n[TEST 3] Word report generated successfully (bytes: ", len(res.data), ")")

    def test_04_export_excel(self):
        res = self.client.get('/api/students/EVI056/export?format=excel')
        self.assertEqual(res.status_code, 200)
        self.assertIn('csv', res.content_type)
        content = res.data.decode('utf-8')
        self.assertIn('BÁO CÁO HỌC TẬP HỌC SINH EVI ACADEMY', content)
        print("\n[TEST 4] Excel CSV report generated successfully (length: ", len(content), ")")

if __name__ == '__main__':
    unittest.main()
