import sys
import os
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def test_http_routes():
    url_add = "http://127.0.0.1:5001/api/students/EVI068/add-class"
    url_remove = "http://127.0.0.1:5001/api/students/EVI068/remove-class"

    print("Testing POST", url_add)
    r1 = requests.post(url_add, json={"class_name": "Galax 3.1"})
    print("Add response status:", r1.status_code, r1.json())
    assert r1.status_code == 200

    print("Testing POST", url_remove)
    r2 = requests.post(url_remove, json={"class_name": "Galax 3.1"})
    print("Remove response status:", r2.status_code, r2.json())
    assert r2.status_code == 200

    print("HTTP ROUTES TEST PASSED 100%!")

if __name__ == '__main__':
    test_http_routes()
