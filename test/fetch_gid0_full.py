import urllib.request, csv, io, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = "1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA"

# The first sheet (gid=0 default) had "Tra cứu điểm số học viên" section with columns
# Let me look more carefully at the default sheet (gid=0) - the "BÁO CÁO ĐIỂM SỐ" dashboard
# It mentions "Sun 1.6" and individual student scores in row 5

# Let me try to get the full first sheet more carefully
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = resp.read().decode('utf-8')
reader = csv.reader(io.StringIO(data))
rows = list(reader)

print(f"GID 0: {len(rows)} rows, max cols: {max(len(r) for r in rows)}")
print()
for i, r in enumerate(rows):
    # Show ALL columns
    full = [c for c in r]
    # Only show rows with some data
    if any(c.strip() for c in full):
        # Print columns with data
        data_cols = [(j, c.strip()) for j, c in enumerate(full) if c.strip()]
        print(f"Row {i:2d}: {data_cols}")
