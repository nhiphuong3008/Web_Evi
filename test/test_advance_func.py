import unittest
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import ClassSchedule, LessonSyllabus
from services.db_service import get_next_study_date, get_prev_study_date, get_class_lesson_log_db, get_schedule_matrix_db

def advance_class_lesson_db(class_name, lesson_num):
    """
    Nhảy Bài / Đẩy sớm tiến độ bài học:
    Đẩy Buổi lesson_num và toàn bộ các bài phía sau lên sớm 1 buổi học trong lịch học thực tế.
    """
    session = db_session()
    try:
        clean_cname = class_name.strip()
        schedules = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{clean_cname}%")).all()
        matched_syllabuses = session.query(LessonSyllabus).filter(
            LessonSyllabus.class_name.ilike(f"%{clean_cname}%")
        ).order_by(LessonSyllabus.lesson_num.asc()).all()

        if not matched_syllabuses:
            return {'success': False, 'error': f'Không tìm thấy giáo án riêng cho lớp {clean_cname}'}

        target_idx = -1
        for idx, s in enumerate(matched_syllabuses):
            if (s.lesson_num or idx + 1) == int(lesson_num):
                target_idx = idx
                break

        if target_idx <= 0:
            return {'success': False, 'error': f'Không thể đẩy sớm bài học đầu tiên (Buổi 1)'}

        # The date that session (target_idx - 1) currently has
        from services.db_service import calculate_real_class_lesson_dates
        lesson_dates, _ = calculate_real_class_lesson_dates(schedules, clean_cname, matched_syllabuses, session)
        
        # Study weekdays
        study_weekdays = set()
        for s in schedules:
            if s.day:
                day_str = s.day.lower()
                for k, v in [('mon', 0), ('tue', 1), ('wed', 2), ('thu', 3), ('fri', 4), ('sat', 5), ('sun', 6)]:
                    if k in day_str:
                        study_weekdays.add(v)
        if not study_weekdays:
            study_weekdays = {0, 3}
        sorted_weekdays = sorted(list(study_weekdays))

        # The new anchor date for target lesson is the date of (target_idx - 1)
        anchor_d = lesson_dates[target_idx - 1]

        # Shift target_idx and forward
        curr_d = anchor_d
        for idx in range(target_idx, len(matched_syllabuses)):
            matched_syllabuses[idx].official_date = curr_d.strftime('%Y-%m-%d')
            curr_d = get_next_study_date(curr_d, sorted_weekdays)

        # Ensure previous lesson is shifted backward or matches previous slot
        prev_curr_d = anchor_d
        for idx in range(target_idx - 1, -1, -1):
            prev_curr_d = get_prev_study_date(prev_curr_d, sorted_weekdays)
            matched_syllabuses[idx].official_date = prev_curr_d.strftime('%Y-%m-%d')

        session.commit()
        session.close()
        return {'success': True, 'class_name': clean_cname, 'lesson_num': int(lesson_num), 'message': f'Đã đẩy tiến độ bài học của lớp {clean_cname} từ Buổi {lesson_num} lên sớm 1 buổi thành công!'}
    except Exception as e:
        session.rollback()
        session.close()
        return {'success': False, 'message': str(e)}

print("Testing advance_class_lesson_db function...")
res = advance_class_lesson_db('Moon 5.1', 47)
print("Result:", res)

log_res = get_class_lesson_log_db('Moon 5.1')
for l in log_res['lessons']:
    if l['buoi'] in range(45, 50):
        print(f"Buoi {l['buoi']}: Date={l['date']} | Status={l['status_label']}")
