import os, sys, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_class_lesson_log_db

test_classes = [
    "Galax 2.1", "Galax 2.2", "Moon 2.1", "Moon 2.3", "Moon 3.1",
    "Sun 1.3", "Sun 1.4", "Sun 1.5", "Sun 2.1", "Sun 2.2", "Sun 2.3",
    "Sun 3.1", "Sun 3.4", "Sun 4.1", "Sun 5.2", "Sun 5.3", "Sun 6.1"
]

print("Checking non-monotonic or anomalous dates for remaining classes...")
print("="*100)

for cname in test_classes:
    res = get_class_lesson_log_db(cname)
    lessons = res.get('lessons', [])
    if not lessons:
        continue
        
    date_issues = []
    for i in range(len(lessons) - 1):
        d1_str = lessons[i]['date']
        d2_str = lessons[i+1]['date']
        try:
            p1 = [int(x) for x in d1_str.split('/')]
            p2 = [int(x) for x in d2_str.split('/')]
            
            # Simple day/month compare (assume current year)
            if (p2[1] < p1[1]) or (p2[1] == p1[1] and p2[0] < p1[0]):
                date_issues.append((lessons[i]['buoi'], d1_str, lessons[i+1]['buoi'], d2_str))
        except:
            pass
            
    print(f"Class: {cname:12s} | Total Lessons: {len(lessons):2d} | Date anomalies: {len(date_issues)}")
    for iss in date_issues[:3]:
        print(f"    ⚠️ Lesson {iss[0]:2d} ({iss[1]}) -> Lesson {iss[2]:2d} ({iss[3]})")

