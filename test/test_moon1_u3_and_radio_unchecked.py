import sys
import os
import requests
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_moon1_u3():
    # 1. Test JSON syllabus data
    with open("static/js/moon_syllabus_db.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    m1_u3 = data["Moon 1"]["Unit 03"]
    assert m1_u3["subtitle"] == "UNIT 3: CLASSROOM"
    assert "Book" in m1_u3["vocab"]
    assert "Shelf" in m1_u3["vocab"]
    assert "Letter C - /c/(Cut, Candy, Candy Cat)" in m1_u3["phonics"]
    print("  • Moon 1 Unit 3 (CLASSROOM) syllabus verified 100%!")

    # 2. Test PDF API endpoint for Moon 1 Unit 3
    r = requests.get("http://127.0.0.1:5001/api/students/EVI068/test-report-pdf?is_moon=1&class_name=Moon+1.1&test_name=Unit+3")
    assert r.status_code == 200
    assert "UNIT 3: CLASSROOM" in r.text
    assert "Crayon" in r.text
    assert "Eraser" in r.text
    print("  • PDF Moon 1 Unit 3 (CLASSROOM) verified 100%!")

    # 3. Test cm_portal.js for no radio checked attribute
    with open("static/js/cm_portal.js", "r", encoding="utf-8") as js_f:
        js_content = js_f.read()
    
    assert 'value="excellent" checked' not in js_content
    print("  • cm_portal.js radio buttons are UNCHECKED (blank for manual ticking) 100%!")

    print("\nALL MOON 1 UNIT 3 & UNCHECKED RADIO TESTS PASSED 100%!")

if __name__ == '__main__':
    test_moon1_u3()
