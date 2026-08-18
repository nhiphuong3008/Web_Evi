import time
import subprocess
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_keep_alive():
    print("🚀 [KeepAlive Worker] Khởi động tiến trình tự động duy trì Website EVI & Localtunnel...")
    
    flask_proc = None
    tunnel_proc = None

    while True:
        try:
            # 1. Kiểm tra Flask server 5001
            import urllib.request
            server_healthy = False
            try:
                req = urllib.request.Request("http://127.0.0.1:5001/api/health")
                with urllib.request.urlopen(req, timeout=4) as resp:
                    if resp.status == 200:
                        server_healthy = True
            except Exception:
                server_healthy = False

            if not server_healthy:
                print("⚠️ [KeepAlive] Flask server 5001 ngắt kết nối. Đang khởi động lại `python app.py`...")
                if flask_proc and flask_proc.poll() is None:
                    try:
                        flask_proc.kill()
                    except Exception:
                        pass
                flask_proc = subprocess.Popen([sys.executable, "app.py"], cwd=PROJECT_DIR)
                time.sleep(4)

            # 2. Kiểm tra Localtunnel process
            if tunnel_proc is None or tunnel_proc.poll() is not None:
                print("🔄 [KeepAlive] Localtunnel ngắt kết nối. Đang khởi tạo lại tunnel https://busy-carpets-fly.loca.lt...")
                cmd = 'cmd.exe /c "npx -y localtunnel --port 5001 --subdomain busy-carpets-fly"'
                tunnel_proc = subprocess.Popen(cmd, cwd=PROJECT_DIR, shell=True)

        except Exception as e:
            print(f"❌ [KeepAlive Error]: {e}")
            
        time.sleep(10)

if __name__ == '__main__':
    run_keep_alive()
