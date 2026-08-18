import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app

app = create_app()

def verify_endpoints():
    print("--- Testing API Endpoints via Flask Test Client ---")
    with app.test_client() as client:
        # 1. Test GET /api/schedule/holiday-history
        r1 = client.get('/api/schedule/holiday-history')
        print("1. History Endpoint Status:", r1.status_code, r1.get_json())
        assert r1.status_code == 200

        # 2. Test POST /api/schedule/holiday-shift/preview for a single class
        r2 = client.post('/api/schedule/holiday-shift/preview', json={
            'start_date': '2026-09-01',
            'end_date': '2026-09-02',
            'affected_classes': ['Galax 1.3']
        })
        print("2. Preview Single Class Status:", r2.status_code, r2.get_json())
        assert r2.status_code == 200

        # 3. Test POST /api/schedule/holiday-shift/preview for ALL
        r3 = client.post('/api/schedule/holiday-shift/preview', json={
            'start_date': '2026-09-01',
            'end_date': '2026-09-02',
            'affected_classes': ['ALL']
        })
        print("3. Preview ALL Status:", r3.status_code)
        assert r3.status_code == 200

    print("\n✅ API ENDPOINTS VERIFIED SUCCESSFULLY!")

if __name__ == '__main__':
    verify_endpoints()
