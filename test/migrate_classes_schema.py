import sqlite3

conn = sqlite3.connect('database/evi_center.db')
c = conn.cursor()

c.execute('PRAGMA table_info(classes)')
cols = [row[1] for row in c.fetchall()]

new_cols = [
    ('start_date', 'TEXT'),
    ('curriculum', 'TEXT'),
    ('shift_code', 'TEXT'),
    ('status', 'TEXT')
]

for col_name, col_type in new_cols:
    if col_name not in cols:
        print(f"Adding column {col_name}...")
        c.execute(f"ALTER TABLE classes ADD COLUMN {col_name} {col_type}")

c.execute("UPDATE classes SET status = 'Đang hoạt động' WHERE status IS NULL OR status = ''")
conn.commit()
conn.close()
print("✅ Migrated classes table successfully!")
