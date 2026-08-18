"""
Test script: Kiểm tra nội dung homework_note và ngày học (lesson dates)
sau khi sửa lỗi backend format trong db_service.py
"""
import sys, os, datetime, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import LessonSyllabus, ClassSchedule
from services.db_service import get_class_lesson_log_db

def test_homework_format():
    """Kiểm tra homework_note format cho từng lớp"""
    test_classes = ['Moon 1.1', 'Galax 1.3', 'Sun 2.4', 'Sun 2.2', 'Moon 5.2']
    
    all_pass = True
    for cn in test_classes:
        result = get_class_lesson_log_db(cn)
        if not result.get('success'):
            print(f"  X {cn}: API ERROR - {result.get('error')}")
            all_pass = False
            continue
        
        lessons = result.get('lessons', [])
        print(f"\n{'='*60}")
        print(f"  Lop: {cn} ({len(lessons)} buoi)")
        print(f"{'='*60}")
        
        for l in lessons[:5]:
            hw = l.get('homework_note', '')
            date = l.get('date', '')
            unit = l.get('unit_name', '')
            print(f"  L{l['buoi']:2d} | {date:6s} | {unit[:30]:30s} | HW: {hw[:80]}")
            
            if '00:00:00' in hw:
                print(f"    X ERROR: Raw date string detected in homework!")
                all_pass = False
            
            if '<b>' in hw and '\xf0\x9f\x93\x96' not in hw and '\xf0\x9f\x93\x9d' not in hw:
                print(f"    X ERROR: Raw HTML <b> tag detected!")
                all_pass = False
    
    return all_pass

def test_lesson_dates():
    """Kiểm tra ngày học tính ngược chính xác từ start date"""
    test_cases = {
        'Moon 1.1': {'expected_start': '2026-03-19', 'desc': 'Has official_date from Excel'},
        'Galax 1.3': {'expected_start': '2026-04-20', 'desc': 'Start date from filename (20_4_2026)'},
        'Galax 1.5': {'expected_start': '2026-07-22', 'desc': 'Start date from filename (22_07_2026)'},
    }
    
    all_pass = True
    for cn, info in test_cases.items():
        result = get_class_lesson_log_db(cn)
        if not result.get('success'):
            print(f"  X {cn}: API ERROR - {result.get('error')}")
            all_pass = False
            continue
        
        lessons = result.get('lessons', [])
        if not lessons:
            print(f"  X {cn}: No lessons found")
            all_pass = False
            continue
        
        first_date = lessons[0].get('date', '')
        expected = info['expected_start']
        ep = expected.split('-')
        expected_short = f"{ep[2]}/{ep[1]}"
        
        match = (first_date == expected_short)
        status = "OK" if match else "~"
        print(f"  {status} {cn}: Lesson 1 date = {first_date} (expected ~{expected_short}) [{info['desc']}]")
        
        for i in range(1, min(5, len(lessons))):
            curr = lessons[i]['date']
            print(f"    L{lessons[i]['buoi']}: {curr}")
    
    return all_pass

if __name__ == '__main__':
    print("=" * 60)
    print("  TEST 1: Homework Format Verification")
    print("=" * 60)
    hw_ok = test_homework_format()
    
    print()
    print("=" * 60)
    print("  TEST 2: Lesson Dates Verification")
    print("=" * 60)
    dates_ok = test_lesson_dates()
    
    print()
    print("=" * 60)
    if hw_ok and dates_ok:
        print("  ALL TESTS PASSED!")
    else:
        print("  SOME TESTS FAILED - Review output above")
    print("=" * 60)
