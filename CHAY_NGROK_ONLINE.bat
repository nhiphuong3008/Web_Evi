@echo off
title [EVI] KHOI CHAY NGROK ONLINE TUNNEL 24/7
color 0B

echo ===============================================================================
echo            KHOI CHAY NGROK ONLINE TUNNEL CO DINH 24/7
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Ngoai le Windows Defender de khong bi chan ngrok
echo [1/3] Cau hinh an toan Windows Defender cho thu muc...
powershell -Command "Add-MpPreference -ExclusionPath '%~dp0' -ErrorAction SilentlyContinue" >nul 2>&1
powershell -Command "Add-MpPreference -ExclusionPath 'D:\Vicare_web' -ErrorAction SilentlyContinue" >nul 2>&1
powershell -Command "Add-MpPreference -ExclusionPath 'C:\Vicare_web' -ErrorAction SilentlyContinue" >nul 2>&1

:: 2. Kiem tra va tai ngrok.exe
if not exist "ngrok.exe" (
    echo [2/3] Dang tai lai ngrok.exe...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 'ngrok.zip'); Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force; Remove-Item 'ngrok.zip' -ErrorAction SilentlyContinue"
)

powershell -Command "Unblock-File ngrok.exe -ErrorAction SilentlyContinue" >nul 2>&1

:: 3. Cau hinh authtoken va chay
echo [3/3] Dang mo Tunnel ket noi voi domain: hardy-porthole-wildland.ngrok-free.dev...
echo.
echo ===============================================================================
echo   DUONG LINK ONLINE NGROK CO DINH:
echo   👉 https://hardy-porthole-wildland.ngrok-free.dev
echo ===============================================================================
echo.
echo [Luu y]: Giu cua so nay mo de link Online luon hoat dong 24/7.
echo.

"%~dp0ngrok.exe" config add-authtoken 3IBiTbkXguuBIBqAroSuk5Y3ugF_6yudsrKPch9sr97rURSqk
"%~dp0ngrok.exe" http 5001 --domain=hardy-porthole-wildland.ngrok-free.dev

pause
