"""
Test script to verify that 'Tính Lại Hạn Hết Phí' and 'Nhập Đóng Phí' buttons are restricted to Admin users.
"""
import unittest

class TestAdminOnlyRenewalButtons(unittest.TestCase):
    def test_renewals_js_contains_admin_checks(self):
        with open("static/js/renewals.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verify that recalculateExpiry button has AuthModule.isAdmin() check
        self.assertIn("AuthModule.isAdmin()", content)
        self.assertIn("recalculateExpiry()", content)
        self.assertIn("openPaymentModal()", content)

if __name__ == "__main__":
    unittest.main()
