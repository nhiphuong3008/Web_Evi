import sqlite3
import shutil
import os

db_path = 'database/evi_center.db'
backup_path = 'database/evi_center_backup_schedule_fix.db'

# 1. Backup DB
shutil.copyfile(db_path, backup_path)
print(f"Backed up database to {backup_path}")

# 2. Cleanup records ID >= 41 (the obsolete 'Bổ trợ' records)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM class_schedules WHERE id >= 41")
count_before = cursor.fetchone()[0]
print(f"Found {count_before} records to remove (id >= 41).")

cursor.execute("DELETE FROM class_schedules WHERE id >= 41")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM class_schedules")
total_after = cursor.fetchone()[0]
print(f"Total remaining records in class_schedules: {total_after}")

conn.close()
