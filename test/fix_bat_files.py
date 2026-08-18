import os

start_web_content = """@echo off
chcp 65001 >nul
title EVI Dashboard Launcher
echo ============================================================
echo   KHỞI ĐỘNG EVI DASHBOARD (BACKEND VÀ FRONTEND)
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Đang tắt các phiên bản app.py cũ (nếu có)...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance" >nul 2>&1

echo [2/3] Đang khởi chạy Python Backend Server (app.py)...
set "PY_CMD=python"
if exist "%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe"
)

start "EVI Dashboard Server" /min "%PY_CMD%" app.py

echo [3/3] Đang chờ Server khởi tạo và kết nối Google Sheets...
set "COUNT=0"
:WAIT_LOOP
ping 127.0.0.1 -n 2 >nul
powershell -Command "try { (New-Object System.Net.Sockets.TcpClient).Connect('127.0.0.1', 5000); exit 0 } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto SERVER_READY
set /a COUNT+=1
if %COUNT% GEQ 25 goto TIMEOUT_ERR
echo       Đang chờ backend sẵn sàng... (%COUNT%s)
goto WAIT_LOOP

:SERVER_READY
echo.
echo ============================================================
echo   ĐÃ BẬT THÀNH CÔNG!
echo   Địa chỉ web: http://127.0.0.1:5000
echo   Nút tắt: Nhấp đúp vào file "stop_web.bat" để tắt nhanh.
echo ============================================================
start http://127.0.0.1:5000
ping 127.0.0.1 -n 4 >nul
exit /b 0

:TIMEOUT_ERR
echo.
echo ============================================================
echo   [CẢNH BÁO] Server mất nhiều thời gian hơn dự kiến (25s).
echo   Đang tự động mở trình duyệt...
echo ============================================================
start http://127.0.0.1:5000
ping 127.0.0.1 -n 5 >nul
exit /b 1
"""

stop_web_content = """@echo off
chcp 65001 >nul
title EVI Dashboard Stopper
echo ============================================================
echo   ĐANG TẮT HỆ THỐNG EVI DASHBOARD...
echo ============================================================
echo.

:: Tìm và ngắt tiến trình Python đang chạy app.py
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance"

echo.
echo ============================================================
echo   ĐÃ TẮT HOÀN TOÀN SERVER BACKEND VÀ FRONTEND!
echo ============================================================
ping 127.0.0.1 -n 4 >nul
"""

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

start_web_path = os.path.join(base_dir, "start_web.bat")
stop_web_path = os.path.join(base_dir, "stop_web.bat")

with open(start_web_path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(start_web_content)

with open(stop_web_path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(stop_web_content)

print("Successfully updated start_web.bat and stop_web.bat with CRLF line endings.")
