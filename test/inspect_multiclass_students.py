import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

students_to_check = ['EVI056', 'EVI068', 'EVI073', 'EVI122', 'EVI147', 'EVI162', 'EVI166', 'EVI236', 'EVI266', 'EVI393', 'EVI437']

print("=== CHECKING MULTI-CLASS STUDENTS IN DB ===")
for st_code in students_to_check:
    c.execute("SELECT code, full_name, class_name, total_sessions, remaining_sessions, expiry_date FROM students WHERE code = ?", (st_code,))
    st_row = c.fetchone()
    print(f"\nStudent {st_code}: {st_row}")

    c.execute("SELECT id, student_code, student_name, class_name, month, year, expected_expiry_date FROM student_renewals WHERE student_code = ?", (st_code,))
    rn_rows = c.fetchall()
    print(f"  Renewals records ({len(rn_rows)}): {rn_rows}")

conn.close()
