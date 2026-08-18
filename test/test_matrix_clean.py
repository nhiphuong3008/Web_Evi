import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_schedule_matrix_db

def main():
    res = get_schedule_matrix_db()
    matrix = res.get('matrix', [])
    mon_rows = [r for r in matrix if r['day_code'] == 'Mon']
    
    print("==================================================")
    print("THỜI KHÓA BIỂU NGÀY THỨ 2 (MON) SAU KHI LÀM SẠCH DỮ LIỆU TRÙNG LẶP")
    print("==================================================")
    print(f"{'Hàng':<5} | {'Ca MT5':<16} | {'CM (MT5)':<12} | {'Ca MT6':<16} | {'CM (MT6)':<12}")
    print("-" * 75)
    for idx, r in enumerate(mon_rows):
        mt5_c = r['mt5']['class_name'] if r['mt5'] else '—'
        mt5_cm = r['mt5']['cm_staff'] if r['mt5'] else '—'
        mt6_c = r['mt6']['class_name'] if r['mt6'] else '—'
        mt6_cm = r['mt6']['cm_staff'] if r['mt6'] else '—'
        print(f"{idx+1:<5} | {mt5_c:<16} | {mt5_cm:<12} | {mt6_c:<16} | {mt6_cm:<12}")

if __name__ == "__main__":
    main()
