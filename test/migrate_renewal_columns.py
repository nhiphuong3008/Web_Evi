import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'evi_center.db')

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add expected_expiry_date if not exists
    try:
        cursor.execute("ALTER TABLE student_renewals ADD COLUMN expected_expiry_date VARCHAR(50);")
        print("Added column expected_expiry_date to student_renewals")
    except Exception as e:
        print("expected_expiry_date column status:", e)

    # Add completed_at if not exists
    try:
        cursor.execute("ALTER TABLE student_renewals ADD COLUMN completed_at DATETIME;")
        print("Added column completed_at to student_renewals")
    except Exception as e:
        print("completed_at column status:", e)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
