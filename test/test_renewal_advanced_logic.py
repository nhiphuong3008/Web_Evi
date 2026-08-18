import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import save_renewal_db, get_renewals_db

def test_advanced_logic():
    print("==================================================")
    print("TEST NGHIỆP VỤ TÁI PHÍ CHUẨN: THÀNH CÔNG, CHỒNG PHÍ, CHỜ XỬ LÝ, THẤT BẠI")
    print("==================================================")

    # 1. Add sample records for Month 9/2026
    r1 = save_renewal_db({
        'student_name': 'Trần Gia Hân',
        'student_code': 'EVI005',
        'class_name': 'Sun 2.2',
        'cm_staff': 'Vân Anh',
        'month': 9,
        'year': 2026,
        'status': 'success',
        'expected_expiry_date': '18/01/2028',
        'fee_package': '24,000,000đ (12 tháng)',
        'notes': 'Nộp học phí đúng hạn'
    })
    print("Record 1 (Thành công):", r1['data']['status_label'], "| Completed At:", r1['data']['completed_at'])

    r2 = save_renewal_db({
        'student_name': 'Trần Đỉnh Long',
        'student_code': 'EVI022',
        'class_name': 'Sun 2.1',
        'cm_staff': 'AnhPTT',
        'month': 9,
        'year': 2026,
        'status': 'stacked',
        'expected_expiry_date': '07/11/2026',
        'fee_package': '15,000,000đ (6 tháng)',
        'notes': 'Đóng tái phí trước hạn (Chồng phí khóa mới)'
    })
    print("Record 2 (Chồng phí):", r2['data']['status_label'], "| Completed At:", r2['data']['completed_at'])

    r3 = save_renewal_db({
        'student_name': 'Nguyễn Công Hải',
        'student_code': 'EVI024',
        'class_name': 'Galax 1.1',
        'cm_staff': 'Naomi',
        'month': 9,
        'year': 2026,
        'status': 'failed',
        'expected_expiry_date': '10/09/2026',
        'notes': 'Phụ huynh báo hết khóa dừng học'
    })
    print("Record 3 (Thất bại):", r3['data']['status_label'], "| Completed At:", r3['data']['completed_at'])

    # 2. Get renewal stats for Month 9/2026
    res = get_renewals_db(month=9, year=2026)
    summary = res['summary']
    print("\nSummary Month 9/2026:")
    print("  📋 Tổng đến hạn:", summary['due'])
    print("  🟢 Thành công:", summary['success'])
    print("  🔵 Chồng phí:", summary['stacked'])
    print("  🟢 Total Effective Success:", summary['effective_success'])
    print("  🔴 Thất bại:", summary['failed'])
    print("  📈 Tỉ lệ % Tái phí chuẩn:", summary['rate'], "%")

    # Assert expected formula: (1 success + 1 stacked) / 3 due = 66.7%
    assert summary['effective_success'] == 2, "Effective success count should be 2"
    assert summary['rate'] == 66.7, f"Expected 66.7%, got {summary['rate']}%"
    print("\n✅ KIỂM THỬ THÀNH CÔNG! CÔNG THỨC TÍNH TỈ LỆ TÁI PHÍ CHUẨN ĐẠT 100%!")

if __name__ == '__main__':
    test_advanced_logic()
