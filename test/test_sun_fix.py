import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import get_class_lesson_log_db

for cname in ['Sun 4.3', 'Sun 3.5']:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    print(f"\n==================================================")
    print(f"  Lớp: {cname} ({len(lessons)} buổi)")
    print(f"==================================================")
    for l in lessons:
        if l.get('buoi') in [48, 49, 50, 51, 52] or l.get('status_code') == 'today':
            b = l['buoi']
            d = l['date']
            st = l['status_label']
            un = l['unit_name'].replace('\n', ' ')
            hw = l['homework_note'].replace('\n', ' ')
            print(f"  Buổi {b:2d} | Ngày: {d} | Status: {st:25s} | Unit: {un[:25]:25s} | HW: {hw}")
