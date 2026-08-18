import os
import sys

sys.path.insert(0, os.path.abspath('.'))
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_renewals_db

print("=== CHECK RENEWALS FOR MONTH 9/2026 FOR MINH & HUYEN ===")
res_m9 = get_renewals_db(month=9, year=2026)
data_m9 = res_m9.get('data', [])

print(f"Total renewals records for Month 9/2026: {len(data_m9)}")

target_students = ['EVI068', 'EVI056']
found = [r for r in data_m9 if r.get('student_code') in target_students]

for r in found:
    print(f"\nFound renewal record #{r['id']}:")
    print(f"  Mã HS: {r['student_code']}")
    print(f"  Tên HS: {r['student_name']}")
    print(f"  Lớp chính: {r['class_name']}")
    print(f"  Tháng/Năm Tái phí: Tháng {r['month']}/{r['year']}")
    print(f"  Hạn Hết Phí Dự Kiến: {r.get('expected_expiry_date')}")

assert len(found) == 2, f"Expected 2 records for EVI068 and EVI056 in Month 9/2026, found {len(found)}"
print("\nVERIFICATION SUCCESSFUL! 🚀")
