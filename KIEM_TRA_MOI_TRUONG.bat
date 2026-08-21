@echo off
title [EVI] KIEM TRA HE THONG VA MOI TRUONG SERVER
color 0E

echo ===============================================================================
echo            KIEM TRA TOAN DIEN HE THONG VA MOI TRUONG EVI
echo ===============================================================================
echo.

cd /d "%~dp0"

set "ERR_COUNT=0"

:: -------------------------------------------------------------------------------
:: 1. KIEM TRA PYTHON HE THONG
:: -------------------------------------------------------------------------------
echo [1/6] Kiem tra Python tren Windows...

set "SYS_PYTHON="
py -3 -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "SYS_PYTHON=py -3"
    goto SYS_PY_OK
)

python -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "SYS_PYTHON=python"
    goto SYS_PY_OK
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "SYS_PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto SYS_PY_OK
)

if exist "%ProgramFiles%\Python312\python.exe" (
    set "SYS_PYTHON=%ProgramFiles%\Python312\python.exe"
    goto SYS_PY_OK
)

echo         [FAIL] CHUA CAI PYTHON TRUOC DO!
set /a ERR_COUNT+=1
goto STEP_2

:SYS_PY_OK
echo         [OK] Da tim thay Python: %SYS_PYTHON%

:STEP_2
:: -------------------------------------------------------------------------------
:: 2. KIEM TRA THU MUC VENV
:: -------------------------------------------------------------------------------
echo.
echo [2/6] Kiem tra thu muc moi truong ao venv...
if exist "venv\Scripts\python.exe" (
    echo         [OK] Thu muc venv da san sang.
    goto STEP_3
) else (
    echo         [FAIL] CHUA CO THU MUC venv\Scripts\python.exe!
    set /a ERR_COUNT+=1
    goto STEP_3
)

:STEP_3
:: -------------------------------------------------------------------------------
:: 3. KIEM TRA CAC THU VIEN REQUIREMENT
:: -------------------------------------------------------------------------------
echo.
echo [3/6] Kiem tra cac thu vien Flask va SQLAlchemy...
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe -c "import flask, sqlalchemy, openpyxl, dotenv, requests; exit(0)" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo         [OK] Cac goi thu vien Flask, SQLAlchemy, openpyxl da cai du.
    ) else (
        echo         [FAIL] THIEU THU VIEN! Can chay pip install -r requirements.txt.
        set /a ERR_COUNT+=1
    )
) else (
    echo         [FAIL] Chua co venv de kiem tra thu vien.
    set /a ERR_COUNT+=1
)

:: -------------------------------------------------------------------------------
:: 4. KIEM TRA CO SO DU LIEU SQLITE
:: -------------------------------------------------------------------------------
echo.
echo [4/6] Kiem tra file Co So Du Lieu SQLite...
if exist "database\evi_center.db" (
    echo         [OK] File database\evi_center.db da ton tai san sang.
) else (
    echo         [FAIL] KHONG TIM THAY FILE database\evi_center.db!
    set /a ERR_COUNT+=1
)

:: -------------------------------------------------------------------------------
:: 5. KIEM TRA CONG CU TUNNEL
:: -------------------------------------------------------------------------------
echo.
echo [5/6] Kiem tra cong cu Online Tunnel...
if exist "ngrok.exe" (
    echo         [OK] ngrok.exe da co san trong thu muc.
) else (
    echo         [CANH BAO] Chua co ngrok.exe.
)

if exist "cloudflared.exe" (
    echo         [OK] cloudflared.exe da co san.
) else (
    echo         [CANH BAO] Chua co cloudflared.exe.
)

:: -------------------------------------------------------------------------------
:: 6. KIEM TRA CONG 5001 FLASK BACKEND
:: -------------------------------------------------------------------------------
echo.
echo [6/6] Kiem tra trang thai Backend tren cong 5001...
powershell -Command "try { $c = New-Object System.Net.Sockets.TcpClient; $c.Connect('127.0.0.1', 5001); $c.Close(); Write-Host '        [OK] Backend Server DANG CHAY tren cong 5001!' -ForegroundColor Green } catch { Write-Host '        [OFFLINE] Backend Server chua chay (se bat khi khoi dong).' -ForegroundColor Yellow }"

echo.
echo ===============================================================================
if %ERR_COUNT% EQU 0 (
    color 0A
    echo   [KET QUA]: MOI TRUONG SERVER HOAN TOAN DAY DU VA SAN SANG 100%%!
    echo ===============================================================================
    echo.
    echo   Ban co the bat Server ngay bang file: [2_CHAY_SERVER_VA_LINK_ONLINE.bat]
) else (
    color 0C
    echo   [KET QUA]: PHAT HIEN %ERR_COUNT% MUC CHUA HOAN TAT!
    echo ===============================================================================
    echo.
    echo   [HUONG DAN KHAC PHUC]:
    echo   Ban chi can nhap dup file [CAI_DAT_VA_CHAY_TAT_CA.bat] de may tu dong cai toan bo!
)
echo.
echo ===============================================================================
echo Nhấn phím bất kỳ để đóng cửa sổ này...
pause >nul
