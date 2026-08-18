import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_class_lesson_log_db

def test_api():
    res = get_class_lesson_log_db("Sun 2.1")
    print("Class: Sun 2.1")
    print(f"Success: {res.get('success')}")
    print(f"Detected Course: {res.get('detected_course')}")
    print(f"Total Lessons: {res.get('total_lessons')}")
    
    lessons = res.get('lessons', [])
    print(f"First 4 Lessons Preview:")
    for l in lessons[:4]:
        print(f"\n- Buoi {l['buoi']}: {l['lesson_title']} | {l['unit_name']} (Trang {l['pages']})")
        print(f"  Vocab: {l['vocabulary']}")
        print(f"  Grammar: {l['grammar']}")
        print(f"  Target: {l['lesson_target']}")

if __name__ == '__main__':
    test_api()
