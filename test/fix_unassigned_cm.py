import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("""
    SELECT id, student_code, student_name, class_name, cm_staff, month, year, status
    FROM student_renewals
    WHERE cm_staff IS NULL OR cm_staff = '' OR cm_staff = 'Chưa phân công'
""")
empty_rows = c.fetchall()
print(f"Total rows in student_renewals with empty CM: {len(empty_rows)}")
for r in empty_rows:
    print(r)

# Auto fix empty CM by looking up student_code in students master table
fixed = 0
for r in empty_rows:
    rec_id = r[0]
    st_code = r[1]
    st_name = r[2]

    # Find matching student in students table
    c.execute("SELECT cm_staff FROM students WHERE code = ? AND cm_staff IS NOT NULL AND cm_staff != ''", (st_code,))
    st_match = c.fetchone()
    cm_found = st_match[0] if st_match else None

    if not cm_found:
        # Fallback by full name
        c.execute("SELECT cm_staff FROM students WHERE full_name = ? AND cm_staff IS NOT NULL AND cm_staff != ''", (st_name,))
        st_match = c.fetchone()
        cm_found = st_match[0] if st_match else None

    if cm_found:
        c.execute("UPDATE student_renewals SET cm_staff = ? WHERE id = ?", (cm_found, rec_id))
        print(f"  -> Fixed record ID {rec_id} ({st_code} {st_name}): assigned CM '{cm_found}'")
        fixed += 1
    else:
        print(f"  -> Warning: Could not resolve CM for ID {rec_id} ({st_code} {st_name})")

conn.commit()

# Re-verify Month 8/2026 breakdown
c.execute("""
    SELECT cm_staff, status, COUNT(*) 
    FROM student_renewals 
    WHERE month = 8 AND year = 2026 
    GROUP BY cm_staff, status
""")
print("\nUpdated Month 8/2026 CM Breakdown:")
for r in c.fetchall():
    print(r)

conn.close()
