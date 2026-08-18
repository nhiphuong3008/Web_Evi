import sys, os, io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
import services.db_service as dbs

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

res = dbs.get_cm_classes_db(include_ended=True)
print("Total merged classes count:", res.get('count'))
classes = res.get('data', [])
for c in classes:
    print(f"- {c['class_name']}: {c['status']} ({c['student_count']} HS)")

print("✅ Merged classes test completed!")
