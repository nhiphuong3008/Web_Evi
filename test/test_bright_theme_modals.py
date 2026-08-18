"""
Test script to verify modals use bright light neutral theme.
"""
import unittest

class TestBrightThemeModals(unittest.TestCase):
    def test_students_js_no_dark_modal_bg(self):
        with open('static/js/students.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn('#111827', content)
        self.assertIn('background: #ffffff', content)

    def test_cm_portal_js_no_dark_modal_bg(self):
        with open('static/js/cm_portal.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn('#111827', content)

if __name__ == '__main__':
    unittest.main()
