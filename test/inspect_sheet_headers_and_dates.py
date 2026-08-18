import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

app = create_app()
with app.app_context():
    sheets_service = app.config.get('SHEETS_SERVICE')
    if not sheets_service or not sheets_service.is_connected:
        print("Google Sheets API not connected!")
        sys.exit(1)

    spreadsheet_id = app.config.get('SPREADSHEET_1_ID')
    sheets_info = sheets_service.get_all_sheets()
    print("Available sheets:")
    for s in sheets_info:
        print(f" - {s.get('title')}")
        if 'tương tác' in s.get('title', '').lower() or 'tuong tac' in s.get('title', '').lower() or 'chăm sóc' in s.get('title', '').lower():
            target_name = s.get('title')
            sheet_data = sheets_service.read_sheet(sheet_name=target_name, spreadsheet_id=spreadsheet_id)
            if sheet_data:
                header = sheet_data[0]
                print(f"\nHeader for '{target_name}' ({len(header)} cols):")
                for idx, col in enumerate(header):
                    print(f"  Col {idx} ({chr(65+idx) if idx < 26 else f'A{chr(65+idx-26)}'}): {repr(col)}")
