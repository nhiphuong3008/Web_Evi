import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session, engine
from sqlalchemy import inspect, text

def check_and_add_column():
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('students')]
    print("Current columns in students table count:", len(columns))
    
    if 'last_class_name' not in columns:
        print("Adding last_class_name column via SQLAlchemy engine...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE students ADD COLUMN last_class_name VARCHAR(100);"))
            conn.commit()
        print("Successfully added last_class_name column!")
    else:
        print("last_class_name column already exists in DB!")

if __name__ == '__main__':
    check_and_add_column()
