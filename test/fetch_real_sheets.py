import urllib.request, csv, io, sys, os
sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = "1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA"

# Real GIDs discovered from HTML
real_gids = [1373957511, 857957658, 2045547967, 1625976022, 260368934, 447453409, 788254536]

for gid in real_gids:
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={gid}"
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8')
            reader = csv.reader(io.StringIO(data))
            rows = list(reader)
            non_empty = [r for r in rows if any(c.strip() for c in r)]
            
            # Print header info
            print(f"\n{'='*120}")
            print(f"GID {gid}: {len(non_empty)} non-empty rows")
            
            # Print first 15 rows to understand structure
            for i, r in enumerate(non_empty[:15]):
                # Trim empty cells at end
                trimmed = [c for c in r if c.strip()]
                if len(trimmed) > 8:
                    trimmed = trimmed[:8] + [f"...+{len(trimmed)-8} more"]
                print(f"  Row {i:2d}: {trimmed}")
                
    except Exception as e:
        print(f"GID {gid}: ERROR - {e}")
