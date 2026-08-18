import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

# 1. Update EVI068 (Nguyễn Ngọc Minh)
c.execute("""
    UPDATE students 
    SET class_name = 'Galax 3.1',
        total_sessions = 89,
        remaining_sessions = 15,
        expiry_date = '15/09/2026',
        expiry_month = '9',
        expiry_year = '2026'
    WHERE code = 'EVI068'
""")

c.execute("""
    UPDATE student_renewals
    SET class_name = 'Galax 3.1',
        month = 9,
        year = 2026,
        expected_expiry_date = '15/09/2026'
    WHERE id = 8 OR student_code = 'EVI068'
""")

# 2. Update EVI056 (Nguyễn Ngọc Huyền)
c.execute("""
    UPDATE students 
    SET class_name = 'Galax 1.4',
        expiry_date = '22/09/2026',
        expiry_month = '9',
        expiry_year = '2026'
    WHERE code = 'EVI056'
""")

c.execute("""
    UPDATE student_renewals
    SET class_name = 'Galax 1.4',
        month = 9,
        year = 2026,
        expected_expiry_date = '22/09/2026'
    WHERE id = 6 OR student_code = 'EVI056'
""")

# 3. Clean up primary class names for students with comma-separated class names in student_renewals
c.execute("SELECT id, student_code, student_name, class_name FROM student_renewals WHERE class_name LIKE '%,%'")
rows = c.fetchall()
print(f"Fixing {len(rows)} renewal records with merged class names:")
for r in rows:
    primary_cls = r[3].split(',')[0].strip()
    print(f"  Renewal #{r[0]} ({r[1]} - {r[2]}): '{r[3]}' -> '{primary_cls}'")
    c.execute("UPDATE student_renewals SET class_name = ? WHERE id = ?", (primary_cls, r[0]))

conn.commit()
print("\n✅ DB UPDATE SUCCESSFUL!")
conn.close()
