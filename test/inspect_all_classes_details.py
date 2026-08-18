import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_cm_classes_db

def main():
    res = get_cm_classes_db('', include_ended=False)
    classes = res.get('data', [])
    print(f"Tổng số {len(classes)} lớp đang hoạt động:\n")
    print(f"{'STT':<4} | {'Tên Lớp':<18} | {'Phụ Trách CM':<15} | {'Giáo Viên':<15} | {'Số HS':<6}")
    print("-" * 70)
    for idx, c in enumerate(classes):
        print(f"{idx+1:<4} | {c['class_name']:<18} | {c.get('cm_staff') or 'Chưa phân công':<15} | {c.get('teacher') or '—':<15} | {c.get('student_count', 0):<6}")

if __name__ == "__main__":
    main()
