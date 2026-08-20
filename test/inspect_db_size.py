import sqlite3
import os

conn = sqlite3.connect('database/evi_center.db')
cursor = conn.cursor()

print("Database file size:", os.path.getsize('database/evi_center.db') / (1024*1024), "MB")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\n--- Table row counts ---")
for t in tables:
    tname = t[0]
    cursor.execute(f"SELECT COUNT(*) FROM `{tname}`")
    cnt = cursor.fetchone()[0]
    print(f"{tname:35}: {cnt} rows")

cursor.execute("PRAGMA page_size")
page_size = cursor.fetchone()[0]
cursor.execute("PRAGMA page_count")
page_count = cursor.fetchone()[0]
cursor.execute("PRAGMA freelist_count")
freelist_count = cursor.fetchone()[0]

print(f"\nPage size: {page_size}, Page count: {page_count}, Free pages: {freelist_count}")
print(f"Wasted / Free space: {freelist_count * page_size / (1024*1024):.2f} MB")

conn.close()
