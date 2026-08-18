import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import Student, ParentInteractionLog

def clean_test():
    session = db_session()
    session.query(ParentInteractionLog).filter(ParentInteractionLog.student_code == 'EVI999').delete()
    session.query(Student).filter(Student.code == 'EVI999').delete()
    session.commit()
    print("Cleaned test student EVI999 successfully.")

if __name__ == '__main__':
    clean_test()
