import urllib.request, json, csv, io, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Google Sheet ID
SHEET_ID = "1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA"

# First, try to get a list of all sheet names using the htmlview endpoint
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/htmlview"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
    
    # Find sheet tab names
    import re
    # Look for sheet tab names in the HTML
    tabs = re.findall(r'class="[^"]*tab-name[^"]*"[^>]*>([^<]+)<', html)
    if not tabs:
        tabs = re.findall(r'sheet-tab[^>]*>([^<]+)<', html)
    if not tabs:
        tabs = re.findall(r'"sheet_name":"([^"]+)"', html)
    if not tabs:
        # Search for gid patterns 
        gids = re.findall(r'gid[=:](\d+)', html)
        tabs_raw = re.findall(r'>([^<]{2,40})</(?:a|span|div)', html)
        print(f"Found GIDs: {list(set(gids))[:20]}")
        print(f"Some tab-like elements: {tabs_raw[:20]}")
    else:
        print(f"Found sheets: {tabs}")
except Exception as e:
    print(f"Error getting sheet tabs: {e}")

# Try fetching data for multiple GIDs  
known_gids = [0]
# Try common GIDs to discover sheets
test_gids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
             100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
             1234567890, 2000000000]

for gid in test_gids:
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={gid}"
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode('utf-8')
            # Parse CSV and get first row to identify sheet
            reader = csv.reader(io.StringIO(data))
            rows = list(reader)
            if rows:
                first_cell = rows[0][0] if rows[0] else ""
                row_count = len([r for r in rows if any(c.strip() for c in r)])
                print(f"GID {gid:>12d}: '{first_cell[:50]}...' | {row_count} non-empty rows")
    except Exception as e:
        pass  # GID doesn't exist

