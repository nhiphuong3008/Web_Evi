import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_dashboard_summary

def test_summary():
    print("==================================================================")
    print("🧪 KIỂM THỬ ĐỒNG BỘ DỮ LIỆU DASHBOARD TỔNG QUAN VỚI CSDL MẸ")
    print("==================================================================")

    res = get_dashboard_summary()
    kpi = res.get('kpi', {})
    acs = res.get('acs_stats', {})

    print(f"  • Tổng học sinh: {kpi.get('total_students')} (Expected: 236)")
    print(f"  • Lớp đang hoạt động: {kpi.get('active_classes')} (Expected: 21)")
    print(f"  • Tỷ lệ tái phí T8/2026: {kpi.get('latest_renewal_rate')}%")
    print(f"  • Điểm ACS trung bình: {kpi.get('avg_acs')}")
    print(f"  • Danh sách CM ACS: {[s['name'] for s in acs.get('staff', [])]}")

    assert kpi.get('total_students') == 236, f"Expected 236 active students, got {kpi.get('total_students')}"
    assert kpi.get('active_classes') == 21, f"Expected 21 active classes, got {kpi.get('active_classes')}"
    assert 'AnhNV' in [s['name'] for s in acs.get('staff', [])], "Expected 'AnhNV' in ACS staff list"

    print("==================================================================")
    print("🎉 DỮ LIỆU DASHBOARD ĐÃ ĐỒNG BỘ CHUẨN XÁC 100% VỚI CÁC MỤC MENU!")
    print("==================================================================")

if __name__ == '__main__':
    test_summary()
