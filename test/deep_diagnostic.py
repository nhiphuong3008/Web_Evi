"""Deep diagnostic v2 - check API response structures and DB field names."""
import sys, os, json, requests
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = "http://localhost:5001"

# 1. Dashboard summary structure
print("=" * 60)
print("1. DASHBOARD SUMMARY API STRUCTURE")
print("=" * 60)
r = requests.get(f"{BASE}/api/dashboard/summary", timeout=30)
d = r.json()
print(f"Top-level keys: {list(d.keys())}")
if 'data' in d:
    inner = d['data']
    print(f"  data keys: {list(inner.keys()) if isinstance(inner, dict) else type(inner).__name__}")
    if isinstance(inner, dict):
        if 'kpi' in inner:
            print(f"  data.kpi keys: {list(inner['kpi'].keys())}")
            print(f"  data.kpi.total_students: {inner['kpi'].get('total_students')}")
            print(f"  data.kpi.active_classes: {inner['kpi'].get('active_classes')}")
        print(f"  data.total_students: {inner.get('total_students', 'MISSING')}")
        rm = inner.get('renewal_monthly')
        print(f"  data.renewal_monthly type: {type(rm).__name__}, len: {len(rm) if rm else 0}")

# 2. Students API structure
print("\n" + "=" * 60)
print("2. STUDENTS API STRUCTURE")
print("=" * 60)
r = requests.get(f"{BASE}/api/students", timeout=15)
d = r.json()
print(f"Response keys: {list(d.keys())}")
students = d.get('data', [])
print(f"Students count: {len(students)}")
if students:
    s0 = students[0]
    print(f"First student keys: {sorted(s0.keys())}")
    print(f"  code: {s0.get('code')}")
    print(f"  name: {s0.get('name')}")
    print(f"  class_name: {s0.get('class_name')}")
    print(f"  status: {s0.get('status')}")

    # Count active without class
    active = [s for s in students if s.get('status') == 'Dang hoc']
    print(f"\n  Students with status 'Dang hoc': {len(active)}")
    active2 = [s for s in students if 'ang h' in (s.get('status') or '')]
    print(f"  Students with status containing 'ang h': {len(active2)}")
    
    # Find distinct statuses
    statuses = {}
    for s in students:
        st = s.get('status', 'null')
        statuses[st] = statuses.get(st, 0) + 1
    print(f"  Status distribution:")
    for st, cnt in sorted(statuses.items(), key=lambda x: -x[1]):
        print(f"    '{st}': {cnt}")

    # Active students without class
    no_class = [s for s in active2 if not s.get('class_name') or s['class_name'].strip() in ['', '-']]
    print(f"\n  Active students without valid class: {len(no_class)}")
    for s in no_class[:10]:
        print(f"    {s.get('code')} | {s.get('name')} | class='{s.get('class_name')}' | status='{s.get('status')}'")

# 3. Check routes
print("\n" + "=" * 60)
print("3. API ROUTES CHECK")
print("=" * 60)
endpoints = [
    "/api/health",
    "/api/dashboard/summary",
    "/api/students",
    "/api/schedule",
    "/api/classes",
    "/api/syllabus",
    "/api/syllabus/classes",
    "/api/lessons",
    "/api/crm/renewals/pipeline",
    "/api/interactions",
    "/api/parent-interactions",
    "/api/schedule/holiday-history",
    "/api/auth/me",
    "/api/auth/user",
    "/api/users",
    "/api/cm/classes",
]
for path in endpoints:
    try:
        r = requests.get(f"{BASE}{path}", timeout=5)
        print(f"  {'OK' if r.status_code == 200 else 'XX'} [{r.status_code}] GET {path}")
    except Exception as e:
        print(f"  !! GET {path}: {e}")

# 4. Check CRM pipeline structure
print("\n" + "=" * 60)
print("4. CRM PIPELINE STRUCTURE")
print("=" * 60)
r = requests.get(f"{BASE}/api/crm/renewals/pipeline", timeout=15)
d = r.json()
print(f"Response keys: {list(d.keys())}")
if 'data' in d:
    inner = d['data'] if isinstance(d.get('data'), dict) else d
    print(f"  data keys: {list(inner.keys()) if isinstance(inner, dict) else 'N/A'}")
else:
    inner = d
for k in ['pipeline', 'kpi', 'cm_leaderboard', 'students']:
    if k in inner:
        val = inner[k]
        if isinstance(val, dict):
            print(f"  {k}: dict with keys {list(val.keys())}")
        elif isinstance(val, list):
            print(f"  {k}: list with {len(val)} items")

# 5. Schedule detail
print("\n" + "=" * 60)
print("5. SCHEDULE STRUCTURE")
print("=" * 60)
r = requests.get(f"{BASE}/api/schedule", timeout=15)
d = r.json()
print(f"Response keys: {list(d.keys())}")
schedule = d.get('data', d.get('schedule', d if isinstance(d, list) else []))
if isinstance(schedule, list):
    print(f"Schedule entries: {len(schedule)}")
elif isinstance(schedule, dict):
    print(f"Schedule dict keys: {list(schedule.keys())}")
    
print("\nDiagnostic complete!")
