import urllib.request
import json

url = 'http://127.0.0.1:5001/api/students?class_name=Galax+1.3'
r = urllib.request.urlopen(url)
d = json.loads(r.read())
count = d.get('count', 0)
print(f"Live API returned {count} students for Galax 1.3:")
for s in d.get('data', []):
    code = s.get('code', '???')
    name = s.get('name', '???').encode('ascii', 'ignore').decode('ascii')
    print(f"  {code} - {name}")
