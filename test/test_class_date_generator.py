import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule

DAY_MAP = {
    'thứ 2': 0, 'mon': 0,
    'thứ 3': 1, 'tue': 1,
    'thứ 4': 2, 'wed': 2,
    'thứ 5': 3, 'thu': 3,
    'thứ 6': 4, 'fri': 4,
    'thứ 7': 5, 'sat': 5,
    'chủ nhật': 6, 'sun': 6
}

def get_class_days(class_name):
    session = db_session()
    schedules = session.query(ClassSchedule).filter(ClassSchedule.class_name.ilike(f"%{class_name.strip()}%")).all()
    session.close()
    
    target_days = set()
    for s in schedules:
        if s.day:
            day_str = s.day.lower()
            for key, val in DAY_MAP.items():
                if key in day_str:
                    target_days.add(val)
                    
    if not target_days:
        # Default Mon/Thu if not specified
        target_days = {0, 3}
        
    return sorted(list(target_days))

def generate_lesson_dates(class_name, total_lessons=72):
    days_of_week = get_class_days(class_name) # e.g. [1, 4] for Tue, Fri
    
    # Calculate start date roughly 12-16 weeks ago so current lesson falls near today
    today = datetime.date.today()
    
    # Generate list of dates matching days_of_week starting from a base date
    # Let's say we want lesson #15 to #20 to be near today
    # Total lessons 72 -> ~36 weeks (2 lessons/week)
    start_base = today - datetime.timedelta(weeks=10)
    
    # Move start_base to first matching day_of_week
    while start_base.weekday() not in days_of_week:
        start_base += datetime.timedelta(days=1)
        
    dates = []
    curr = start_base
    while len(dates) < total_lessons:
        if curr.weekday() in days_of_week:
            dates.append(curr)
        curr += datetime.timedelta(days=1)
        
    return days_of_week, dates

def test_gen():
    sample_classes = ['Galax 1.4', 'Galax 1.3', 'Sun 1.4', 'Moon 3.1', 'Sun 2.1']
    today = datetime.date.today()
    print(f"Today is: {today.strftime('%Y-%m-%d (%A)')}\n")
    
    for cname in sample_classes:
        days, dates = generate_lesson_dates(cname, 10)
        print(f"Class '{cname}' -> Study Days: {days}")
        for idx, d in enumerate(dates[:6]):
            is_today = (d == today)
            is_past = (d < today)
            status = "COMPLETED" if is_past else ("TODAY" if is_today else "PENDING")
            print(f"  Lesson {idx+1}: {d.strftime('%d/%m/%Y (%a)')} -> Status: {status}")
        print()

if __name__ == '__main__':
    test_gen()
