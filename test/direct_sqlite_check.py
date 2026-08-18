import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'evi_center.db')
db_path = os.path.abspath(db_path)
print(f"DB Path: {db_path}")
print(f"DB Exists: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT code, full_name, class_name, grammar_class, status FROM students WHERE code = 'EVI122'")
rows = cur.fetchall()
print(f"\n--- EVI122 in raw SQLite ---")
for r in rows:
    code, fname, cname, gclass, status = r
    print(f"  code: {code}")
    print(f"  full_name: {fname.encode('ascii','ignore').decode('ascii')}")
    print(f"  class_name: {(cname or '').encode('ascii','ignore').decode('ascii')}")
    print(f"  grammar_class: {(gclass or '').encode('ascii','ignore').decode('ascii')}")
    print(f"  status: {(status or '').encode('ascii','ignore').decode('ascii')}")

print(f"\n--- All students where class_name LIKE '%Galax 1.3%' ---")
cur.execute("SELECT code, full_name, class_name FROM students WHERE class_name LIKE '%Galax 1.3%'")
for r in cur.fetchall():
    code, fname, cname = r
    fn = fname.encode('ascii','ignore').decode('ascii')
    cn = cname.encode('ascii','ignore').decode('ascii') if cname else ''
    print(f"  {code} | {fn} | class='{cn}'")

conn.close()
