"""
Test script to verify that portal-subtabs bar has been removed from cm_portal.js.
"""
import unittest

class TestSubtabsRemoval(unittest.TestCase):
    def test_portal_subtabs_removed(self):
        with open("static/js/cm_portal.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertNotIn("portal-subtabs", content)

if __name__ == "__main__":
    unittest.main()
