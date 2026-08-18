import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

def test_sun16():
    url = "http://127.0.0.1:5001/api/students?class_name=Sun+1.6"
    req = urllib.request.urlopen(url)
    data = json.loads(req.read().decode('utf-8'))

    print("API Response for Sun 1.6:")
    print("  Success:", data.get('success'))
    print("  Count:", data.get('count'))
    print("  Students List:")
    for s in data.get('data', []):
        print(f"    - [{s.get('code')}] {s.get('name')} | Class: '{s.get('class_name')}' | Status: '{s.get('status')}'")

    assert data.get('count') == 11, f"Expected 11 students, got {data.get('count')}"
    print("\n✅ TEST PASSED: All 11 students of class Sun 1.6 returned correctly!")

if __name__ == '__main__':
    test_sun16()
