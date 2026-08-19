"""
Test kiểm tra endpoint /api/admin/sync-db-snapshot và hàm sync_db_from_host
"""
import os
import sys
import gzip

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

def test_sync_endpoint():
    client = app.test_client()

    # 1. Test unauthorized (no token)
    res_unauth = client.get('/api/admin/sync-db-snapshot')
    assert res_unauth.status_code == 401, f"Expected 401, got {res_unauth.status_code}"
    print("✅ Test 1: 401 Unauthorized khi không có token passed.")

    # 2. Test authorized with gzip
    res_auth = client.get(
        '/api/admin/sync-db-snapshot?gzip=1',
        headers={'X-Sync-Token': 'evi_secure_sync_token_2026_x9k2'}
    )
    assert res_auth.status_code == 200, f"Expected 200, got {res_auth.status_code}"
    assert res_auth.headers.get('Content-Type') == 'application/gzip'
    data = res_auth.get_data()
    print(f"✅ Test 2: 200 OK với Gzip Payload ({len(data)/(1024*1024):.2f} MB) passed.")

    # 3. Decompress test
    decompressed = gzip.decompress(data)
    assert len(decompressed) > 50 * 1024 * 1024, "Decompressed size should be > 50MB"
    print(f"✅ Test 3: Giải nén thành công CSDL SQLite gốc ({len(decompressed)/(1024*1024):.2f} MB).")

if __name__ == '__main__':
    test_sync_endpoint()
