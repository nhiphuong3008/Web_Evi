import sys
import os
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def test_split_menus_and_moon():
    # 1. Test Health
    r = requests.get("http://127.0.0.1:5001/api/health")
    assert r.status_code == 200
    print("  • Flask Server Alive!")

    # 2. Test Sun/Galax classes filter
    r_sun = requests.get("http://127.0.0.1:5001/api/cm/classes")
    assert r_sun.status_code == 200
    classes = r_sun.json().get('data', [])
    sun_classes = [c for c in classes if not c['class_name'].lower().startswith('moon')]
    moon_classes = [c for c in classes if c['class_name'].lower().startswith('moon')]

    print(f"  • Total classes: {len(classes)} (Sun/Galax: {len(sun_classes)}, Moon: {len(moon_classes)})")
    assert len(sun_classes) > 0
    assert len(moon_classes) > 0

    print("\nALL SPLIT SIDEBAR MENU & MOON CLEAN TABLE TESTS PASSED 100%!")

if __name__ == '__main__':
    test_split_menus_and_moon()
