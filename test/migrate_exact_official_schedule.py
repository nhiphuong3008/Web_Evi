import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session, init_db
from database.models import ClassSchedule

def migrate_exact_schedule():
    init_db()
    session = db_session()
    
    # 1. Clean existing schedule records
    session.query(ClassSchedule).delete()
    session.commit()

    # Exact schedule entries from Official PDF Schedule
    entries = [
        # --- MON & THU (MT5 & MT6) ---
        # MT5 (5:30 - 7:00 PM)
        {"day": "Th 2 (MON)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Galax 1.3", "room": "Mars", "teacher": "Vn Anh", "students_count": 5, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 2 (MON)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Moon 5.2", "room": "Mercury", "teacher": "Andrew", "students_count": 11, "cm_staff": "NgcCM", "ta_staff": "Giang", "materials": "Syllabus"},
        {"day": "Th 2 (MON)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "GALAX 3.2", "room": "Jupiter", "teacher": "Jacob", "students_count": 6, "cm_staff": "AnhPTT", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 2 (MON)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 2.4", "room": "Uranus", "teacher": "Miguel", "students_count": 11, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        # MT6 (7:15 - 8:45 PM)
        {"day": "Th 2 (MON)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Sun 4.2", "room": "Mars", "teacher": "Miguel", "students_count": 4, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 2 (MON)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Moon 1.1", "room": "Uranus", "teacher": "Andrew", "students_count": 6, "cm_staff": "AnhPTT", "ta_staff": "Giang", "materials": "Syllabus"},

        {"day": "Th 5 (THU)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Galax 1.3", "room": "Mars", "teacher": "Vn Anh", "students_count": 5, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 5 (THU)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Moon 5.2", "room": "Mercury", "teacher": "Andrew", "students_count": 11, "cm_staff": "NgcCM", "ta_staff": "Giang", "materials": "Syllabus"},
        {"day": "Th 5 (THU)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "GALAX 3.2", "room": "Jupiter", "teacher": "Jacob", "students_count": 6, "cm_staff": "AnhPTT", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 5 (THU)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 2.4", "room": "Uranus", "teacher": "Miguel", "students_count": 11, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 5 (THU)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Sun 4.2", "room": "Mars", "teacher": "Miguel", "students_count": 4, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 5 (THU)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Moon 1.1", "room": "Uranus", "teacher": "Andrew", "students_count": 6, "cm_staff": "AnhPTT", "ta_staff": "Giang", "materials": "Syllabus"},

        # --- TUE & FRI (TF5 & TF6) ---
        # TF5 (5:30 - 7:00 PM)
        {"day": "Th 3 (TUE)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 2.2", "room": "Mercury", "teacher": "Jacob", "students_count": 14, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 3 (TUE)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Galax 1.4", "room": "Mars", "teacher": "Andrew", "students_count": 11, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 3 (TUE)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 4.3", "room": "Uranus", "teacher": "Thomas", "students_count": 6, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 3 (TUE)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 3.5", "room": "Jupiter", "teacher": "Miguel", "students_count": 11, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        # TF6 (7:15 - 8:45 PM)
        {"day": "Th 3 (TUE)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Galax 3.1", "room": "Mars", "teacher": "Jacob", "students_count": 6, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 3 (TUE)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Sun 4.4", "room": "Uranus", "teacher": "Andrew", "students_count": 11, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 3 (TUE)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Sun S.7", "room": "Mercury", "teacher": "Miguel", "students_count": 9, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},

        {"day": "Th 6 (FRI)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 2.2", "room": "Mercury", "teacher": "Jacob", "students_count": 14, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 6 (FRI)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Galax 1.4", "room": "Mars", "teacher": "Andrew", "students_count": 11, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 6 (FRI)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 4.3", "room": "Uranus", "teacher": "Thomas", "students_count": 6, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 6 (FRI)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 3.5", "room": "Jupiter", "teacher": "Miguel", "students_count": 11, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 6 (FRI)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Galax 3.1", "room": "Mars", "teacher": "Jacob", "students_count": 6, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 6 (FRI)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Sun 4.4", "room": "Uranus", "teacher": "Andrew", "students_count": 11, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 6 (FRI)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Sun S.7", "room": "Mercury", "teacher": "Miguel", "students_count": 9, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},

        # --- WED & SAT (WS5 & WS6) ---
        # WS5 (5:30 - 7:00 PM)
        {"day": "Th 4 (WED)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Galax 1.5", "room": "Uranus", "teacher": "Jacob", "students_count": 9, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 4 (WED)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Moon 3.1", "room": "Mercury", "teacher": "Miguel", "students_count": 11, "cm_staff": "AnhPTT", "ta_staff": "Dyn", "materials": "Syllabus"},
        {"day": "Th 4 (WED)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 1.6", "room": "Mars", "teacher": "Andrew", "students_count": 9, "cm_staff": "AnhPTT", "ta_staff": "Giang", "materials": "Syllabus"},
        {"day": "Th 4 (WED)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Lp n thi 9-10", "room": "Jupiter", "teacher": "GVVN Ms Vn", "students_count": 4, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        # WS6 (7:15 - 8:45 PM)
        {"day": "Th 4 (WED)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Sun 2.1", "room": "Uranus", "teacher": "Miguel", "students_count": 13, "cm_staff": "AnhPTT", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 4 (WED)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Moon 5.1", "room": "Mercury", "teacher": "Andrew", "students_count": 8, "cm_staff": "Vn Anh", "ta_staff": "Dyn", "materials": "Syllabus"},

        {"day": "Th 7 (SAT)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Galax 1.5", "room": "Uranus", "teacher": "Jacob", "students_count": 9, "cm_staff": "Vn Anh", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 7 (SAT)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Moon 3.1", "room": "Mercury", "teacher": "Miguel", "students_count": 11, "cm_staff": "AnhPTT", "ta_staff": "Dyn", "materials": "Syllabus"},
        {"day": "Th 7 (SAT)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Sun 1.6", "room": "Mars", "teacher": "Andrew", "students_count": 9, "cm_staff": "AnhPTT", "ta_staff": "Giang", "materials": "Syllabus"},
        {"day": "Th 7 (SAT)", "shift": "Ca 1 (17h30 - 19h00)", "class_name": "Lp n thi 9-10", "room": "Jupiter", "teacher": "GVVN Ms Vn", "students_count": 4, "cm_staff": "NgcCM", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 7 (SAT)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Sun 2.1", "room": "Uranus", "teacher": "Miguel", "students_count": 13, "cm_staff": "AnhPTT", "ta_staff": "", "materials": "Syllabus"},
        {"day": "Th 7 (SAT)", "shift": "Ca 2 (19h15 - 20h45)", "class_name": "Moon 5.1", "room": "Mercury", "teacher": "Andrew", "students_count": 8, "cm_staff": "Vn Anh", "ta_staff": "Dyn", "materials": "Syllabus"}
    ]

    for item in entries:
        shift_code = 'MT5'
        if 'Ca 2' in item['shift']:
            if 'MON' in item['day'] or 'THU' in item['day']: shift_code = 'MT6'
            elif 'TUE' in item['day'] or 'FRI' in item['day']: shift_code = 'TF6'
            elif 'WED' in item['day'] or 'SAT' in item['day']: shift_code = 'WS6'
        else:
            if 'MON' in item['day'] or 'THU' in item['day']: shift_code = 'MT5'
            elif 'TUE' in item['day'] or 'FRI' in item['day']: shift_code = 'TF5'
            elif 'WED' in item['day'] or 'SAT' in item['day']: shift_code = 'WS5'

        sc = ClassSchedule(
            day=item['day'],
            shift_code=shift_code,
            shift_name=item['shift'],
            class_name=item['class_name'],
            room=item['room'],
            teacher=item['teacher'],
            students_count=item['students_count'],
            cm_staff=item['cm_staff'],
            ta_staff=item['ta_staff'],
            materials=item['materials'],
            lesson_plan_url="https://drive.google.com/drive/folders/1JBDNHJLPorVjqbEHfHJgObhP9wsEejTz?usp=sharing"
        )
        session.add(sc)

    session.commit()
    print(f"Successfully migrated clean official schedule with {len(entries)} entries (No duplicates!)")
    session.close()

if __name__ == '__main__':
    migrate_exact_schedule()
