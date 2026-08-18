import os
import sys

sys.path.insert(0, os.path.abspath('.'))
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import (
    get_monthly_renewal_pdf_data_db,
    get_student_interaction_timeline_db,
)

print('=== 1. CHECK TIMELINE FOR BÙI KHÁNH LY (EVI241) ===')
res_timeline = get_student_interaction_timeline_db('EVI241')
timeline = res_timeline.get('timeline', [])
print(f'Retrieved {len(timeline)} timeline items for EVI241:')
for t in timeline:
    print(
        f"  [ID #{t['id']}] {t['created_at']} | Staff: {t['staff_name']} | Detail: {t['detail']}"
    )

assert (
    len(timeline) >= 1
), 'Expected at least 1 timeline item for Bùi Khánh Ly (EVI241)'
assert (
    timeline[0]['id'] == 227
), f"Expected log ID #227 for Bùi Khánh Ly, got #{timeline[0]['id']}"
print(
    '-> PASS! Bùi Khánh Ly (EVI241) timeline matched log #227 perfectly! 🚀'
)


print('\n=== 2. CHECK RENEWAL PDF REPORT FOR BÙI KHÁNH LY ===')
pdf_res = get_monthly_renewal_pdf_data_db(month=8, year=2026)
data = pdf_res.get('data', [])
found_ly = False
for r in data:
    if 'Khánh Ly' in r.get('student_name', '') or r.get(
        'student_code'
    ) == 'EVI241':
        found_ly = True
        print(f"Found Bùi Khánh Ly in Month 8/2026 renewals:")
        print(f"  Mã HS: {r.get('student_code')}")
        print(f"  Tên HS: {r.get('student_name')}")
        print(f"  Latest interaction: {r.get('latest_interaction')}")
        assert (
            r.get('latest_interaction') is not None
        ), 'Expected non-null latest_interaction for Bùi Khánh Ly'

assert (
    found_ly
), 'Expected Bùi Khánh Ly to be found in Month 8/2026 renewal list'
print(
    '-> PASS! Latest interaction snippet correctly attached to Bùi Khánh Ly! 🚀'
)

print('\nALL VERIFICATION TESTS PASSED 100%! 🚀')
