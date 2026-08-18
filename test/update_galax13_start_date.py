import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassScheduleAdjustment

def update_galax13_start():
    session = db_session()
    adj = session.query(ClassScheduleAdjustment).filter(ClassScheduleAdjustment.class_name == 'Galax 1.3').first()
    if not adj:
        adj = ClassScheduleAdjustment(class_name='Galax 1.3', start_date='2026-05-18', note='Set exact start date for Lesson 24 on 06/08')
        session.add(adj)
    else:
        adj.start_date = '2026-05-18'
        adj.note = 'Set exact start date for Lesson 24 on 06/08'
    session.commit()
    print("Successfully updated Galax 1.3 start_date to '2026-05-18'!")
    session.close()

if __name__ == '__main__':
    update_galax13_start()
