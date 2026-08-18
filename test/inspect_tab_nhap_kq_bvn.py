import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import get_config
from services.google_sheets import GoogleSheetsService

def inspect_tab():
    config = get_config()
    target_id = "1wKcmRH9azv9urXvp-Ld4zWwmZ-iuGA2Vo30WzEkBR1I"
    svc = GoogleSheetsService(config.GOOGLE_SHEETS_CREDENTIALS_FILE, target_id)
    if not svc.connect():
        print("Cannot connect")
        return

    # Open Tab 'Nhập KQ BVN'
    try:
        ws = svc.spreadsheet.worksheet("Nhập KQ BVN")
        all_vals = ws.get_all_values()
        print(f"Total rows in 'Nhap KQ BVN': {len(all_vals)}")
        print("\n--- Header rows (First 5 rows) ---")
        for idx in range(min(5, len(all_vals))):
            row_str = " | ".join([str(c).encode('ascii', 'ignore').decode('ascii') for c in all_vals[idx][:15]])
            print(f"Row {idx+1}: {row_str}")

        print("\n--- Sample data rows (Rows 6-15) ---")
        for idx in range(5, min(15, len(all_vals))):
            row = all_vals[idx]
            row_str = " | ".join([str(c).encode('ascii', 'ignore').decode('ascii') for c in row[:15]])
            if any(str(c).strip() for c in row[:15]):
                print(f"Row {idx+1:3d}: {row_str}")

    except Exception as e:
        print(f"Error inspecting tab: {e}")

if __name__ == '__main__':
    inspect_tab()
