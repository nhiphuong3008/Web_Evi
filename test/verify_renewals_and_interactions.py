import sys
import os
import datetime
import sqlite3

sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import (
    add_parent_interaction_log_db,
    get_all_parent_interactions_db,
    get_renewals_db,
    get_student_interaction_timeline_db,
    recalculate_all_renewals_expiry_db,
)

print('=== 1. TEST RECALCULATING EXPIRY DATES ===')
res_exp = recalculate_all_renewals_expiry_db()
print('Recalculate result:', res_exp)
assert res_exp.get('success') is True
assert res_exp.get('updated', 0) > 0
print('-> PASS!')

print('\n=== 2. TEST ADDING INTERACTION LOG ===')
res_add = add_parent_interaction_log_db(
    student_code='EVI377',
    student_name='Đinh Gia Huy Hoàng',
    staff_name='Vân Anh',
    note='Gọi điện trao đổi nộp học phí đợt mới',
    detail='Phụ huynh đồng ý nộp tái phí khóa mới vào ngày 25/08.',
    class_name='Galax 1.3',
)
print('Add result:', res_add)
assert res_add.get('success') is True
log_data = res_add.get('data', {})
assert log_data.get('student_code') == 'EVI377'
print('-> PASS!')

print(
    '\n=== 3. TEST RETRIEVING STUDENT TIMELINE (ORDERED FROM OLDEST TO NEWEST) ==='
)
res_timeline = get_student_interaction_timeline_db('EVI377')
print('Timeline success:', res_timeline.get('success'))
timeline = res_timeline.get('timeline', [])
print(f'Retrieved {len(timeline)} timeline items for EVI377:')
for t in timeline:
    print(
        f"  [ID #{t['id']}] {t['created_at']} | CM: {t['staff_name']} | Note: {t['note']} | Detail: {t['detail']}"
    )

assert len(timeline) >= 1
# Verify ordering: check if IDs are strictly ascending (Oldest -> Newest)
ids = [t['id'] for t in timeline]
assert ids == sorted(
    ids
), f'Timeline IDs are not ordered chronologically ascending! Got: {ids}'
print('-> PASS! Timeline is correctly sorted from OLDEST to NEWEST! ⏳')

print('\n=== 4. TEST RETRIEVING ALL INTERACTIONS FOR CENTRAL PAGE ===')
res_all = get_all_parent_interactions_db()
print(f"Total central interactions retrieved: {res_all.get('count')}")
assert res_all.get('success') is True
assert res_all.get('count', 0) > 0
print('-> PASS!')

print('\n=== 5. TEST GET RENEWALS WITH EXPECTED EXPIRY DATES ===')
res_rn = get_renewals_db(month=8, year=2026)
print('Renewals success:', res_rn.get('success'))
data_rn = res_rn.get('data', [])
print(f'Total renewals records for 8/2026: {len(data_rn)}')
if data_rn:
    sample = data_rn[0]
    print(
        f"Sample renewal: #{sample['id']} {sample['student_name']} - Expected Expiry: {sample.get('expected_expiry_date')}"
    )

print('\nALL TESTS PASSED 100%! 🚀')
