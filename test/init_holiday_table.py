import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import init_db, engine
from database.models import Base

if __name__ == '__main__':
    print("Initializing DB tables...")
    Base.metadata.create_all(bind=engine)
    init_db()
    print("DB initialized successfully. Checking holiday_history_logs table...")
    from database.models import HolidayHistoryLog
    from database.db_manager import db_session
    s = db_session()
    count = s.query(HolidayHistoryLog).count()
    print(f"Current HolidayHistoryLog count: {count}")
    s.close()
