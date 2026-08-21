@echo off
title [EVI] CAI DAT & KHOI CHAY SERVER TU DONG 100%%
color 0A

echo ===============================================================================
echo        🚀 TU DONG CAI DAT & KHOI CHAY EVI DASHBOARD SERVER 24/7
echo ===============================================================================
echo.
echo   Script nay se tu dong lam tat ca moi viec:
echo     1. Tai va cai dat Python 3.12 chinh thuc
echo     2. Tao moi truong ao venv va cai toan bo thu vien
echo     3. Tai va kich hoat Ngrok Tunnel co dinh (hardy-porthole-wildland)
echo     4. Khoi chay Flask Backend Server tren cong 5001
echo.
echo ===============================================================================
echo.

cd /d "%~dp0"

:: -------------------------------------------------------------------------------
:: BƯỚC 1: KIỂM TRA & TỰ ĐỘNG CÀI PYTHON 3.12
:: -------------------------------------------------------------------------------
echo [1/4] Kiem tra moi truong Python tren may tinh...

set "PY_EXE="

if exist "venv\Scripts\python.exe" (
    set "PY_EXE=venv\Scripts\python.exe"
    goto PYTHON_READY
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto PYTHON_READY
)

if exist "%ProgramFiles%\Python312\python.exe" (
    set "PY_EXE=%ProgramFiles%\Python312\python.exe"
    goto PYTHON_READY
)

py -3 -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_EXE=py -3"
    goto PYTHON_READY
)

python -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_EXE=python"
    goto PYTHON_READY
)

:: Nếu chưa có Python -> Tự động tải và cài đặt
echo.
echo [!] May chua co Python. Dang tu dong tai Python 3.12 chinh thuc tu python.org...
set "INSTALLER=%TEMP%\python-3.12.8-amd64.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe', $env:TEMP + '\python-3.12.8-amd64.exe')"

if not exist "%INSTALLER%" (
    echo [LOI] Khong the tai Python installer! Vui long kiem tra ket noi Internet.
    pause
    exit /b 1
)

echo.
echo [!] Dang tien hanh cai dat Python 3.12 (vui long cho khoang 30-45 giay)...
start /wait "" "%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 SimpleInstall=1

:: Chờ file python.exe xuất hiện
set "WAIT_COUNT=0"
:WAIT_PY_LOOP
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto PYTHON_READY
)
if exist "%ProgramFiles%\Python312\python.exe" (
    set "PY_EXE=%ProgramFiles%\Python312\python.exe"
    goto PYTHON_READY
)
ping 127.0.0.1 -n 3 >nul
set /a WAIT_COUNT+=2
if %WAIT_COUNT% LEQ 40 goto WAIT_PY_LOOP

set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"
set "PY_EXE=python"

:PYTHON_READY
echo     -> Da co Python hop le!
echo.

:: -------------------------------------------------------------------------------
:: BƯỚC 2: TẠO VENV & CÀI ĐẶT THƯ VIỆN
:: -------------------------------------------------------------------------------
echo [2/4] Thiet lap moi truong ao venv va cai dat thu vien...

if not exist "venv\Scripts\python.exe" (
    echo     -> Dang tao moi truong ao venv...
    %PY_EXE% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [LOI] Khong the tao venv. Thu lai bang python he thong...
        python -m venv venv
    )
)

if exist "venv\Scripts\pip.exe" (
    echo     -> Dang cai dat cac thu vien Flask, SQLAlchemy, openpyxl tu requirements.txt...
    "venv\Scripts\pip.exe" install -r requirements.txt --quiet
    echo     -> Cai dat thu vien hoan tat thanh cong!
)

echo.

:: -------------------------------------------------------------------------------
:: BƯỚC 3: TẢI VÀ THIẾT LẬP NGROK & CLOUDFLARE TUNNEL
:: -------------------------------------------------------------------------------
echo [3/4] Thiet lap cong cu Online Link 24/7...

if not exist "ngrok.exe" (
    echo     -> Dang tai ngrok.exe...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 'ngrok.zip'); Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force; Remove-Item 'ngrok.zip' -ErrorAction SilentlyContinue"
)

if exist "ngrok.exe" (
    powershell -Command "Unblock-File ngrok.exe -ErrorAction SilentlyContinue" >nul 2>&1
    "%~dp0ngrok.exe" config add-authtoken 3IBiTbkXguuBIBqAroSuk5Y3ugF_6yudsrKPch9sr97rURSqk >nul 2>&1
    echo     -> Da cau hinh Ngrok Token ban quyen thanh cong!
)

if not exist "cloudflared.exe" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object System.Net.WebClient).DownloadFile('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe', 'cloudflared.exe') } catch {}" >nul 2>&1
)

:: Mở cổng Firewall 5001
netsh advfirewall firewall add rule name="EVI_Dashboard_Port_5001" dir=in action=allow protocol=TCP localport=5001 >nul 2>&1

echo.

:: -------------------------------------------------------------------------------
:: BƯỚC 4: KHỞI CHẠY SERVER & MỞ LINK ONLINE
:: -------------------------------------------------------------------------------
echo [4/4] Dang khoi chay Server Backend va Duong link Online...

:: Tắt các tiến trình cũ nếu có
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance" >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1

set "FINAL_PY=venv\Scripts\python.exe"
if not exist "%FINAL_PY%" set "FINAL_PY=%PY_EXE%"

start "EVI Backend Server" /min "%FINAL_PY%" app.py

:: Đợi backend sẵn sàng
ping 127.0.0.1 -n 3 >nul

:: Bật Ngrok trong cửa sổ riêng
if exist "ngrok.exe" (
    start "EVI Ngrok Online Tunnel" "%~dp0ngrok.exe" http 5001 --domain=hardy-porthole-wildland.ngrok-free.dev
)

:: Bật Cloudflare dự phòng
if exist "cloudflared.exe" (
    powershell -Command "Unblock-File cloudflared.exe -ErrorAction SilentlyContinue" >nul 2>&1
    start "EVI Cloudflare Tunnel" /min "%~dp0cloudflared.exe" tunnel --url http://127.0.0.1:5001
)

:: Lấy IP mạng LAN
set "LAN_IP=127.0.0.1"
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi*','Ethernet*','vEthernet*' | Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -notlike '127.*' } | Select-Object -First 1).IPAddress"`) do (
    set "LAN_IP=%%I"
)

echo.
echo ===============================================================================
echo   🎉 HE THONG EVI DASHBOARD DA SAN SANG HOAT DONG 24/7!
echo ===============================================================================
echo.
echo   🌐 1. DUONG LINK ONLINE CO DINH CHINH THUC (TRUY CAP TU XA MOI NOI 24/7):
echo      👉 https://hardy-porthole-wildland.ngrok-free.dev
echo.
echo   📶 2. TRUY CAP CUNG MANG WI-FI / MANG NOI BO (LAN):
echo      👉 http://%LAN_IP%:5001
echo.
echo   💻 3. TRUY CAP TRUC TIEP TREN MAY SERVER NAY:
echo      👉 http://127.0.0.1:5001
echo.
echo ===============================================================================
echo   [LUU Y QUAN TRONG]:
echo   • Giu 2 cua so dang mo de Server tiep tuc chay 24/7.
echo   • Khi muon dung Server, chay file [4_DUNG_SERVER.bat].
echo ===============================================================================
echo.

:: Tự động mở trình duyệt
start https://hardy-porthole-wildland.ngrok-free.dev

echo Nhan phim bat ky de thu nho cua so nay...
pause >nul
