import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_config
from services.google_sheets import GoogleSheetsService

def inspect_all_sheets():
    config = get_config()
    sheets_service = GoogleSheetsService(
        credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE,
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
    )
    sheets_service.connect()

    for name, key in [
        ("Dashboard Sheet", config.GOOGLE_SHEETS_SPREADSHEET_ID),
        ("BTVN Sheet", getattr(config, 'GOOGLE_SHEETS_BTVN_ID', None)),
        ("Grades Sheet", getattr(config, 'GOOGLE_SHEETS_GRADES_ID', None))
    ]:
        if not key: continue
        try:
            sp = sheets_service.client.open_by_key(key)
            print(f"\n--- Worksheets in {name} ({key}) ---")
            for ws in sp.worksheets():
                print(f"  • Worksheet Title: '{ws.title}' (rows: {ws.row_count}, cols: {ws.col_count})")
        except Exception as e:
            print(f"Error inspecting {name}: {e}")

if __name__ == '__main__':
    inspect_all_sheets()
