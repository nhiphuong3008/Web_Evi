import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute("SELECT id, class_name, status FROM classes WHERE LOWER(TRIM(class_name)) = 'sun 5.1'")
print("Sun 5.1 in classes table:", c.fetchall())

# Set Sun 5.1 status to 'Đã kết thúc'
c.execute("UPDATE classes SET status = 'Đã kết thúc' WHERE LOWER(TRIM(class_name)) = 'sun 5.1'")
conn.commit()

c.execute("SELECT id, class_name, status FROM classes WHERE LOWER(TRIM(class_name)) = 'sun 5.1'")
print("Updated Sun 5.1 in classes table:", c.fetchall())

conn.close()
