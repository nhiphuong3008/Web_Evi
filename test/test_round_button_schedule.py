import sys
import os
import datetime
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import calculate_fee_expiry_date

class TestRoundButtonSchedule(unittest.TestCase):
    def test_one_session_per_week_w5(self):
        # 1 session/week (W5 = Wednesday)
        # Starting from Monday 2026-08-10, 4 remaining sessions
        # Wed 12 Aug (1), Wed 19 Aug (2), Wed 26 Aug (3), Wed 02 Sep (4)
        start_date = datetime.date(2026, 8, 10)
        res = calculate_fee_expiry_date(remaining_sessions=4, schedule_str='W5', start_from_date=start_date)
        self.assertEqual(res, '02/09/2026')
        print("\n✅ 1. Lớp 1 buổi/tuần (W5 - Thứ 4): 4 buổi bắt đầu 10/08/2026 ➔ Hạn hết phí: 02/09/2026")

    def test_two_sessions_per_week_mt5(self):
        # 2 sessions/week (MT5 = Mon & Thu)
        # Starting from Mon 2026-08-10, 4 remaining sessions
        # Mon 10 Aug (1), Thu 13 Aug (2), Mon 17 Aug (3), Thu 20 Aug (4)
        start_date = datetime.date(2026, 8, 10)
        res = calculate_fee_expiry_date(remaining_sessions=4, schedule_str='MT5', start_from_date=start_date)
        self.assertEqual(res, '20/08/2026')
        print("✅ 2. Lớp 2 buổi/tuần (MT5 - T2/T5): 4 buổi bắt đầu 10/08/2026 ➔ Hạn hết phí: 20/08/2026")

    def test_three_sessions_per_week(self):
        # 3 sessions/week (T2/T4/T6)
        # Starting from Mon 2026-08-10, 3 remaining sessions
        # Mon 10 Aug (1), Wed 12 Aug (2), Fri 14 Aug (3)
        start_date = datetime.date(2026, 8, 10)
        res = calculate_fee_expiry_date(remaining_sessions=3, schedule_str='T2/T4/T6 (Ca 5)', start_from_date=start_date)
        self.assertEqual(res, '14/08/2026')
        print("✅ 3. Lớp 3 buổi/tuần (T2/T4/T6): 3 buổi bắt đầu 10/08/2026 ➔ Hạn hết phí: 14/08/2026")

if __name__ == '__main__':
    unittest.main()
