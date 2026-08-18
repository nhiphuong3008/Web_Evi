import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

# 1. Update EVI056 (Nguyễn Ngọc Huyền) with her primary course Galax 1.4 data from Google Sheet
c.execute("""
    UPDATE students 
    SET class_name = 'Galax 1.4',
        total_sessions = 91,
        remaining_sessions = 16,
        expiry_date = '06/10/2026',
        expiry_month = '10',
        expiry_year = '2026'
    WHERE code = 'EVI056'
""")

c.execute("""
    UPDATE student_renewals
    SET class_name = 'Galax 1.4',
        month = 10,
        year = 2026,
        expected_expiry_date = '06/10/2026'
    WHERE id = 6 OR student_code = 'EVI056'
""")

print("✅ Updated EVI056 (Nguyễn Ngọc Huyền): Lớp Galax 1.4 | Tổng: 91 | Còn lại: 16 | Hạn hết phí: 06/10/2026 (Tháng 10/2026)")

# 2. Check all other students with multi-class or short-term course in class_name
c.execute("""
    SELECT code, full_name, class_name, total_sessions, remaining_sessions 
    FROM students 
    WHERE class_name LIKE '%,%' OR class_name LIKE '%Debate%' OR class_name LIKE '%Speaking%' OR class_name LIKE '%Ôn thi%'
""")
rows = c.fetchall()
print(f"\nAuditing {len(rows)} students with short courses/multi-classes:")
for r in rows:
    st_code, st_name, cls, tot, rem = r
    primary_cls = cls.split(',')[0].strip()
    print(f"  [{st_code}] {st_name}: Class='{cls}' -> Primary='{primary_cls}' | Tot={tot} | Rem={rem}")
    # If class_name contains comma, strip the short-term course so class_name only stores the primary long-term course
    if ',' in cls:
        c.execute("UPDATE students SET class_name = ? WHERE code = ?", (primary_cls, st_code))
        c.execute("UPDATE student_renewals SET class_name = ? WHERE student_code = ?", (primary_cls, st_code))

conn.commit()
conn.close()
print("\n✅ AUDIT AND FIX COMPLETED FOR ALL MULTI-CLASS STUDENTS!")
