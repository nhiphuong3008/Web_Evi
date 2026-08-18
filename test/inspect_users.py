import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import User

def main():
    session = db_session()
    users = session.query(User).all()
    print(f"Total Users: {len(users)}")
    for u in users:
        print(f"ID: {u.id} | Username: {u.username} | Name: {u.full_name} | Role: {u.role} | CM: {u.cm_staff_name} | Active: {u.is_active}")
    session.close()

if __name__ == "__main__":
    main()
