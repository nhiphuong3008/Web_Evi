import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule
from services.db_service import get_class_lesson_log_db

def test_dates():
    sample_classes = ['Galax 1.4', 'Galax 1.3', 'Sun 1.4', 'Moon 3.1', 'Sun 2.1']
    print(f"Today is: {datetime.date.today().strftime('%d/%m/%Y (%A)')}\n")
    
    for cname in sample_classes:
        res = get_class_lesson_log_db(cname)
        lessons = res.get('lessons', [])
        print(f"--- Class '{cname}' (Total {len(lessons)} lessons) ---")
        for l in lessons[:8]:
            st = l['status_label'].encode('ascii', 'ignore').decode('ascii')
            print(f"  Buoi {l['buoi']}: {l['date']} ({l['lesson_title']}) -> {st}")
        print()

if __name__ == '__main__':
    test_dates()
