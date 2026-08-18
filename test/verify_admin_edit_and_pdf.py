import os
import sys

sys.path.insert(0, os.path.abspath('.'))
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
app = create_app()
from services.db_service import (
    add_parent_interaction_log_db,
    get_monthly_renewal_pdf_data_db,
    update_parent_interaction_log_db,
)

print('=== 1. TESTING UPDATE INTERACTION FOR ADMIN ===')
# Add a test interaction
add_res = add_parent_interaction_log_db(
    student_code='EVI363',
    student_name='Nguyễn Tuệ Nhi',
    staff_name='Vân Anh',
    note='Tương tác ban đầu',
    detail='Phụ huynh phản hồi khá hài lòng',
)
assert add_res.get('success'), f"Add failed: {add_res}"
log_id = add_res['data']['id']
print(f'Created test interaction log #{log_id}')

# Now edit it using update_parent_interaction_log_db
upd_res = update_parent_interaction_log_db(
    log_id=log_id,
    staff_name='Amber',
    note='Đã cập nhật tái phí',
    detail='Phụ huynh đồng ý gia hạn gói 48 buổi mới vào ngày 15/09/2026.',
)
assert upd_res.get('success'), f"Update failed: {upd_res}"
print(f'Updated interaction log #{log_id}:', upd_res['data'])

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()
c.execute(
    'SELECT staff_name, note, interaction_detail FROM parent_interaction_logs WHERE id = ?',
    (log_id,),
)
row = c.fetchone()
conn.close()

assert row[0] == 'Amber', f'Expected staff Amber, got {row[0]}'
assert (
    row[1] == 'Đã cập nhật tái phí'
), f'Expected note Đã cập nhật tái phí, got {row[1]}'
print('-> PASS! Admin update interaction log verified 100%! ✏️')


print('\n=== 2. TESTING GET MONTHLY RENEWAL PDF REPORT DATA ===')
pdf_data_res = get_monthly_renewal_pdf_data_db(month=8, year=2026)
assert pdf_data_res.get('success'), f'PDF data failed: {pdf_data_res}'
print(
    f"Retrieved {pdf_data_res.get('count')} records for Month 8/2026 PDF report."
)
for r in pdf_data_res.get('data', [])[:3]:
    print(
        f"  HS: {r.get('student_name')} ({r.get('student_code')}) | Lớp: {r.get('class_name')} | Care gần nhất: {r.get('latest_interaction')}"
    )

print('-> PASS! Monthly renewal PDF report data verified! 📊')


print('\n=== 3. TESTING FLASK API ENDPOINTS WITH CLIENT ===')
client = app.test_client()

# Test POST /api/interactions/update/<id>
res_api = client.post(
    f'/api/interactions/update/{log_id}',
    json={
        'staff_name': 'Thục Anh',
        'note': 'Chăm sóc định kỳ',
        'detail': 'Đã hoàn tất gọi điện phụ huynh',
    },
)
assert res_api.status_code == 200, f'API status {res_api.status_code}'
data_json = res_api.get_json()
assert data_json.get('success'), f'API json failed: {data_json}'
print(f'API POST /api/interactions/update/{log_id} SUCCESS!')

# Test GET /api/renewals/report-pdf
res_pdf = client.get('/api/renewals/report-pdf?month=8&year=2026')
assert res_pdf.status_code == 200, f'PDF status {res_pdf.status_code}'
html_text = res_pdf.get_data(as_text=True)
assert (
    'BÁO CÁO TỔNG HỢP THEO DÕI TÁI PHÍ HỌC SINH' in html_text
), 'Missing PDF header title'
assert 'In Báo Cáo / Lưu PDF' in html_text, 'Missing print PDF button'
# Test POST /api/interactions/delete/<id>
res_del_api = client.post(f'/api/interactions/delete/{log_id}')
assert res_del_api.status_code == 200, f"Delete API status {res_del_api.status_code}"
data_del_json = res_del_api.get_json()
assert data_del_json.get('success'), f"Delete API json failed: {data_del_json}"
print(f"API POST /api/interactions/delete/{log_id} SUCCESS! Deleted log from SQLite DB!")

print('\nALL VERIFICATION TESTS PASSED 100%! 🚀')
