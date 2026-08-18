import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule, ClassMaster, LessonSyllabus
from services.db_service import get_class_lesson_log_db

def check_all():
    session = db_session()
    schedules = session.query(ClassSchedule).all()
    all_class_names = sorted(list(set(s.class_name for s in schedules if s.class_name)))
    
    print(f"Total unique classes in Schedule: {len(all_class_names)}\n")
    print("=" * 70)
    
    no_syll_count = 0
    match_count = 0
    
    for cname in all_class_names:
        res = get_class_lesson_log_db(cname)
        detected = res.get('detected_course')
        total_lessons = res.get('total_lessons')
        lessons = res.get('lessons', [])
        
        has_real_data = False
        if lessons and total_lessons > 0:
            first_l = lessons[0]
            # Check if it has real vocab/grammar from Excel template
            if first_l.get('vocabulary') and first_l.get('vocabulary') != '—' and 'Review Vocabulary' not in first_l.get('vocabulary'):
                has_real_data = True
                
        clean_cname = cname.encode('ascii', 'ignore').decode('ascii')
        clean_det = str(detected).encode('ascii', 'ignore').decode('ascii')
        if has_real_data:
            match_count += 1
            print(f"[MATCHED] CLASS '{clean_cname}' -> Syllabus: '{clean_det}' ({total_lessons} lessons real from Excel)")
        else:
            no_syll_count += 1
            print(f"[UNMATCHED] CLASS '{clean_cname}' -> Syllabus: '{clean_det}' (NO REAL SYLLABUS DATA)")

    print("=" * 70)
    print(f"SUMMARY: Matched {match_count}/{len(all_class_names)} classes with real Excel Syllabuses.")
    print(f"Unmatched/Fallback classes: {no_syll_count}")
    
    session.close()

if __name__ == '__main__':
    check_all()
