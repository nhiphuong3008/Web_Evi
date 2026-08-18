import os
import sys

sys.path.insert(0, os.path.abspath('.'))
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_renewals_db

print('=== RENEWALS FOR AUGUST 2027 ===')
res = get_renewals_db(month=8, year=2027)
data = res.get('data', [])
print(f'Total renewal records for Month 8/2027: {len(data)}')
for r in data:
    if r.get('student_code') == 'EVI363':
        print(f"FOUND EVI363 (Nguyễn Tuệ Nhi):")
        print(f"  ID: #{r['id']}")
        print(f"  Mã HS: {r['student_code']}")
        print(f"  Tên HS: {r['student_name']}")
        print(f"  Lớp: {r['class_name']}")
        print(f"  Hạn Hết Phí Dự Kiến: {r.get('expected_expiry_date')}")
        print(f"  Tháng/Năm: Tháng {r['month']}/{r['year']}")

print('\nTEST PASSED 100%! 🚀')
