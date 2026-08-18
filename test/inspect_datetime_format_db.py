import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'evi_center.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def convert_to_iso(val):
    if not val or '/' not in str(val):
        return val
    try:
        parts = str(val).strip().split(' ')
        d_parts = parts[0].split('/')
        if len(d_parts) == 3:
            day, month, year = int(d_parts[0]), int(d_parts[1]), int(d_parts[2])
            time_str = parts[1] if len(parts) > 1 else '00:00:00'
            if len(time_str.split(':')) == 2:
                time_str += ':00'
            return f"{year:04d}-{month:02d}-{day:02d} {time_str}"
    except Exception as e:
        print(f"Error converting '{val}': {e}")
    return val

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall() if not r[0].startswith('sqlite_')]

total_fixes = 0
for t in tables:
    cursor.execute(f"PRAGMA table_info({t})")
    cols = [col[1] for col in cursor.fetchall() if 'created' in col[1] or 'updated' in col[1]]
    for col in cols:
        cursor.execute(f"SELECT id, {col} FROM {t} WHERE {col} LIKE '%/%'")
        bad_rows = cursor.fetchall()
        if bad_rows:
            print(f"Fixing Table '{t}', Column '{col}': {len(bad_rows)} rows...")
            for r_id, val in bad_rows:
                new_val = convert_to_iso(val)
                cursor.execute(f"UPDATE {t} SET {col} = ? WHERE id = ?", (new_val, r_id))
                total_fixes += 1

conn.commit()
conn.close()
print(f"\n[OK] Total non-ISO datetime fields fixed across all tables: {total_fixes}")
