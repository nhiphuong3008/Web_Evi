@echo off
title [EVI] Dung Toan Bo Server va Tunnel
color 0C

echo ===============================================================================
echo                DUNG HE THONG EVI DASHBOARD SERVER
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Dang tat Flask Backend (app.py)...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance" >nul 2>&1

echo [2/3] Dang tat Cloudflare va Ngrok Tunnel...
taskkill /f /im cloudflared.exe >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1

echo [3/3] Dang tat cac tien trinh phu tro...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''node.exe'' AND CommandLine LIKE ''%%localtunnel%%''' | Remove-CimInstance" >nul 2>&1

echo.
echo ===============================================================================
echo   DA TAT HOAN TOAN SERVER VA CAC DUONG LINK TRUY CAP!
echo ===============================================================================
echo.
timeout /t 3 /nobreak >nul
exit /b 0
