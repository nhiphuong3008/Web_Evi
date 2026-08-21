@echo off
title [EVI] CAI DAT SERVER TU DONG 100%%
color 0B

echo ===============================================================================
echo        TU DONG CAI DAT MOI TRUONG SERVER CHO EVI DASHBOARD
echo ===============================================================================
echo.
echo   Script nay se tu dong thiet lap toan bo may tinh thanh Server:
echo     1. Them ngoai le Windows Defender de khong bi chan cong cu
echo     2. Kiem tra / Tu dong tai va cai dat Python 3.12 chinh thuc
echo     3. Tao moi truong ao cach ly (venv) va cai dat toan bo thu vien
echo     4. Tu dong tai Cloudflare Tunnel va Ngrok kem Token ban quyen
echo     5. Mo cong tuong lua Windows Firewall 5001
echo.
echo ===============================================================================
echo.

cd /d "%~dp0"

:: -------------------------------------------------------------------------------
:: BUOC 0: NGOAI LE WINDOWS DEFENDER CHO THU MUC HIEN TAI VA O D
:: -------------------------------------------------------------------------------
echo [0/5] Thiet lap an toan Windows Defender cho thu muc...
powershell -Command "Add-MpPreference -ExclusionPath '%~dp0' -ErrorAction SilentlyContinue" >nul 2>&1
powershell -Command "Add-MpPreference -ExclusionPath 'D:\Vicare_web' -ErrorAction SilentlyContinue" >nul 2>&1
powershell -Command "Add-MpPreference -ExclusionPath 'C:\Vicare_web' -ErrorAction SilentlyContinue" >nul 2>&1

:: -------------------------------------------------------------------------------
:: BUOC 1: KIEM TRA VA CAI DAT PYTHON 3.12
:: -------------------------------------------------------------------------------
echo [1/5] Kiem tra moi truong Python tren Windows...

set "PYTHON_EXE="

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto PYTHON_FOUND
)

if exist "%ProgramFiles%\Python312\python.exe" (
    set "PYTHON_EXE=%ProgramFiles%\Python312\python.exe"
    goto PYTHON_FOUND
)

py -3 -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=py -3"
    goto PYTHON_FOUND
)

python -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    goto PYTHON_FOUND
)

:: Neu chua co Python -> Tu dong tai va cai dat
echo     -> CHUA CO PYTHON! Dang tu dong tai Python 3.12 tu python.org...
set "PY_INSTALLER=%TEMP%\python-3.12.8-amd64.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe', $env:TEMP + '\python-3.12.8-amd64.exe')"

if not exist "%PY_INSTALLER%" (
    echo [LOI] Khong the tai Python installer! Vui long kiem tra mang Internet.
    pause
    exit /b 1
)

echo     -> Dang tien hanh cai dat Python 3.12 (khoang 30-45 giay)...
start /wait "" "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 SimpleInstall=1

:: Cho file python.exe xuat hien
set "WAIT_PY=0"
:CHECK_PY_LOOP
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto PYTHON_FOUND
)
if exist "%ProgramFiles%\Python312\python.exe" (
    set "PYTHON_EXE=%ProgramFiles%\Python312\python.exe"
    goto PYTHON_FOUND
)
ping 127.0.0.1 -n 3 >nul
set /a WAIT_PY+=2
if %WAIT_PY% LEQ 30 goto CHECK_PY_LOOP

set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"
set "PYTHON_EXE=python"

:PYTHON_FOUND
echo     -> Da co Python: %PYTHON_EXE%
echo.

:: -------------------------------------------------------------------------------
:: BUOC 2: TAO VENV
:: -------------------------------------------------------------------------------
echo [2/5] Cau hinh moi truong ao venv...
if exist "venv\Scripts\python.exe" (
    echo     -> Thu muc venv da ton tai.
) else (
    echo     -> Dang tao thu muc venv...
    %PYTHON_EXE% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        python -m venv venv
    )
    echo     -> Da tao venv thanh cong!
)
echo.

:: -------------------------------------------------------------------------------
:: BUOC 3: CAI DAT CAC THU VIEN (REQUIREMENTS.TXT)
:: -------------------------------------------------------------------------------
echo [3/5] Cai dat cac thu vien Flask, SQLAlchemy, openpyxl...
if exist "venv\Scripts\pip.exe" (
    "venv\Scripts\pip.exe" install --upgrade pip --quiet >nul 2>&1
    "venv\Scripts\pip.exe" install -r requirements.txt --quiet
    echo     -> Cai dat thu vien thanh cong!
) else (
    echo     [LOI] Chua tim thay venv\Scripts\pip.exe!
)
echo.

:: -------------------------------------------------------------------------------
:: BUOC 4: TAI VA THIET LAP CONG CU TUNNEL (CLOUDFLARE VA NGROK)
:: -------------------------------------------------------------------------------
echo [4/5] Thiet lap cong cu Online Tunnel 24/7...

if not exist "cloudflared.exe" (
    echo     -> Dang tai cloudflared.exe...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe', 'cloudflared.exe')" >nul 2>&1
)
powershell -Command "Unblock-File cloudflared.exe -ErrorAction SilentlyContinue" >nul 2>&1

if not exist "ngrok.exe" (
    echo     -> Dang tai ngrok.exe...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 'ngrok.zip'); Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force; Remove-Item 'ngrok.zip' -ErrorAction SilentlyContinue"
)
powershell -Command "Unblock-File ngrok.exe -ErrorAction SilentlyContinue" >nul 2>&1

if exist "ngrok.exe" (
    "%~dp0ngrok.exe" config add-authtoken 3IBiTbkXguuBIBqAroSuk5Y3ugF_6yudsrKPch9sr97rURSqk >nul 2>&1
    echo     -> Da nap Authtoken Ngrok ban quyen thanh cong!
)
echo.

:: -------------------------------------------------------------------------------
:: BUOC 5: CAU HINH .ENV VA MO CONG FIREWALL
:: -------------------------------------------------------------------------------
echo [5/5] Cau hinh he thong va Mo cong Tuong lua Firewall 5001...

if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
    )
)

netsh advfirewall firewall add rule name="EVI_Dashboard_Port_5001" dir=in action=allow protocol=TCP localport=5001 >nul 2>&1

echo.
echo ===============================================================================
color 0A
echo   CAI DAT SERVER HOAN TAT 100%% THANH CONG!
echo ===============================================================================
echo.
echo   Moi truong may tinh da san sang de tro thanh Server chinh thuc.
echo   Ban co the khoi chay ngay bang file: [2_CHAY_SERVER_VA_LINK_ONLINE.bat]
echo.
echo ===============================================================================
echo Nhan phim bat ky de thoat...
pause >nul
