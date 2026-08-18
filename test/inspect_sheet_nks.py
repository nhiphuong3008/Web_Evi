import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from config import Config
from services.google_sheets import GoogleSheetsService

def inspect_sheet():
    gs = GoogleSheetsService(Config.GOOGLE_SHEETS_CREDENTIALS_FILE, Config.GOOGLE_SHEETS_SPREADSHEET_ID)
    if not gs.connect():
        print("❌ Cannot connect to Google Sheets API (credentials file missing or demo mode)")
        return
    sp = gs.spreadsheet
    ws = None
    for w in sp.worksheets():
        if 'chăm sóc' in w.title.lower() or 'tương tác' in w.title.lower():
            ws = w
            print(f"✅ Found Worksheet: '{w.title}'")
            break

    if not ws:
        print("❌ Worksheet not found!")
        return

    rows = ws.get_all_values()
    print(f"Total rows in worksheet '{ws.title}': {len(rows)}")
    if len(rows) > 0:
        print("Header row 0:", [f"Col {i+1} ({chr(65+i)}): {rows[0][i]}" for i in range(min(18, len(rows[0])))])
    if len(rows) > 1:
        print("\n--- SAMPLE DATA ROWS ---")
        for idx, r in enumerate(rows[1:]):
            st_code = r[1].strip() if len(r) > 1 else ''
            st_name = r[2].strip() if len(r) > 2 else ''
            if st_name and st_name.lower() not in ('tên học sinh', 'học sinh'):
                print(f"Row #{idx+2}: Code='{st_code}' | Name='{st_name}' | Nickname='{r[3] if len(r)>3 else ''}' | Class='{r[4] if len(r)>4 else ''}'")
                # Print notes in columns K to Q (indices 10 to 16)
                for col_i in range(10, min(17, len(r))):
                    if r[col_i].strip():
                        print(f"   -> Col {chr(65+col_i)} ('{rows[0][col_i]}'): '{r[col_i].strip()[:70]}...'")
                if idx > 8:
                    break

if __name__ == '__main__':
    inspect_sheet()
