import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_class_lesson_log_db

def test_moon52():
    res = get_class_lesson_log_db("Moon 5.2")
    lessons = res.get('lessons', [])
    
    print(f"Class: Moon 5.2 | Total lessons found: {len(lessons)}")
    print("=" * 70)
    
    lesson_8 = None
    for l in lessons:
        if l['buoi'] == 8 or '8' in str(l['buoi']):
            lesson_8 = l
            break
            
    if lesson_8:
        print(f"[FOUND] LESSON 8 for Moon 5.2:")
        print(f"   Buoi: {lesson_8['buoi']}")
        print(f"   Date: {lesson_8['date']}")
        print(f"   Unit Name: {lesson_8['unit_name'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"   Pages: {lesson_8['pages']}")
        print(f"   Vocab: {lesson_8['vocabulary'][:120].encode('ascii', 'ignore').decode('ascii')}...")
        print(f"   Grammar: {lesson_8['grammar'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"   Target: {lesson_8['lesson_target'][:120].encode('ascii', 'ignore').decode('ascii')}")
        print(f"   Homework: {lesson_8['homework_note'].encode('ascii', 'ignore').decode('ascii')}")
    else:
        print("❌ LESSON 8 NOT FOUND!")

if __name__ == '__main__':
    test_moon52()
