import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('database/evi_center.db')
cur = conn.cursor()

print("=== CHECK EVI266 ===")
cur.execute("SELECT code, full_name FROM students WHERE code='EVI266'")
r = cur.fetchone()
if r:
    print(f"  FOUND: code={r[0]}, name={r[1]}")
else:
    print("  NOT FOUND!")

print("\n=== CHECK CLASSES ===")
for cn in ['Sun 4.4', 'GALAX 3.2']:
    cur.execute("SELECT id, class_name FROM classes WHERE class_name=?", (cn,))
    r = cur.fetchone()
    if r:
        print(f"  '{cn}' FOUND: id={r[0]}")
    else:
        print(f"  '{cn}' NOT FOUND!")

print("\n=== CHECK IF SEED FUNCTION CREATED FAKE DATA ===")
# Look at the description - contains "kiem tra tu dong ghi log hoat dong"
cur.execute("SELECT id, description FROM activity_logs WHERE description LIKE '%kiểm tra tự động%'")
rows = cur.fetchall()
print(f"  Records with test description: {len(rows)}")
for r in rows:
    print(f"    id={r[0]}: {r[1]}")

print("\n=== CHECK db_service.py FOR seed_initial_activity_logs_db ===")
import os
with open('services/db_service.py', 'r', encoding='utf-8') as f:
    content = f.read()
if 'seed_initial_activity_logs_db' in content:
    print("  FOUND: seed_initial_activity_logs_db function exists!")
    # Find where it's called
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'seed_initial' in line.lower():
            print(f"    Line {i+1}: {line.strip()}")
else:
    print("  NOT FOUND: no seed function")

conn.close()
