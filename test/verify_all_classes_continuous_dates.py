import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_class_lesson_log_db

def test_multiple():
    test_classes = ["Galax 1.3", "Moon 5.2", "Sun 4.2", "Moon 1.1", "Galax 3.1", "Sun 2.4"]
    
    for cname in test_classes:
        res = get_class_lesson_log_db(cname)
        lessons = res.get('lessons', [])
        print(f"\n==========================================")
        print(f"Class: {cname} | Total lessons: {len(lessons)}")
        print(f"------------------------------------------")
        
        # Check if dates strictly increase chronologically
        date_issues = 0
        for i in range(len(lessons) - 1):
            d1_str = lessons[i]['date']
            d2_str = lessons[i+1]['date']
            
            p1 = [int(x) for x in d1_str.split('/')]
            p2 = [int(x) for x in d2_str.split('/')]
            
            # Simple day/month compare
            if (p2[1] < p1[1]) or (p2[1] == p1[1] and p2[0] <= p1[0]):
                date_issues += 1
                print(f"  [ISSUE] at Lesson {lessons[i]['buoi']} ({d1_str}) -> Lesson {lessons[i+1]['buoi']} ({d2_str})")
                
        if date_issues == 0:
            print(f"  [SUCCESS] Perfect! All dates are strictly continuous and chronological!")
            # Print sample range around August
            for l in lessons:
                if l['date'] in ['03/08', '04/08', '05/08', '06/08', '07/08', '10/08', '11/08', '12/08', '13/08']:
                    print(f"     Lesson {l['buoi']:2d} | Date: {l['date']} | Unit: {l['unit_name'][:30].encode('ascii','ignore').decode('ascii')}")

if __name__ == '__main__':
    test_multiple()
