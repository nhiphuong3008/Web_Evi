import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM parent_interaction_logs")
print("Total records in parent_interaction_logs:", c.fetchone()[0])

c.execute("SELECT id, student_code, student_name, class_name, staff_name, month, note, interaction_detail, created_at FROM parent_interaction_logs LIMIT 10")
rows = c.fetchall()
print("\nSample records:")
for r in rows:
    print(r)

conn.close()
