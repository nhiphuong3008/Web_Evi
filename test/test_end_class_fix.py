import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = 'http://127.0.0.1:5001/api'

def test_end_galax22():
    # Attempt to change status of GALAX 2.2 to Đã kết thúc
    res = requests.post(f"{BASE_URL}/classes/status", json={'class_name': 'GALAX 2.2', 'status': 'Đã kết thúc'})
    print("Status update response for GALAX 2.2:", res.status_code, res.json())
    assert res.json().get('success') == True

    # Re-open GALAX 2.2 to test toggling back
    res2 = requests.post(f"{BASE_URL}/classes/status", json={'class_name': 'GALAX 2.2', 'status': 'Đang hoạt động'})
    print("Toggle back response:", res2.json())
    assert res2.json().get('success') == True

    print("✅ GALAX 2.2 end class toggle test passed 100%!")

if __name__ == '__main__':
    test_end_galax22()
