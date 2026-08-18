import os, openpyxl, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\14. Class syllabus (official)\MT_B5_Galax 1.3 (20_4_2026).xlsx"

wb = openpyxl.load_workbook(filepath, data_only=True)
print(f"Sheet names: {wb.sheetnames}")
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

print(f"File: {os.path.basename(filepath)} | Sheet: {ws.title} | Total rows: {len(rows)}")
print("="*100)

for idx, r in enumerate(rows):
    if r and any(r):
        r_str = [str(cell).strip() if cell is not None else '' for cell in r]
        # Check rows around 23, 24, 25
        if any(x in r_str[0:3] for x in ['23', '24', '25', '26', '27', 'LESSON 24', 'LESSON 25']):
            print(f"Row {idx:3d} | Col0:{r_str[0]:12s} | Col1:{r_str[1]:12s} | Col2:{r_str[2]:30s} | Col3:{r_str[3]:30s}")

