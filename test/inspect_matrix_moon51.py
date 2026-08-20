import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.db_service import get_schedule_matrix_db, get_class_lesson_log_db

matrix = get_schedule_matrix_db()
print("=== Matrix entries for Moon 5.1 ===")
for r in matrix['matrix']:
    day = r['day_full']
    for shift_name, s in [('MT5', r['mt5']), ('MT6', r['mt6'])]:
        if s and 'Moon 5.1' in s.get('class_name', ''):
            print(f"Day: {day:18} | Shift: {shift_name} | Class: {s['class_name']} | current_buoi: {s.get('current_buoi')} | is_pinned: {s.get('is_pinned')}")

print("\n=== Lesson Log for Moon 5.1 ===")
log = get_class_lesson_log_db('Moon 5.1')
for l in log['lessons']:
    if l['buoi'] in range(45, 51):
        print(f"Buoi {l['buoi']}: Date={l['date']} | Status={l['status_label']} ({l['status_code']})")
