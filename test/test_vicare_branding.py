import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class TestVicareBranding(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_logo_asset_exists(self):
        print("\n--- Verifying Vicare Logo Asset ---")
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'logo.svg')
        self.assertTrue(os.path.exists(logo_path))
        print("✅ static/images/logo.svg exists!")

    def test_index_page_branding(self):
        print("\n--- Verifying Index Page Branding ---")
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        
        self.assertIn("Trung tâm Anh ngữ Vicare", html)
        self.assertIn("Thiết kế bởi:", html)
        self.assertIn("Nhi Phương", html)
        self.assertIn("/static/images/logo.svg", html)
        print("✅ HTML contains Vicare title, logo reference, and 'Thiết kế bởi: Nhi Phương' watermark credit!")

    def test_logo_route_static(self):
        print("\n--- Verifying Static Logo Route ---")
        res = self.client.get('/static/images/logo.svg')
        self.assertEqual(res.status_code, 200)
        self.assertIn("ANH NGỮ VICARE", res.get_data(as_text=True))
        print("✅ /static/images/logo.svg loads SVG content successfully!")

if __name__ == '__main__':
    unittest.main()
