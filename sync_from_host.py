"""
Script 1-Click: Tải và đồng bộ CSDL SQLite mới nhất từ Cloud PythonAnywhere về máy Local.
Chạy: python sync_from_host.py
"""

import os
import sys

# Đảm bảo import được module trong project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from services.sync_host_db import sync_db_from_host

if __name__ == '__main__':
    config = get_config()
    host_url = getattr(config, 'PRODUCTION_HOST_URL', 'https://vicarecrm.pythonanywhere.com')
    secret_token = getattr(config, 'SYNC_SECRET_TOKEN', 'evi_secure_sync_token_2026_x9k2')

    print("\n" + "=" * 65)
    print("  🚀 ĐỒNG BỘ CSDL SQLITE TỪ HOST PYTHONANYWHERE ➔ LOCAL")
    print("=" * 65)
    print(f"  🌐 Host:  {host_url}")
    print("=" * 65)

    success = sync_db_from_host(
        host_url=host_url,
        secret_token=secret_token,
        verbose=True
    )

    if success:
        print("\n🎉 Hoàn tất! CSDL trên máy local đã được cập nhật 100% khớp với Host.\n")
    else:
        print("\n⚠️ Quá trình đồng bộ chưa thành công. Bạn vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau.\n")
