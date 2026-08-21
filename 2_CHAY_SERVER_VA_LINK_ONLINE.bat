@echo off
title [EVI] Dang Chay Server va Mo Duong Link Online 24/7
color 0A

echo ===============================================================================
echo                KHOI CHAY EVI DASHBOARD SERVER 24/7
echo ===============================================================================
echo.

cd /d "%~dp0"

:: -------------------------------------------------------------------------------
:: 1. KIEM TRA MOI TRUONG PYTHON VENV
:: -------------------------------------------------------------------------------
set "PY_CMD="
if exist "venv\Scripts\python.exe" (
    set "PY_CMD=venv\Scripts\python.exe"
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else (
        set "PY_CMD=python"
    )
)

:: -------------------------------------------------------------------------------
:: 2. TAT CAC TIEN TRINH CU
:: -------------------------------------------------------------------------------
echo [1/3] Dang don dep cac tien trinh cu neu co...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance" >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1

:: -------------------------------------------------------------------------------
:: 3. KHOI DONG FLASK BACKEND
:: -------------------------------------------------------------------------------
echo [2/3] Dang khoi chay Flask Backend Server Port 5001...
start "EVI Backend Server" /min "%PY_CMD%" app.py

:: Doi backend san sang
set "COUNT=0"
:WAIT_SERVER
ping 127.0.0.1 -n 2 >nul
powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('127.0.0.1', 5001); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto SERVER_READY
set /a COUNT+=1
if %COUNT% GEQ 15 goto SERVER_READY
goto WAIT_SERVER

:SERVER_READY
echo     -> Flask Backend da san sang tren cong 5001!
echo.

:: -------------------------------------------------------------------------------
:: 4. KHOI TAO DUONG LINK ONLINE CLOUDFLARE VA NGROK
:: -------------------------------------------------------------------------------
echo [3/3] Dang kich hoat duong link Online 24/7...

set "CF_LOG=%TEMP%\cloudflared_evi.log"
if exist "%CF_LOG%" del /f /q "%CF_LOG%" >nul 2>&1
set "PUBLIC_URL="

if exist "cloudflared.exe" (
    powershell -Command "Unblock-File cloudflared.exe -ErrorAction SilentlyContinue" >nul 2>&1
    start "EVI Cloudflare Tunnel" /min "%~dp0cloudflared.exe" tunnel --url http://127.0.0.1:5001 --logfile "%CF_LOG%"
    ping 127.0.0.1 -n 4 >nul
    if exist "%CF_LOG%" (
        for /f "usebackq tokens=*" %%L in (`powershell -NoProfile -Command "(Get-Content -Path '%CF_LOG%' -ErrorAction SilentlyContinue | Select-String 'https://[a-zA-Z0-9-]+\.trycloudflare\.com').Matches.Value | Select-Object -First 1"`) do (
            set "PUBLIC_URL=%%L"
        )
    )
)

:: Thu bat Ngrok neu co
if exist "ngrok.exe" (
    powershell -Command "Unblock-File ngrok.exe -ErrorAction SilentlyContinue" >nul 2>&1
    "%~dp0ngrok.exe" config add-authtoken 3IBiTbkXguuBIBqAroSuk5Y3ugF_6yudsrKPch9sr97rURSqk >nul 2>&1
    start "EVI Ngrok Online Tunnel" "%~dp0ngrok.exe" http 5001 --domain=hardy-porthole-wildland.ngrok-free.dev >nul 2>&1
)

:: Tim IP mang noi bo LAN
set "LAN_IP=127.0.0.1"
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi*','Ethernet*','vEthernet*' | Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -notlike '127.*' } | Select-Object -First 1).IPAddress"`) do (
    set "LAN_IP=%%I"
)

echo.
echo ===============================================================================
echo   HE THONG EVI DASHBOARD DA SAN SANG HOAT DONG 24/7!
echo ===============================================================================
echo.
if defined PUBLIC_URL (
    echo   [1] DUONG LINK ONLINE TOC DO CAO 24/7:
    echo       👉 %PUBLIC_URL%
    echo.
)
echo   [2] DUONG LINK NGROK CO DINH:
echo       👉 https://hardy-porthole-wildland.ngrok-free.dev
echo.
echo   [3] TRUY CAP CUNG MANG WI-FI LAN:
echo       👉 http://%LAN_IP%:5001
echo.
echo   [4] TRUY CAP TRUC TIEP TREN MAY SERVER NAY:
echo       👉 http://127.0.0.1:5001
echo.
echo ===============================================================================
echo   Luu y: Giu cua so nay mo de Server chay 24/7.
echo ===============================================================================
echo.

:: Tu dong mo trinh duyet
if defined PUBLIC_URL (
    start %PUBLIC_URL%
) else (
    start http://127.0.0.1:5001
)

echo Nhan phim bat ky de thu nho cua so nay...
pause >nul
