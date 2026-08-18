import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'evi_center.db')
db_path = os.path.abspath(db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check existing columns in attendance_records
cur.execute("PRAGMA table_info(attendance_records)")
cols = [r[1] for r in cur.fetchall()]
print(f"Existing columns in attendance_records: {cols}")

new_cols = [
    ("hw_total_questions", "INTEGER DEFAULT 10"),
    ("hw_correct_answers", "INTEGER NULL"),
    ("hw_score", "REAL NULL"),
    ("hw_submission_status", "TEXT DEFAULT 'Nộp đúng giờ'"),
    ("hw_comment", "TEXT NULL")
]

for col_name, col_type in new_cols:
    if col_name not in cols:
        cur.execute(f"ALTER TABLE attendance_records ADD COLUMN {col_name} {col_type}")
        print(f"[ADDED] Column '{col_name}' added to attendance_records")
    else:
        print(f"  Column '{col_name}' already exists.")

conn.commit()
conn.close()
print("MIGRATION COMPLETED!")
