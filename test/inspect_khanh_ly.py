import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

print("=== CHECKING BÙI KHÁNH LY IN PARENT_INTERACTION_LOGS ===")
c.execute("SELECT id, student_code, student_name, staff_name, note, interaction_detail FROM parent_interaction_logs WHERE student_name LIKE '%Khánh Ly%' OR student_code = 'EVI241'")
for r in c.fetchall():
    print(r)

print("\n=== CHECKING BÙI KHÁNH LY IN STUDENTS TABLE ===")
c.execute("SELECT code, full_name, english_name FROM students WHERE code = 'EVI241' OR full_name LIKE '%Khánh Ly%'")
for r in c.fetchall():
    print(r)

conn.close()
