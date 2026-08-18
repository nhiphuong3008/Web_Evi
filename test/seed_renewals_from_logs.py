import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

# 1. Fetch valid records from renewal_detail_logs
c.execute("""
    SELECT student_code, student_name, english_name, class_name, cm_staff, expiry_month, expiry_year, expiry_date, renewal_status, interaction_note
    FROM renewal_detail_logs
    WHERE expiry_month IS NOT NULL AND expiry_month != '' AND expiry_month != '#VALUE!'
      AND expiry_year IS NOT NULL AND expiry_year != '' AND expiry_year != '#VALUE!'
""")
logs = c.fetchall()
print(f"Total valid renewal detail log entries: {len(logs)}")

status_map = {
    'thành công': 'success',
    'chồng phí': 'stacked',
    'chưa tái phí': 'pending',
    'thất bại': 'failed',
}

inserted = 0
updated = 0

for log in logs:
    st_code = (log[0] or '').strip().upper()
    st_name = (log[1] or '').strip()
    en_name = (log[2] or '').strip()
    cls_name = (log[3] or '').strip()
    cm = (log[4] or '').strip()
    try:
        m = int(log[5])
        y = int(log[6])
    except ValueError:
        continue
    exp_date = (log[7] or '').strip()
    raw_status = (log[8] or '').strip().lower()
    notes = (log[9] or '').strip()

    status_code = status_map.get(raw_status, 'pending')

    # Check existing in student_renewals by student_code + month + year
    c.execute("""
        SELECT id FROM student_renewals 
        WHERE UPPER(TRIM(student_code)) = ? AND month = ? AND year = ?
    """, (st_code, m, y))
    row = c.fetchone()

    if row:
        c.execute("""
            UPDATE student_renewals 
            SET student_name=?, english_name=?, class_name=?, cm_staff=?, status=?, expected_expiry_date=?, notes=?
            WHERE id=?
        """, (st_name, en_name, cls_name, cm, status_code, exp_date, notes, row[0]))
        updated += 1
    else:
        c.execute("""
            INSERT INTO student_renewals (student_code, student_name, english_name, class_name, cm_staff, month, year, status, expected_expiry_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (st_code, st_name, en_name, cls_name, cm, m, y, status_code, exp_date, notes))
        inserted += 1

    # Also update student table expiry_month and expiry_year if matching student_code
    if st_code:
        c.execute("""
            UPDATE students 
            SET expiry_month = ?, expiry_year = ?, expiry_date = ?
            WHERE UPPER(TRIM(code)) = ?
        """, (str(m), str(y), exp_date, st_code))

conn.commit()

c.execute("SELECT COUNT(*) FROM student_renewals")
print(f"Inserted: {inserted}, Updated: {updated}. Total student_renewals now: {c.fetchone()[0]}")

c.execute("SELECT month, year, COUNT(*) FROM student_renewals GROUP BY year, month ORDER BY year, month")
print("\nRenewals distribution by month/year:")
for r in c.fetchall():
    print(f"  Tháng {r[0]}/{r[1]}: {r[2]} lượt tái phí")

conn.close()
