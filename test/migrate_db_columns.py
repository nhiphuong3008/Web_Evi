import os
import sys
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import init_db

db_path = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\database\evi_center.db"

def migrate():
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Check & add is_guest column to attendance_records
    cursor.execute("PRAGMA table_info(attendance_records);")
    att_cols = [col[1] for col in cursor.fetchall()]
    if 'is_guest' not in att_cols:
        print("Adding column 'is_guest' to 'attendance_records'...")
        cursor.execute("ALTER TABLE attendance_records ADD COLUMN is_guest INTEGER DEFAULT 0;")
    else:
        print("Column 'is_guest' already exists in 'attendance_records'.")

    # 2. Check & add lesson_plan_url column to class_schedules
    cursor.execute("PRAGMA table_info(class_schedules);")
    sch_cols = [col[1] for col in cursor.fetchall()]
    if 'lesson_plan_url' not in sch_cols:
        print("Adding column 'lesson_plan_url' to 'class_schedules'...")
        cursor.execute("ALTER TABLE class_schedules ADD COLUMN lesson_plan_url VARCHAR(500);")
    else:
        print("Column 'lesson_plan_url' already exists in 'class_schedules'.")

    conn.commit()
    conn.close()

    # 3. Create any new tables e.g. lesson_syllabuses
    init_db()
    print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate()
