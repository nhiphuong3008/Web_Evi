"""
Module đồng bộ CSDL từ Production Host (PythonAnywhere) về máy Local.
Cho phép tự động cập nhật dữ liệu mới nhất mỗi khi khởi động Local Server.
"""

import os
import sys
import gzip
import shutil
import sqlite3
import logging
import requests

logger = logging.getLogger(__name__)

def sync_db_from_host(
    host_url="https://vicarecrm.pythonanywhere.com",
    secret_token="evi_secure_sync_token_2026_x9k2",
    db_path=None,
    timeout=20,
    verbose=True
):
    """
    Tải bản CSDL SQLite mới nhất từ Production Host về Local.
    Tự động sao lưu bản cũ và giải nén an toàn.
    """
    if db_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "database", "evi_center.db")

    endpoint = f"{host_url.rstrip('/')}/api/admin/sync-db-snapshot"
    headers = {"X-Sync-Token": secret_token}
    params = {"gzip": "1"}

    if verbose:
        print(f"🔄 [Sync DB] Đang kết nối tới Host ({host_url}) để kiểm tra CSDL mới nhất...")

    try:
        response = requests.get(endpoint, headers=headers, params=params, stream=True, timeout=timeout)
        if response.status_code == 401:
            if verbose:
                print("❌ [Sync DB] Sai mã bảo mật X-Sync-Token.")
            logger.warning("[Sync DB] Token không hợp lệ khi tải DB snapshot.")
            return False

        if response.status_code != 200:
            if verbose:
                print(f"⚠️ [Sync DB] Máy chủ phản hồi mã {response.status_code}. Bỏ qua đồng bộ, dùng CSDL local hiện tại.")
            return False

        temp_gz_path = db_path + ".tmp.gz"
        temp_db_path = db_path + ".tmp"
        backup_db_path = db_path.replace("evi_center.db", "evi_center_local_backup.db")

        # Ghi file tải về
        with open(temp_gz_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)

        # Giải nén GZIP
        try:
            with gzip.open(temp_gz_path, "rb") as f_in:
                with open(temp_db_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception:
            # Nếu server trả về file thô không nén
            shutil.copyfile(temp_gz_path, temp_db_path)

        if os.path.exists(temp_gz_path):
            os.remove(temp_gz_path)

        # Kiểm tra tính toàn vẹn của CSDL SQLite vừa tải
        conn = sqlite3.connect(temp_db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        st_count = cur.fetchone()[0]
        conn.close()

        # Tạo bản sao lưu DB local cũ nếu có
        if os.path.exists(db_path):
            shutil.copyfile(db_path, backup_db_path)

        # Ghi đè file DB chính
        shutil.move(temp_db_path, db_path)

        db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
        if verbose:
            print(f"✅ [Sync DB] Đồng bộ CSDL thành công từ Host!")
            print(f"   • Kích thước: {db_size_mb:.2f} MB")
            print(f"   • Tổng số học sinh: {st_count}")
            print(f"   • Đã tự động tạo bản lưu: {os.path.basename(backup_db_path)}")
        logger.info(f"✅ [Sync DB] Đã đồng bộ CSDL từ {host_url} ({st_count} học sinh, {db_size_mb:.2f}MB)")
        return True

    except requests.exceptions.RequestException as req_err:
        if verbose:
            print(f"⚠️ [Sync DB] Không thể kết nối tới Host ({req_err}). Dùng CSDL local hiện tại.")
        logger.warning(f"[Sync DB] Kết nối Host thất bại: {req_err}")
        return False
    except Exception as ex:
        if verbose:
            print(f"⚠️ [Sync DB] Lỗi khi xử lý CSDL: {ex}. Dùng CSDL local hiện tại.")
        logger.error(f"[Sync DB] Lỗi đồng bộ: {ex}")
        return False
