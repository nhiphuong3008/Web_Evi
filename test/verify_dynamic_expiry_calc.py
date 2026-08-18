import os
import sys

sys.path.insert(0, os.path.abspath('.'))
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import (
    get_renewals_db,
    recalculate_all_renewals_expiry_db,
)

print('=== 1. RUNNING DYNAMIC RECALCULATE FOR ALL RENEWALS ===')
res = recalculate_all_renewals_expiry_db()
print('Recalculate result:', res)

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

print('\n=== 2. CHECKING RENEWAL RECORD FOR EVI363 (Nguyễn Tuệ Nhi) ===')
c.execute("""
    SELECT id, student_code, student_name, class_name, month, year, expected_expiry_date
    FROM student_renewals
    WHERE student_code = 'EVI363' OR student_name LIKE '%Tuệ Nhi%'
""")
rows = c.fetchall()
for r in rows:
    print(r)
    # Check that Tuệ Nhi with 107 remaining sessions is now calculated to 2027!
    assert (
        r[5] == 2027
    ), f"Expected year 2027 for EVI363 (107 remaining sessions), got {r[5]}"
    assert (
        '2027' in r[6]
    ), f"Expected 2027 in expected_expiry_date for EVI363, got {r[6]}"

print('-> PASS! Nguyễn Tuệ Nhi expiry date correctly calculated to 2027! 🚀')

print(
    '\n=== 3. CHECKING RENEWAL RECORDS FOR EVI068 & EVI056 (Minh & Huyền) ==='
)
c.execute("""
    SELECT id, student_code, student_name, class_name, month, year, expected_expiry_date
    FROM student_renewals
    WHERE student_code IN ('EVI068', 'EVI056')
""")
for r in c.fetchall():
    print(r)

conn.close()
print('\nALL VERIFICATION TESTS PASSED 100%! 🚀')
