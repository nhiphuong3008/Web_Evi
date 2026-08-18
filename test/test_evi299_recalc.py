import sys
import os
import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.db_service import calculate_fee_expiry_date

exp_w5 = calculate_fee_expiry_date(8, 'W5', datetime.date(2026, 8, 14))
print(f"8 sessions in W5 (1 session/week on Wednesday) starting 14/08/2026 ➔ Expiry: '{exp_w5}'")

exp_ws5 = calculate_fee_expiry_date(8, 'WS5', datetime.date(2026, 8, 14))
print(f"8 sessions in WS5 (2 sessions/week Wed/Sat) starting 14/08/2026 ➔ Expiry: '{exp_ws5}'")
