import urllib.request, csv, io, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = "1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA"

# GID 1373957511 - the big sheet with 25k+ rows
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1373957511"
req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read().decode('utf-8')
reader = csv.reader(io.StringIO(data))
rows = list(reader)

print(f"Total rows: {len(rows)}, max cols: {max(len(r) for r in rows)}")

# Print first 50 rows to understand the structure
for i, r in enumerate(rows[:50]):
    data_cols = [(j, c.strip()) for j, c in enumerate(r) if c.strip()]
    if data_cols:
        print(f"Row {i:3d}: {data_cols}")

# Also check where "class" names appear
print("\n\n=== Looking for class names / section headers ===")
class_names = set()
for i, r in enumerate(rows[:5000]):
    for j, c in enumerate(r):
        cs = c.strip()
        if re.match(r'^(Sun|Moon|Galax)\s+\d', cs, re.IGNORECASE):
            class_names.add(cs)
            if i < 100:
                print(f"Row {i:5d}, Col {j:2d}: '{cs}'")

print(f"\nAll class names found in first 5000 rows: {sorted(class_names)}")
