import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

short_course_students = ['EVI073', 'EVI162', 'EVI166', 'EVI236', 'EVI266']

print("=== CHECKING PRIMARY CLASS ATTENDANCE FOR SHORT COURSE STUDENTS ===")
for code in short_course_students:
    c.execute("SELECT code, full_name, class_name, total_sessions, remaining_sessions FROM students WHERE code = ?", (code,))
    st = c.fetchone()
    print(f"\nStudent {code}: {st}")
    
    # Check attendance records in primary class
    primary_cls = st[2].split(',')[0].strip()
    c.execute("SELECT COUNT(*) FROM monthly_attendance_records WHERE student_code = ? AND class_name = ?", (code, primary_cls))
    att_count = c.fetchone()[0]
    print(f"  Attendance count in primary class '{primary_cls}': {att_count}")

conn.close()
