"""Initialize activity_logs table in database."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import init_db
from services.db_service import seed_initial_activity_logs_db

print("Initializing DB tables...")
init_db()
print("Seeding initial activity logs...")
seed_initial_activity_logs_db()
print("Done!")
