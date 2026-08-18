@echo off
chcp 65001 >nul
title EVI Dashboard - Mo Tuong Lua Port 5001 Cho Mang Wi-Fi
echo ============================================================
echo   MỞ TƯỜNG LỬA (FIREWALL) PORT 5001 CHO CÁC MÁY CÙNG WI-FI
echo ============================================================
echo.
echo [1/2] Dang mo cong 5001 trong Windows Firewall (Private + Public + Domain)...

powershell -Command "netsh advfirewall firewall delete rule name='EVI Dashboard 5001' > $null 2>&1"
powershell -Command "netsh advfirewall firewall add rule name='EVI Dashboard 5001' dir=in action=allow protocol=TCP localport=5001 profile=any"

echo [2/2] Dang chuyen mang Wi-Fi sang che do Private...
powershell -Command "Set-NetConnectionProfile -InterfaceAlias 'Wi-Fi' -NetworkCategory Private -ErrorAction SilentlyContinue"

echo.
echo ============================================================
echo   THANH CONG! CAC MAY TINH VAP DIEN THOAI CUNG MANG WI-FI
echo   GIO DAY CO THE TRUY CAP TRUC TIEP VAP DIA CHI:
echo.
echo   http://192.168.1.38:5001
echo.
echo   (Neu Wi-Fi trung tam bat che do "AP Isolation" khong vao bang IP duoc,
echo    hay mo file "start_tunnel.bat" de lay link online chia se cho moi nguoi!)
echo ============================================================
echo.
pause
