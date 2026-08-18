import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

print("=== STUDENTS WITH MULTIPLE / SHORT TERM CLASSES IN CLASS_NAME ===")
c.execute("SELECT code, full_name, class_name, total_sessions, remaining_sessions, expiry_date FROM students WHERE class_name LIKE '%,%' OR class_name LIKE '%Debate%' OR class_name LIKE '%Speaking%'")
rows = c.fetchall()
print(f"Total found: {len(rows)}")
for r in rows:
    print(r)

conn.close()
