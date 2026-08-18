import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_class_lesson_log_db, toggle_delay_class_lesson_db

def test_official_and_delay():
    test_classes = ['Galax 1.4', 'Galax 3.2', 'Galax 1.3', 'Sun 2.4']
    
    print("--- STEP 1: Check initial dates from Official Syllabuses ---")
    for cname in test_classes:
        res = get_class_lesson_log_db(cname)
        lessons = res.get('lessons', [])
        print(f"\nClass '{cname}': Total {len(lessons)} lessons")
        for l in lessons[:5]:
            st = l['status_label'].encode('ascii', 'ignore').decode('ascii')
            print(f"  Buoi {l['buoi']}: {l['date']} -> {st}")

    print("\n--- STEP 2: Simulate Delaying Lesson 3 for 'Galax 1.4' ---")
    toggle_delay_class_lesson_db('Galax 1.4', 3)
    
    res_after = get_class_lesson_log_db('Galax 1.4')
    lessons_after = res_after.get('lessons', [])
    print(f"\nClass 'Galax 1.4' AFTER DELAYING LESSON 3:")
    for l in lessons_after[:6]:
        st = l['status_label'].encode('ascii', 'ignore').decode('ascii')
        print(f"  Buoi {l['buoi']}: {l['date']} -> {st}")

    # Clean up test delay
    toggle_delay_class_lesson_db('Galax 1.4', 3)
    print("\n[SUCCESS] Cleaned up test delay for 'Galax 1.4'.")

if __name__ == '__main__':
    test_official_and_delay()
