import urllib.request
import json

# Check what the live server actually sees for EVI122
url = 'http://127.0.0.1:5001/api/students?search=EVI122'
r = urllib.request.urlopen(url)
d = json.loads(r.read())
count = d.get('count', 0)
print(f"Live API search for EVI122 returned {count} students:")
for s in d.get('data', []):
    code = s.get('code', '???')
    name = s.get('name', '???').encode('ascii', 'ignore').decode('ascii')
    cls = str(s.get('class_name', '')).encode('ascii', 'ignore').decode('ascii')
    status = str(s.get('status', '')).encode('ascii', 'ignore').decode('ascii')
    print(f"  {code} | Name: {name} | Class: '{cls}' | Status: '{status}'")
