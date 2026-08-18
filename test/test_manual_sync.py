import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from database.migrate_sheets_to_db import run_migration

print("Testing sync sheets to DB function...")
success = run_migration()
print(f"SYNC RESULT: {success}")
