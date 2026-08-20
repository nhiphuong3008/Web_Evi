"""
EVI Dashboard - Database Manager & Connection Pool
Khởi tạo và quản lý kết nối Cơ sở dữ liệu SQLite / PostgreSQL.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base

logger = logging.getLogger(__name__)

# Base directory for database file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DB_DIR, exist_ok=True)

# Default to SQLite file database
DB_PATH = os.path.join(DB_DIR, 'evi_center.db')
DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')

from sqlalchemy.pool import NullPool

# SQLite pragma settings for ultra fast performance & WAL mode
connect_args = {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool if DATABASE_URL.startswith('sqlite') else None
)

# Thread-safe session factory
session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db_session = scoped_session(session_factory)


def seed_initial_users():
    """
    Khởi tạo danh sách tài khoản người dùng mẫu nếu chưa có dữ liệu.
    """
    from database.models import User
    session = db_session()
    try:
        if session.query(User).count() == 0:
            initial_users = [
                {'username': 'admin', 'password': 'admin123', 'full_name': 'Quản Trị Viên (Admin)', 'email': 'admin@evi.edu.vn', 'role': 'admin', 'cm_staff_name': ''},
                {'username': 'cm_ngoc', 'password': '123456', 'full_name': 'CM NgọcCM (Cao Minh Ngọc - Naomi)', 'email': 'ngoc@evi.edu.vn', 'role': 'cm', 'cm_staff_name': 'NgọcCM'},
                {'username': 'cm_anhptt', 'password': '123456', 'full_name': 'CM AnhPTT (Phạm Trần Thục Anh)', 'email': 'anhptt@evi.edu.vn', 'role': 'cm', 'cm_staff_name': 'AnhPTT'},
                {'username': 'cm_anhnv', 'password': '123456', 'full_name': 'CM AnhNV (Nguyễn Vân Anh - Amber)', 'email': 'anhnv@evi.edu.vn', 'role': 'cm', 'cm_staff_name': 'AnhNV'},
            ]
            for udata in initial_users:
                u = User(
                    username=udata['username'],
                    full_name=udata['full_name'],
                    email=udata['email'],
                    role=udata['role'],
                    cm_staff_name=udata['cm_staff_name'],
                    is_active=1
                )
                u.set_password(udata['password'])
                session.add(u)
            session.commit()
            logger.info("✅ Đã khởi tạo 5 tài khoản mẫu (Admin & CM).")
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Lỗi khởi tạo seed users: {e}")
    finally:
        session.close()


def auto_migrate_schema():
    """Tự động kiểm tra và thêm các cột mới vào CSDL nếu chưa có."""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check class_schedule_adjustments for current_lesson_num
            res = conn.execute(text("PRAGMA table_info(class_schedule_adjustments)"))
            cols = [row[1] for row in res.fetchall()]
            if 'current_lesson_num' not in cols:
                conn.execute(text("ALTER TABLE class_schedule_adjustments ADD COLUMN current_lesson_num INTEGER"))
                logger.info("✅ Đã tự động thêm cột current_lesson_num vào bảng class_schedule_adjustments")
    except Exception as e:
        logger.warning(f"Lưu ý khi tự động migrate schema: {e}")


def init_db():
    """
    Tạo tất cả các bảng trong Database nếu chưa tồn tại.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"✅ Đã kết nối và khởi tạo CSDL thành công: {DATABASE_URL}")
        auto_migrate_schema()
        seed_initial_users()
        return True
    except Exception as e:
        logger.error(f"❌ Lỗi khởi tạo CSDL: {e}")
        return False


def get_db():
    """
    Context manager / generator lấy session làm việc với DB.
    """
    session = db_session()
    try:
        yield session
    finally:
        session.close()
