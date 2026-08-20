import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus, ClassScheduleAdjustment
from services.db_service import get_class_lesson_log_db, get_next_study_date, get_prev_study_date

# 1. First ensure Moon 5.1 dates are 100% clean:
# Lesson 47 = 2026-08-19 (Wed)
# Lesson 48 = 2026-08-22 (Sat)
# Lesson 49 = 2026-08-26 (Wed)
# Lesson 50 = 2026-08-29 (Sat)
session = db_session()
sorted_weekdays = [2, 5]
dates = {47: datetime.date(2026, 8, 19)}
for l_num in range(46, 0, -1):
    dates[l_num] = get_prev_study_date(dates[l_num + 1], sorted_weekdays)
for l_num in range(48, 71):
    dates[l_num] = get_next_study_date(dates[l_num - 1], sorted_weekdays)

for l_num, dt in dates.items():
    session.query(LessonSyllabus).filter(
        LessonSyllabus.class_name.ilike('%Moon 5.1%'),
        LessonSyllabus.lesson_num == l_num
    ).update({'official_date': dt.strftime('%Y-%m-%d')})

session.query(ClassScheduleAdjustment).filter(
    ClassScheduleAdjustment.class_name.ilike('%Moon 5.1%')
).update({'delayed_lessons': '[]', 'current_lesson_num': None})

session.commit()
session.close()

# 2. Test day-by-day lesson mapping for Current Week (2026-08-17 to 2026-08-23)
today = datetime.date(2026, 8, 20)
start_of_week = today - datetime.timedelta(days=today.weekday()) # Monday 2026-08-17

log = get_class_lesson_log_db('Moon 5.1')
lessons = log.get('lessons', [])

print("Current week dates:")
days_order = [
    (0, 'Mon', 'Thứ 2 (MON)'),
    (1, 'Tue', 'Thứ 3 (TUE)'),
    (2, 'Wed', 'Thứ 4 (WED)'),
    (3, 'Thu', 'Thứ 5 (THU)'),
    (4, 'Fri', 'Thứ 6 (FRI)'),
    (5, 'Sat', 'Thứ 7 (SAT)'),
    (6, 'Sun', 'Chủ Nhật (SUN)')
]

for w_idx, code_day, full_day in days_order:
    target_dt = start_of_week + datetime.timedelta(days=w_idx)
    target_d_str = target_dt.strftime('%Y-%m-%d')
    target_d_disp = target_dt.strftime('%d/%m')

    # Find matching lesson on this day
    matching = [l for l in lessons if l.get('full_date') == target_d_str or l.get('date') == target_d_disp]
    if matching:
        m = matching[0]
        print(f"[{code_day} - {target_d_disp}] Match: Lesson {m['buoi']} ({m['status_label']})")
    else:
        print(f"[{code_day} - {target_d_disp}] No class")

