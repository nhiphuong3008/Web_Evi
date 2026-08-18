"""
Script tự động tạo tài khoản User cho tất cả Giáo viên (GV) từ ClassSchedule.
Chạy 1 lần duy nhất.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

from services.db_service import db_session
from database.models import User, ClassSchedule

# Danh sách GV thực tế từ ClassSchedule + mapping username/email
TEACHER_MAP = {
    'Andrew':          {'username': 'gv_andrew',    'email': 'andrew@evi.edu.vn'},
    'Jacob':           {'username': 'gv_jacob',     'email': 'jacob@evi.edu.vn'},
    'Miguel':          {'username': 'gv_miguel',    'email': 'miguel@evi.edu.vn'},
    'Thomas (cover)':  {'username': 'gv_thomas',    'email': 'thomas@evi.edu.vn'},
    'GVVN Ms Van':     {'username': 'gv_msvan',     'email': 'msvan@evi.edu.vn'},
    'Thục Anh':        {'username': 'gv_thucanh',   'email': 'thucanh.gv@evi.edu.vn'},
    'Vân Anh':         {'username': 'gv_vananh',    'email': 'vananh@evi.edu.vn'},
}

DEFAULT_PASSWORD = 'evi2026'

def main():
    session = db_session()
    created = 0
    skipped = 0

    for full_name, info in TEACHER_MAP.items():
        username = info['username']
        email = info['email']

        # Kiểm tra đã tồn tại chưa
        existing = session.query(User).filter(
            (User.username == username) | (User.full_name == full_name)
        ).first()

        if existing:
            print(f'  [SKIP] {full_name} ({username}) - da ton tai (ID={existing.id})')
            skipped += 1
            continue

        user = User(
            username=username,
            full_name=full_name,
            email=email,
            role='teacher',
            cm_staff_name=full_name,  # Dùng chính tên GV làm bí danh phân công
            is_active=1
        )
        user.set_password(DEFAULT_PASSWORD)
        session.add(user)
        print(f'  [CREATED] {full_name} ({username}) - role=teacher, password={DEFAULT_PASSWORD}')
        created += 1

    session.commit()
    session.close()

    print(f'\n=== KET QUA: Tao {created} tai khoan GV moi, bo qua {skipped} tai khoan da ton tai ===')

if __name__ == '__main__':
    main()
