import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import Student

def test_unicode_search():
    session = db_session()
    
    # 1. Search 'trần đình long' (lowercase with accents)
    s1 = session.query(Student).filter(Student.full_name.ilike('%trần đình long%')).all()
    print("Search 'trần đình long' (lowercase with accents):", len(s1))

    # 2. Search 'Trần Đình Long' (exact case with accents)
    s2 = session.query(Student).filter(Student.full_name.ilike('%Trần Đình Long%')).all()
    print("Search 'Trần Đình Long' (exact case with accents):", len(s2))

    # 3. Search 'tran dinh long' (no accents)
    s3 = session.query(Student).filter(Student.full_name.ilike('%tran dinh long%')).all()
    print("Search 'tran dinh long' (no accents):", len(s3))

if __name__ == '__main__':
    test_unicode_search()
