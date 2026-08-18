import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("""
    SELECT id, student_code, student_name, class_name, cm_staff
    FROM student_renewals
    WHERE cm_staff IS NULL OR cm_staff = '' OR cm_staff = 'Chưa phân công'
""")
remaining_empty = c.fetchall()
print(f"Remaining empty CM records: {len(remaining_empty)}")

fixed_count = 0
for r in remaining_empty:
    rec_id, st_code, st_name, c_name, cm = r

    # 1. Lookup student history snapshot or parent_interaction_logs
    cm_found = None
    c.execute("SELECT staff_name FROM parent_interaction_logs WHERE (student_code = ? OR student_name = ?) AND staff_name IS NOT NULL AND staff_name != '' LIMIT 1", (st_code, st_name))
    p_log = c.fetchone()
    if p_log:
        cm_found = p_log[0]

    if not cm_found:
        # 2. Lookup last_class_name from students table
        c.execute("SELECT last_class_name FROM students WHERE code = ? OR full_name = ?", (st_code, st_name))
        st_last = c.fetchone()
        if st_last and st_last[0]:
            last_class = st_last[0]
            # Lookup CM of that last class in ClassSchedule or ClassMaster
            c.execute("SELECT cm_staff FROM class_schedules WHERE LOWER(TRIM(class_name)) = LOWER(TRIM(?)) AND cm_staff IS NOT NULL AND cm_staff != '' LIMIT 1", (last_class,))
            cs_cm = c.fetchone()
            if cs_cm:
                cm_found = cs_cm[0]

    if cm_found:
        c.execute("UPDATE student_renewals SET cm_staff = ? WHERE id = ?", (cm_found, rec_id))
        fixed_count += 1
        print(f"  -> Resolved ID {rec_id} ({st_code} {st_name}): assigned CM '{cm_found}'")

conn.commit()

c.execute("SELECT COUNT(*) FROM student_renewals WHERE cm_staff IS NULL OR cm_staff = '' OR cm_staff = 'Chưa phân công'")
print(f"Unassigned CM count remaining: {c.fetchone()[0]}")

conn.close()
