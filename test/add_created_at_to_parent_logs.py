import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import engine
from sqlalchemy import inspect, text

def check_and_add_created_at():
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('parent_interaction_logs')]
    print("Current columns in parent_interaction_logs table:", columns)
    
    if 'created_at' not in columns:
        print("Adding created_at column to parent_interaction_logs...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE parent_interaction_logs ADD COLUMN created_at DATETIME;"))
            conn.commit()
        print("Successfully added created_at column!")
    else:
        print("created_at column already exists.")

if __name__ == '__main__':
    check_and_add_created_at()
