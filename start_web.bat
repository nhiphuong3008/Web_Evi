@echo off
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
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

start "EVI Dashboard Server" /min "%PY_CMD%" app.py

echo [3/3] Đang chờ Server khởi tạo và kết nối Google Sheets...
set "COUNT=0"
:WAIT_LOOP
ping 127.0.0.1 -n 2 >nul
powershell -Command "try { (New-Object System.Net.Sockets.TcpClient).Connect('127.0.0.1', 5001); exit 0 } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto SERVER_READY
set /a COUNT+=1
if %COUNT% GEQ 25 goto TIMEOUT_ERR
echo       Đang chờ backend sẵn sàng... (%COUNT%s)
goto WAIT_LOOP

:SERVER_READY
echo.
echo ============================================================
echo   🎉 ĐÃ BẬT THÀNH CÔNG EVI DASHBOARD!
echo.
echo   1. Máy này dùng:            http://127.0.0.1:5001
echo   2. Các máy cùng Wi-Fi dùng: http://192.168.1.38:5001
echo.
echo   (Nếu máy khác chưa vào được: Chuột phải file "Mo_Tuong_Lua_Firewall.bat" -> Run as Administrator)
echo ============================================================
start http://127.0.0.1:5001
ping 127.0.0.1 -n 4 >nul
exit /b 0

:TIMEOUT_ERR
echo.
echo ============================================================
echo   [CẢNH BÁO] Server mất nhiều thời gian hơn dự kiến (25s).
echo   Đang tự động mở trình duyệt...
echo ============================================================
start http://127.0.0.1:5001
ping 127.0.0.1 -n 5 >nul
exit /b 1
