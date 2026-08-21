@echo off
chcp 65001 >nul
title [EVI] Dang Chay Server & Mo Duong Link Online 24/7
color 0A

echo ===============================================================================
echo                🌟 KHOI CHAY EVI DASHBOARD SERVER 24/7
echo ===============================================================================
echo.

cd /d "%~dp0"

:: -------------------------------------------------------------------------------
:: 1. KIEM TRA MOI TRUONG PYTHON VENV (TU DONG CAI DAT NEU CHUA CO)
:: -------------------------------------------------------------------------------
if not exist "venv\Scripts\python.exe" (
    echo [THONG BAO] Chua tim thay moi truong Python venv!
    echo            Dang tu dong goi [1_CAI_DAT_SERVER_TU_DONG.bat] de thiet lap tu A-Z...
    echo.
    call "%~dp01_CAI_DAT_SERVER_TU_DONG.bat"
    echo.
)

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
echo [1/4] Dang don dep cac tien trinh cu (neu co)...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance" >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1

:: -------------------------------------------------------------------------------
:: 3. KHOI DONG FLASK BACKEND
:: -------------------------------------------------------------------------------
echo [2/4] Dang khoi chay Flask Backend Server (Port 5001)...
start "EVI Backend Server" /min "%PY_CMD%" app.py

:: Doi backend san sang
set "COUNT=0"
:WAIT_SERVER
ping 127.0.0.1 -n 2 >nul
powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('127.0.0.1', 5001); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto SERVER_READY
set /a COUNT+=1
if %COUNT% GEQ 20 (
    echo [CANH BAO] Backend khoi dong lau hon du kien, dang tiep tuc mo Tunnel...
    goto SERVER_READY
)
echo       -> Dang cho Backend phan hoi... (%COUNT%s)
goto WAIT_SERVER

:SERVER_READY
echo     -> Flask Backend da san sang tren cong 5001!
echo.

:: -------------------------------------------------------------------------------
:: 4. KHOI TAO DUONG LINK ONLINE CO DINH (NGROK & CLOUDFLARE)
:: -------------------------------------------------------------------------------
echo [3/4] Dang ket noi duong link Online co dinh (hardy-porthole-wildland.ngrok-free.dev)...

:: Dam bao ngrok.exe ton tai va duoc Unblock
if not exist "ngrok.exe" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 'ngrok.zip'); Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force; Remove-Item 'ngrok.zip' -ErrorAction SilentlyContinue"
)

if exist "ngrok.exe" (
    powershell -Command "Unblock-File ngrok.exe -ErrorAction SilentlyContinue" >nul 2>&1
    "%~dp0ngrok.exe" config add-authtoken 3IBiTbkXguuBIBqAroSuk5Y3ugF_6yudsrKPch9sr97rURSqk >nul 2>&1
    start "EVI Ngrok Online Tunnel" "%~dp0ngrok.exe" http 5001 --domain=hardy-porthole-wildland.ngrok-free.dev
    echo     -> Da khoi dong Ngrok Tunnel co dinh!
)

:: Bat them Cloudflare Tunnel du phong song song
set "CF_LOG=%TEMP%\cloudflared_evi.log"
if exist "%CF_LOG%" del /f /q "%CF_LOG%" >nul 2>&1
set "CF_URL="

if exist "cloudflared.exe" (
    powershell -Command "Unblock-File cloudflared.exe -ErrorAction SilentlyContinue" >nul 2>&1
    start "EVI Cloudflare Tunnel" /min "%~dp0cloudflared.exe" tunnel --url http://127.0.0.1:5001 --logfile "%CF_LOG%"
    ping 127.0.0.1 -n 3 >nul
    if exist "%CF_LOG%" (
        for /f "usebackq tokens=*" %%L in (`powershell -NoProfile -Command "(Get-Content -Path '%CF_LOG%' -ErrorAction SilentlyContinue | Select-String 'https://[a-zA-Z0-9-]+\.trycloudflare\.com').Matches.Value | Select-Object -First 1"`) do (
            set "CF_URL=%%L"
        )
    )
)

:: -------------------------------------------------------------------------------
:: 5. TIM DIA CHI IP MANG NOI BO (LAN)
:: -------------------------------------------------------------------------------
set "LAN_IP=127.0.0.1"
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi*','Ethernet*','vEthernet*' | Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -notlike '127.*' } | Select-Object -First 1).IPAddress"`) do (
    set "LAN_IP=%%I"
)

echo.
echo ===============================================================================
echo   🎉 HE THONG EVI DASHBOARD DA SAN SANG HOAT DONG 24/7!
echo ===============================================================================
echo.
echo   🌐 1. DUONG LINK ONLINE CO DINH VINH VIEN (TRUY CAP TU XA MOI NOI 24/7):
echo      👉 https://hardy-porthole-wildland.ngrok-free.dev
echo.
echo      (Link nay co dinh tron doi, khong bao gio thay doi du tat mo Server!)
echo.
if defined CF_URL (
    echo   🛡️ 2. DUONG LINK ONLINE DU PHONG (CLOUDFLARE):
    echo      👉 %CF_URL%
    echo.
)
echo   📶 3. TRUY CAP CUNG MANG WI-FI / MANG NOI BO (LAN):
echo      👉 http://%LAN_IP%:5001
echo.
echo   💻 4. TRUY CAP TRUC TIEP TREN MAY SERVER NAY:
echo      👉 http://127.0.0.1:5001
echo.
echo ===============================================================================
echo   [LUU Y QUAN TRONG]:
echo   • Giu 2 cua so nay mo de Server va Link Online tiep tuc hoat dong.
echo   • Khi muon dung he thong, chay file [4_DUNG_SERVER.bat] hoac dong cua so nay.
echo ===============================================================================
echo.

:: Tu dong mo trinh duyet
start https://hardy-porthole-wildland.ngrok-free.dev

echo Nhan phim bat ky hoac thu nho cua so nay de Server chay ngam...
pause >nul
