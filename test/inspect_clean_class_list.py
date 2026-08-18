import sys, os, io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

# 1. Distinct from ClassSchedule
c.execute("SELECT DISTINCT class_name FROM class_schedules WHERE class_name IS NOT NULL AND class_name != ''")
sc_classes = [r[0].strip() for r in c.fetchall() if r[0]]

# 2. Distinct from ClassMaster
c.execute("SELECT DISTINCT class_name FROM classes WHERE class_name IS NOT NULL AND class_name != ''")
master_classes = [r[0].strip() for r in c.fetchall() if r[0]]

# 3. Distinct from Student
c.execute("SELECT DISTINCT class_name FROM students WHERE class_name IS NOT NULL AND class_name != '' UNION SELECT DISTINCT grammar_class FROM students WHERE grammar_class IS NOT NULL AND grammar_class != ''")
st_raw = [r[0].strip() for r in c.fetchall() if r[0]]

all_split = set()
for s in sc_classes + master_classes:
    if s and s.lower() != 'bảo lưu':
        all_split.add(s)

for s in st_raw:
    if ',' in s:
        parts = [p.strip() for p in s.split(',')]
        for p in parts:
            if p and p.lower() != 'bảo lưu':
                all_split.add(p)
    else:
        if s and s.lower() != 'bảo lưu':
            all_split.add(s)

clean_classes = sorted(list(all_split))
print("Total clean classes count:", len(clean_classes))
for name in clean_classes:
    print(f"- {name}")

conn.close()
