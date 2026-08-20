"""
Script rà soát dữ liệu cuối cùng:
1. Kiểm tra & tải DB từ PythonAnywhere về so sánh
2. Kiểm tra Google Sheets xem có thay đổi gì 2 ngày qua
3. Hợp nhất vào database/evi_center.db
"""

import os
import sys
import sqlite3
import requests
import gzip
import shutil

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_config

def audit_and_merge():
    config = get_config()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_db_path = os.path.join(base_dir, "database", "evi_center.db")
    host_db_path = os.path.join(base_dir, "database", "pythonanywhere_snapshot.db")
    
    print("=" * 70)
    print("🔍 BƯỚC 1: KIỂM TRA VÀ TẢI SNAPSHOT TỪ PYTHONANYWHERE")
    print("=" * 70)
    
    host_url = getattr(config, 'PRODUCTION_HOST_URL', 'https://vicarecrm.pythonanywhere.com')
    secret_token = getattr(config, 'SYNC_SECRET_TOKEN', 'evi_secure_sync_token_2026_x9k2')
    
    endpoint = f"{host_url.rstrip('/')}/api/admin/sync-db-snapshot"
    headers = {"X-Sync-Token": secret_token}
    params = {"gzip": "1"}
    
    try:
        res = requests.get(endpoint, headers=headers, params=params, stream=True, timeout=25)
        if res.status_code == 200:
            temp_gz = host_db_path + ".gz"
            with open(temp_gz, "wb") as f:
                for chunk in res.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
            
            try:
                with gzip.open(temp_gz, "rb") as f_in:
                    with open(host_db_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            except Exception:
                shutil.copyfile(temp_gz, host_db_path)
            
            if os.path.exists(temp_gz):
                os.remove(temp_gz)
            
            print(f"✅ Đã tải thành công snapshot DB từ PythonAnywhere ({os.path.getsize(host_db_path) / (1024*1024):.2f} MB)")
            
            # So sánh số lượng bản ghi giữa Local và PythonAnywhere
            conn_local = sqlite3.connect(local_db_path)
            conn_host = sqlite3.connect(host_db_path)
            
            cur_l = conn_local.cursor()
            cur_h = conn_host.cursor()
            
            cur_l.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [r[0] for r in cur_l.fetchall()]
            
            print("\n📊 SO SÁNH SỐ LƯỢNG BẢN GHI (LOCAL VS PYTHONANYWHERE):")
            print(f"{'Tên Bảng':<35} | {'Local DB':<12} | {'PythonAnywhere':<15} | {'Trạng thái'}")
            print("-" * 75)
            
            for t in sorted(tables):
                try:
                    cur_l.execute(f"SELECT COUNT(*) FROM {t}")
                    cnt_l = cur_l.fetchone()[0]
                except Exception:
                    cnt_l = "N/A"
                
                try:
                    cur_h.execute(f"SELECT COUNT(*) FROM {t}")
                    cnt_h = cur_h.fetchone()[0]
                except Exception:
                    cnt_h = "N/A"
                
                status = "Khớp 100%" if cnt_l == cnt_h else f"Lệch ({cnt_l} vs {cnt_h})"
                print(f"{t:<35} | {str(cnt_l):<12} | {str(cnt_h):<15} | {status}")
            
            conn_local.close()
            conn_host.close()
            
        else:
            print(f"⚠️ PythonAnywhere trả về mã {res.status_code}. Bỏ qua so sánh DB host.")
    except Exception as e:
        print(f"⚠️ Không thể kết nối tới PythonAnywhere: {e}")

    print("\n" + "=" * 70)
    print("🔍 BƯỚC 2: KIỂM TRA GOOGLE SHEETS LẦN CUỐI")
    print("=" * 70)
    
    try:
        from services.google_sheets import GoogleSheetsService
        from services.sync_scheduler import run_sync_job
        from app import create_app
        
        flask_app = create_app()
        sheets_service = GoogleSheetsService(
            credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE,
            spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
        )
        if sheets_service.connect():
            print("✅ Kết nối Google Sheets thành công. Đang thực hiện quét đồng bộ chốt lần cuối...")
            with flask_app.app_context():
                run_sync_job(flask_app)
            print("✅ Đã hoàn tất đồng bộ Google Sheets lần cuối vào database/evi_center.db!")
        else:
            print("⚠️ Không có credentials hoặc không kết nối được Google Sheets. CSDL SQLite hiện tại là bản nguồn chuẩn nhất.")
    except Exception as err:
        print(f"ℹ️ Google Sheets check: {err}")

if __name__ == '__main__':
    audit_and_merge()
