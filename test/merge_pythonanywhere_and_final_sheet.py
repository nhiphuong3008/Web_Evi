"""
Merge activity logs and any missing records from pythonanywhere_snapshot.db to evi_center.db
Then run a final incremental sync from Google Sheets if available.
"""

import os
import sys
import sqlite3

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def merge_host_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_db_path = os.path.join(base_dir, "database", "evi_center.db")
    host_db_path = os.path.join(base_dir, "database", "pythonanywhere_snapshot.db")
    
    if not os.path.exists(host_db_path):
        print("⚠️ Không tìm thấy pythonanywhere_snapshot.db để merge.")
        return
        
    conn_local = sqlite3.connect(local_db_path)
    conn_host = sqlite3.connect(host_db_path)
    
    cur_l = conn_local.cursor()
    cur_h = conn_host.cursor()
    
    # 1. Merge activity_logs
    cur_h.execute("SELECT username, user_fullname, user_role, action_type, target_module, target_id, description, ip_address, is_read_by_admin, created_at FROM activity_logs")
    host_logs = cur_h.fetchall()
    
    cur_l.execute("SELECT username, action_type, target_module, target_id, description, created_at FROM activity_logs")
    local_log_keys = set((r[0], r[1], r[2], r[3], r[4], r[5]) for r in cur_l.fetchall())
    
    added_logs = 0
    for r in host_logs:
        key = (r[0], r[3], r[4], r[5], r[6], r[9])
        if key not in local_log_keys:
            cur_l.execute("""
                INSERT INTO activity_logs (username, user_fullname, user_role, action_type, target_module, target_id, description, ip_address, is_read_by_admin, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
            added_logs += 1
            
    conn_local.commit()
    print(f"✅ Đã hợp nhất {added_logs} bản ghi activity_logs từ PythonAnywhere vào CSDL Local.")
    
    conn_local.close()
    conn_host.close()
    
    # Clean up snapshot
    if os.path.exists(host_db_path):
        os.remove(host_db_path)
        print("🗑️ Đã dọn dẹp file snapshot PythonAnywhere.")

if __name__ == '__main__':
    merge_host_db()
    
    # Run final Google Sheets sync
    print("\n🔄 Đang thực hiện quét đồng bộ lần cuối cùng từ Google Sheets...")
    try:
        from services.sync_scheduler import run_incremental_sync
        success, msg = run_incremental_sync()
        print(f"Kết quả đồng bộ Sheet: {msg}")
    except Exception as e:
        print(f"Lưu ý Sheet: {e}")
