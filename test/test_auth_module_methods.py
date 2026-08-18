"""
Test script to verify AuthModule methods in auth.js.
"""
import unittest

class TestAuthModule(unittest.TestCase):
    def test_getUserRole_exists_in_auth_js(self):
        with open("static/js/auth.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertIn("getUserRole()", content)
        self.assertIn("getCMStaffName()", content)
        self.assertIn("isAdmin()", content)
        self.assertIn("isCM()", content)

if __name__ == '__main__':
    unittest.main()
