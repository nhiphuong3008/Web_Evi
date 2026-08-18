@echo off
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
