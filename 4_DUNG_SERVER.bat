@echo off
chcp 65001 >nul
title [EVI] Dừng Toàn Bộ Server & Tunnel
color 0C

echo ===============================================================================
echo                🛑 DỪNG HỆ THỐNG EVI DASHBOARD SERVER
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [1/2] Đang tắt Flask Backend (app.py)...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance" >nul 2>&1

echo [2/3] Đang tắt Cloudflare Tunnel (cloudflared.exe)...
taskkill /f /im cloudflared.exe >nul 2>&1

echo [3/3] Đang tắt Localtunnel...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''node.exe'' AND CommandLine LIKE ''%%localtunnel%%''' | Remove-CimInstance" >nul 2>&1

echo.
echo ===============================================================================
echo   ✅ ĐÃ TẮT HOÀN TOÀN SERVER VÀ CÁC ĐƯỜNG LINK TRUY CẬP!
echo ===============================================================================
echo.
timeout /t 3 /nobreak >nul
exit /b 0
