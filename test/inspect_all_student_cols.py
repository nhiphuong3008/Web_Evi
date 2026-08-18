import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

print("=== ALL COLUMNS IN STUDENTS FOR EVI068 & EVI056 ===")
c.execute("SELECT * FROM students WHERE code IN ('EVI068', 'EVI056')")
rows = c.fetchall()
col_names = [description[0] for description in c.description]
for r in rows:
    print("\n--- Student ---")
    for name, val in zip(col_names, r):
        print(f"  {name}: {val}")

conn.close()
