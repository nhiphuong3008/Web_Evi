import os, openpyxl, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\14. Class syllabus (official)\MT_B5_Galax 1.3 (20_4_2026).xlsx"
wb = openpyxl.load_workbook(filepath, data_only=True)

for sname in wb.sheetnames:
    ws = wb[sname]
    rows = list(ws.iter_rows(values_only=True, max_row=40))
    print(f"\n--- Sheet: {sname} (rows: {len(rows)}) ---")
    for idx, r in enumerate(rows[:10]):
        if r and any(r):
            r_str = [str(cell).strip() if cell is not None else '' for cell in r[:6]]
            print(f"  Row {idx:2d}: {r_str}")

