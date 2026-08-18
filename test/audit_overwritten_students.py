import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

print("=== 1. CHECKING EVI056 (Nguyễn Ngọc Huyền) CURRENT DB VALUES ===")
c.execute("""
    SELECT code, full_name, class_name, total_sessions, remaining_sessions, expiry_date 
    FROM students 
    WHERE code = 'EVI056'
""")
for r in c.fetchall():
    print(r)

print("\n=== 2. FINDING ALL STUDENTS WHO MIGHT HAVE OVERWRITTEN REMAINING SESSIONS ===")
# Find all students where remaining_sessions is suspiciously low (1, 2, 3, 4, 5) while total_sessions is 15 (short course length)
c.execute("""
    SELECT code, full_name, class_name, total_sessions, remaining_sessions, expiry_date
    FROM students
    WHERE total_sessions = 15 OR remaining_sessions <= 5
""")
rows = c.fetchall()
print(f"Total students with short course total_sessions (15) or low remaining_sessions (<=5): {len(rows)}")
for r in rows:
    print(r)

conn.close()
