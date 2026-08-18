import urllib.request, csv, io, sys, os
sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = "1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA"

# GID 1373957511 looks like it has student grades data (dates + class + tests)
# GID 857957658 - discovered from HTML (another data sheet)
# GID 1625976022 - student info with scores

for gid in [1373957511, 857957658, 1625976022]:
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={gid}"
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8')
        
        reader = csv.reader(io.StringIO(data))
        rows = list(reader)
        non_empty = [r for r in rows if any(c.strip() for c in r)]
        
        print(f"\n{'='*150}")
        print(f"GID {gid}: {len(non_empty)} non-empty rows, max cols: {max(len(r) for r in non_empty)}")
        
        # Print ALL rows with ALL columns
        for i, r in enumerate(non_empty):
            # Print full row
            vals = [c.strip() for c in r if c.strip()]
            print(f"  Row {i:3d} ({len(vals)} vals): {vals}")
            
    except Exception as e:
        print(f"GID {gid}: ERROR - {e}")
