import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_class_lesson_log_db

def test_galax13():
    res = get_class_lesson_log_db("Galax 1.3")
    lessons = res.get('lessons', [])
    
    print(f"Class: Galax 1.3 | Total lessons found: {len(lessons)}")
    print("=" * 70)
    
    for l in lessons:
        if l['buoi'] == 24 or l['date'] == '06/08':
            print(f"[FOUND] LESSON {l['buoi']} (Date: {l['date']}):")
            print(f"   Unit Name: {l['unit_name'].encode('ascii', 'ignore').decode('ascii')}")
            print(f"   Pages: {l['pages'].encode('ascii', 'ignore').decode('ascii')}")
            print(f"   Vocab: {l['vocabulary'].encode('ascii', 'ignore').decode('ascii')}")
            print(f"   Grammar: {l['grammar'].encode('ascii', 'ignore').decode('ascii')}")
            print(f"   Homework: {l['homework_note'].encode('ascii', 'ignore').decode('ascii')}")
            print()

if __name__ == '__main__':
    test_galax13()
