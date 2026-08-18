import os, openpyxl, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\14. Class syllabus (official)\MT_B5_Galax 1.3 (20_4_2026).xlsx"
wb = openpyxl.load_workbook(filepath, data_only=True)
ws = wb['Basic']

rows = list(ws.iter_rows(values_only=True))
print(f"Sheet: Basic | Total rows: {len(rows)}")
print("="*100)

for idx in range(20, 32):
    r = rows[idx]
    if r:
        r_str = [str(cell).strip() if cell is not None else '' for cell in r[:6]]
        print(f"Row {idx:2d} | Col0:{r_str[0]:20s} | Col1:{r_str[1]:8s} | Col2:{r_str[2]:30s} | Col3:{r_str[3]:30s}")

