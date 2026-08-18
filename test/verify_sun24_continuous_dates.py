import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_class_lesson_log_db

def test_sun24():
    res = get_class_lesson_log_db("Sun 2.4")
    lessons = res.get('lessons', [])
    
    print(f"Class: Sun 2.4 | Total lessons found: {len(lessons)}")
    print("=" * 70)
    
    for l in lessons:
        b = l['buoi']
        if 26 <= b <= 32:
            print(f"  Lesson {b:2d} | Date: {l['date']} | Unit: {l['unit_name'][:30].encode('ascii','ignore').decode('ascii')}")

if __name__ == '__main__':
    test_sun24()
