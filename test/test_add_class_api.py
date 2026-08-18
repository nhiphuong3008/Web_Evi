import requests, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = 'http://127.0.0.1:5001/api'

def test_class_management():
    # 1. Add new class
    payload = {
        'class_name': 'Galax 3.3 Test',
        'schedule': 'MT5 (17:30 - 19:00)',
        'start_date': '2026-08-15',
        'curriculum': 'Galax',
        'teacher': 'Teacher Mark',
        'cm_staff': 'Thục Anh',
        'room': 'Jupiter',
        'status': 'Đang hoạt động'
    }

    res = requests.post(f"{BASE_URL}/classes", json=payload)
    print("Add class response:", res.status_code, res.json())
    assert res.json().get('success') == True

    # 2. Check get classes (default should include active class)
    res_get = requests.get(f"{BASE_URL}/cm/classes")
    c_list = res_get.json().get('data', [])
    c_names = [c['class_name'] for c in c_list]
    print("Active class names count:", len(c_names))
    assert 'Galax 3.3 Test' in c_names

    # 3. Update status to Đã kết thúc
    res_status = requests.post(f"{BASE_URL}/classes/status", json={'class_name': 'Galax 3.3 Test', 'status': 'Đã kết thúc'})
    print("Update status response:", res_status.json())
    assert res_status.json().get('success') == True

    # 4. Check get classes default (include_ended=false) -> Galax 3.3 Test should NOT appear!
    res_get_active = requests.get(f"{BASE_URL}/cm/classes")
    active_names = [c['class_name'] for c in res_get_active.json().get('data', [])]
    print("Active class names after end:", len(active_names))
    assert 'Galax 3.3 Test' not in active_names

    # 5. Check get classes with include_ended=true -> Galax 3.3 Test SHOULD appear!
    res_get_all = requests.get(f"{BASE_URL}/cm/classes?include_ended=true")
    all_names = [c['class_name'] for c in res_get_all.json().get('data', [])]
    assert 'Galax 3.3 Test' in all_names

    # Clean up test class
    requests.post(f"{BASE_URL}/classes/status", json={'class_name': 'Galax 3.3 Test', 'status': 'Đã kết thúc'})
    print("All tests passed cleanly!")

if __name__ == '__main__':
    test_class_management()
