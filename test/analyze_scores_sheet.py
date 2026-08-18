import urllib.request, csv, io, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = "1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA"

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=1373957511"
req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=120) as resp:
    data = resp.read().decode('utf-8')
reader = csv.reader(io.StringIO(data))
rows = list(reader)

print(f"Total rows: {len(rows)}")

# The header is in row 0 (or first few rows)
# Let's analyze header row
print(f"\nHeader row (row 0): {[(j, c) for j, c in enumerate(rows[0]) if c.strip()]}")
print(f"Row 1: {[(j, c) for j, c in enumerate(rows[1]) if c.strip()]}")
print(f"Row 2: {[(j, c) for j, c in enumerate(rows[2]) if c.strip()]}")
print(f"Row 3: {[(j, c) for j, c in enumerate(rows[3]) if c.strip()]}")

# Count real student data rows (has EVI code)
evi_rows = [r for r in rows if len(r) > 1 and r[1].strip().startswith('EVI')]
print(f"\nRows with EVI codes: {len(evi_rows)}")

# Find all unique class names
all_classes = sorted(set(r[4].strip() for r in evi_rows if len(r) > 4 and r[4].strip()))
print(f"All unique classes in data: {all_classes}")

# Find all unique test names
all_tests = sorted(set(r[7].strip() for r in evi_rows if len(r) > 7 and r[7].strip()))
print(f"All unique test names: {all_tests}")

# Find the month/year range
months = sorted(set(r[0].strip() for r in evi_rows if len(r) > 0 and r[0].strip()))
print(f"All month/year values: {months}")

# Count per class
print("\nRecords per class:")
from collections import Counter
cls_counts = Counter(r[4].strip() for r in evi_rows if len(r) > 4)
for k, v in sorted(cls_counts.items()):
    print(f"  {k:20s}: {v}")

# Count per test
print("\nRecords per test:")
test_counts = Counter(r[7].strip() for r in evi_rows if len(r) > 7)
for k, v in sorted(test_counts.items()):
    print(f"  {k:20s}: {v}")

# Sample some rows with full column details
print("\n\n=== SAMPLE 5 RECORDS (full columns) ===")
for r in evi_rows[:5]:
    data_cols = {j: c.strip() for j, c in enumerate(r) if c.strip()}
    print(f"  {data_cols}")
