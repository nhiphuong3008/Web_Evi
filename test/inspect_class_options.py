import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("SELECT DISTINCT teacher FROM class_schedules WHERE teacher IS NOT NULL AND teacher != ''")
teachers = sorted([r[0] for r in c.fetchall() if r[0]])

c.execute("SELECT DISTINCT cm_staff FROM class_schedules WHERE cm_staff IS NOT NULL AND cm_staff != '' UNION SELECT DISTINCT cm_staff_name FROM users WHERE cm_staff_name IS NOT NULL AND cm_staff_name != ''")
cms = sorted([r[0] for r in c.fetchall() if r[0]])

c.execute("SELECT DISTINCT room FROM class_schedules WHERE room IS NOT NULL AND room != ''")
rooms = sorted([r[0] for r in c.fetchall() if r[0]])

print("Teachers:", teachers)
print("CMs:", cms)
print("Rooms:", rooms)

conn.close()
