import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule

def update_materials():
    session = db_session()
    count = session.query(ClassSchedule).update({ClassSchedule.materials: 'Syllabus'})
    session.commit()
    print(f"Successfully updated {count} schedule entries in DB to 'Syllabus'!")
    session.close()

if __name__ == '__main__':
    update_materials()
