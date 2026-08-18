import sqlite3

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()
c.execute("DELETE FROM classes WHERE class_name = 'Galax 3.3 Test'")
conn.commit()
conn.close()
print("Cleaned up test record")
