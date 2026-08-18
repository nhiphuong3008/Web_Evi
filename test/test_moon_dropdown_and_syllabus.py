import sys
import os
import requests
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_moon_dropdowns():
    # 1. Verify Moon syllabus JSON
    with open("static/js/moon_syllabus_db.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    moon1_u4 = data["Moon 1"]["Unit 04"]
    assert moon1_u4["subtitle"] == "UNIT 4: MY FACE"
    assert "Ear" in moon1_u4["vocab"]
    assert "Teeth" in moon1_u4["vocab"]
    print("  • Moon 1 Unit 4 (MY FACE) syllabus verified!")

    moon3_u1 = data["Moon 3"]["Unit 01"]
    assert moon3_u1["subtitle"] == "UNIT 1: HELLO"
    assert "We are quiet" in moon3_u1["vocab"]
    assert "Scooter" in moon3_u1["vocab"]
    print("  • Moon 3 Unit 1 (HELLO) syllabus verified!")

    # 2. Verify Moon PDF rendering
    r1 = requests.get("http://127.0.0.1:5001/api/students/EVI068/test-report-pdf?is_moon=1&class_name=Moon+1.1&test_name=Unit+4")
    assert r1.status_code == 200
    assert "UNIT 4: MY FACE" in r1.text
    assert "Teeth" in r1.text
    print("  • PDF Moon 1 Unit 4 verified!")

    r2 = requests.get("http://127.0.0.1:5001/api/students/EVI068/test-report-pdf?is_moon=1&class_name=Moon+3.1&test_name=Unit+1")
    assert r2.status_code == 200
    assert "UNIT 1: HELLO" in r2.text
    assert "We are quiet" in r2.text
    print("  • PDF Moon 3 Unit 1 verified!")

    print("\nALL MOON DROPDOWN & SYLLABUS TESTS PASSED 100%!")

if __name__ == "__main__":
    test_moon_dropdowns()
