import sqlite3

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(class_schedule_adjustments)")
cols = cursor.fetchall()
print("Columns of class_schedule_adjustments:", cols)

cursor.execute("SELECT * FROM class_schedule_adjustments LIMIT 5")
print("Sample rows:", cursor.fetchall())
conn.close()
