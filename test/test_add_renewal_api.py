import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import save_renewal_db, get_renewals_db

def test_renewal():
    print("==================================================")
    print("TEST TẠO LƯỢT TÁI PHÍ MỚI VÀO CSDL SQLITE")
    print("==================================================")

    # 1. Create renewal records for Month 8/2026
    r1 = save_renewal_db({
        'student_name': 'Nguyễn Văn Minh',
        'student_code': 'EVI056',
        'class_name': 'Galax 1.3',
        'cm_staff': 'Thục Anh',
        'month': 8,
        'year': 2026,
        'status': 'success',
        'fee_package': '15,000,000đ (6 tháng)',
        'due_date': '2026-08-15',
        'notes': 'Đã đóng đủ tiền chuyển khoản'
    })
    print("Record 1:", r1)

    r2 = save_renewal_db({
        'student_name': 'Trần Bảo Anh',
        'student_code': 'EVI057',
        'class_name': 'Sun 2.2',
        'cm_staff': 'Amber',
        'month': 8,
        'year': 2026,
        'status': 'pending',
        'fee_package': '28,000,000đ (12 tháng)',
        'due_date': '2026-08-20',
        'notes': 'Phụ huynh hẹn cuối tuần nộp'
    })
    print("Record 2:", r2)

    r3 = save_renewal_db({
        'student_name': 'Lê Hoàng Nam',
        'student_code': 'EVI058',
        'class_name': 'Moon 1.1',
        'cm_staff': 'Ms. Lan',
        'month': 8,
        'year': 2026,
        'status': 'failed',
        'fee_package': '',
        'due_date': '2026-08-10',
        'notes': 'Gia đình chuyển nhà đi xa'
    })
    print("Record 3:", r3)

    # 2. Get renewal stats for Month 8/2026
    stats = get_renewals_db(month=8, year=2026)
    print("\nSummary Month 8/2026:", stats['summary'])
    print("CM Breakdown:", stats['cm_stats'])
    print("Data count:", len(stats['data']))

if __name__ == "__main__":
    test_renewal()
