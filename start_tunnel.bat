@echo off
chcp 65001 >nul
title EVI Dashboard - Online Tunnel Link Launcher
echo ============================================================
echo   TẠO ĐƯỜNG LINK ONLINE CHO NHÂN VIÊN CM TỪ XA / MÁY KHÁC
echo ============================================================
echo.

cmd /c "npx -y localtunnel --port 5001"

pause
