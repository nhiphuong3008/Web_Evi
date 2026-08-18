import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("SELECT id, student_code, student_name FROM student_renewals WHERE cm_staff IS NULL OR cm_staff = '' OR cm_staff = 'Chưa phân công'")
rows = c.fetchall()

resolved = 0
for r in rows:
    rec_id, code, name = r
    cm_found = None
    c_name = None

    # Check HomeworkRecord
    c.execute("SELECT class_name FROM homework_records WHERE (student_code = ? OR student_name = ?) AND class_name IS NOT NULL AND class_name != '' LIMIT 1", (code, name))
    hw = c.fetchone()
    if hw: c_name = hw[0]

    # Check UnitGrade
    if not c_name:
        c.execute("SELECT class_name FROM unit_grades WHERE (student_code = ? OR student_name = ?) AND class_name IS NOT NULL AND class_name != '' LIMIT 1", (code, name))
        ug = c.fetchone()
        if ug: c_name = ug[0]

    # Check MonthlyAttendanceRecord
    if not c_name:
        c.execute("SELECT class_name FROM monthly_attendance_records WHERE (student_code = ? OR student_name = ?) AND class_name IS NOT NULL AND class_name != '' LIMIT 1", (code, name))
        att = c.fetchone()
        if att: c_name = att[0]

    if c_name:
        # Find CM for that class
        c.execute("SELECT cm_staff FROM class_schedules WHERE LOWER(TRIM(class_name)) = LOWER(TRIM(?)) AND cm_staff IS NOT NULL AND cm_staff != '' LIMIT 1", (c_name,))
        cs = c.fetchone()
        if cs: cm_found = cs[0]

    if cm_found:
        c.execute("UPDATE student_renewals SET cm_staff = ?, class_name = ? WHERE id = ?", (cm_found, c_name, rec_id))
        resolved += 1
        print(f"  -> Resolved ID {rec_id} ({code} {name}): Class '{c_name}', CM '{cm_found}'")

conn.commit()
c.execute("SELECT COUNT(*) FROM student_renewals WHERE cm_staff IS NULL OR cm_staff = '' OR cm_staff = 'Chưa phân công'")
print(f"Remaining unassigned CM count: {c.fetchone()[0]}")
conn.close()
