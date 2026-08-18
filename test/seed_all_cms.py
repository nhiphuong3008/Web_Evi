import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import User

def sync_cm_users():
    session = db_session()
    cm_list = [
        {'username': 'cm_thucanh', 'password': '123456', 'full_name': 'CM Thục Anh', 'email': 'thucanh@evi.edu.vn', 'cm_staff_name': 'Thục Anh'},
        {'username': 'cm_amber', 'password': '123456', 'full_name': 'CM Amber', 'email': 'amber@evi.edu.vn', 'cm_staff_name': 'Amber'},
        {'username': 'cm_naomi', 'password': '123456', 'full_name': 'CM Naomi', 'email': 'naomi@evi.edu.vn', 'cm_staff_name': 'Naomi'},
        {'username': 'cm_lan', 'password': '123456', 'full_name': 'CM Ms. Lan', 'email': 'lan@evi.edu.vn', 'cm_staff_name': 'Ms. Lan'},
        {'username': 'cm_vananh', 'password': '123456', 'full_name': 'CM Vân Anh', 'email': 'vananh@evi.edu.vn', 'cm_staff_name': 'Vân Anh'},
        {'username': 'cm_anhptt', 'password': '123456', 'full_name': 'CM AnhPTT', 'email': 'anhptt@evi.edu.vn', 'cm_staff_name': 'AnhPTT'},
        {'username': 'cm_ngoc', 'password': '123456', 'full_name': 'CM NgọcCM', 'email': 'ngoc@evi.edu.vn', 'cm_staff_name': 'NgọcCM'},
        {'username': 'cm_giang', 'password': '123456', 'full_name': 'CM Giang', 'email': 'giang@evi.edu.vn', 'cm_staff_name': 'Giang'},
        {'username': 'cm_duyen', 'password': '123456', 'full_name': 'CM Duyên', 'email': 'duyen@evi.edu.vn', 'cm_staff_name': 'Duyên'},
    ]

    added = 0
    for udata in cm_list:
        existing = session.query(User).filter(User.username == udata['username']).first()
        if not existing:
            u = User(
                username=udata['username'],
                full_name=udata['full_name'],
                email=udata['email'],
                role='cm',
                cm_staff_name=udata['cm_staff_name'],
                is_active=1
            )
            u.set_password(udata['password'])
            session.add(u)
            added += 1
            print(f"Added new CM user: {udata['username']} -> {udata['cm_staff_name']}")

    session.commit()
    all_users = session.query(User).all()
    print(f"\nTotal users in DB: {len(all_users)}")
    for u in all_users:
        print(f"User: {u.username} | Name: {u.full_name} | Role: {u.role} | CM: '{u.cm_staff_name}'")
    session.close()

if __name__ == "__main__":
    sync_cm_users()
