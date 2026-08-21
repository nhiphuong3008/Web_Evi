@echo off
title [EVI] KHOI CHAY NGROK ONLINE TUNNEL 24/7
color 0B

echo ===============================================================================
echo            KHOI CHAY NGROK ONLINE TUNNEL CO DINH 24/7
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Kiem tra va tai ngrok.exe neu chua co
if not exist "ngrok.exe" (
    echo [1/3] Chua co ngrok.exe. Dang tu dong tai ngrok ban moi nhat...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 'ngrok.zip'); Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force; Remove-Item 'ngrok.zip' -ErrorAction SilentlyContinue"
    echo     -> Da tai xong ngrok.exe!
) else (
    echo [1/3] ngrok.exe da co san trong thu muc.
)

:: 2. Unblock file va them authtoken ban quyen
echo [2/3] Cau hinh Authtoken ban quyen...
powershell -Command "Unblock-File ngrok.exe -ErrorAction SilentlyContinue" >nul 2>&1
"%~dp0ngrok.exe" config add-authtoken 3IBiTbkXguuBIBqAroSuk5Y3ugF_6yudsrKPch9sr97rURSqk

:: 3. Khoi chay Tunnel ket noi voi Port 5001
echo [3/3] Dang mo Tunnel ket noi voi domain: hardy-porthole-wildland.ngrok-free.dev...
echo.
echo ===============================================================================
echo   DUONG LINK ONLINE NGROK CO DINH:
echo   👉 https://hardy-porthole-wildland.ngrok-free.dev
echo ===============================================================================
echo.
echo [Luu y]: Giu cua so nay mo de link Online luon hoat dong 24/7.
echo.

"%~dp0ngrok.exe" http 5001 --domain=hardy-porthole-wildland.ngrok-free.dev

pause
