import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM student_renewals")
print("student_renewals count:", c.fetchone()[0])

c.execute("SELECT id, student_code, student_name, class_name, cm_staff, month, year, status FROM student_renewals")
rows = c.fetchall()
print("student_renewals records:")
for r in rows:
    print(r)

c.execute("SELECT COUNT(*) FROM renewal_detail_logs")
print("\nrenewal_detail_logs count:", c.fetchone()[0])
c.execute("SELECT DISTINCT month, year FROM renewal_detail_logs")
print("renewal_detail_logs months/years:", c.fetchall())

c.execute("SELECT COUNT(*) FROM students WHERE expiry_month IS NOT NULL AND expiry_month != ''")
print("\nstudents with expiry_month count:", c.fetchone()[0])
c.execute("SELECT expiry_month, expiry_year, COUNT(*) FROM students GROUP BY expiry_month, expiry_year")
print("students expiry distribution:", c.fetchall())

conn.close()
