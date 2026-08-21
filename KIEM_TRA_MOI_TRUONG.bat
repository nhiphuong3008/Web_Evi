@echo off
title [EVI] KIEM TRA TOAN DIEN HE THONG & MOI TRUONG SERVER
color 0E

echo ===============================================================================
echo            🔍 BANG KIEM TRA TOAN DIEN HE THONG & MOI TRUONG EVI
echo ===============================================================================
echo.

cd /d "%~dp0"

set "ERRORS=0"

:: -------------------------------------------------------------------------------
:: 1. KIỂM TRA PYTHON HỆ THỐNG
:: -------------------------------------------------------------------------------
echo [1/6] Kiem tra Python he thong...
set "SYS_PY="
py -3 -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "SYS_PY=py -3"
) else (
    python -c "import sys; exit(0)" >nul 2>&1
    if %ERRORLEVEL% EQU 0 set "SYS_PY=python"
)

if defined SYS_PY (
    for /f "tokens=*" %%V in ('%SYS_PY% --version 2^>^&1') do echo         [OK] Python he thong: %%V
) else (
    echo         [FAIL] CHUA CAI PYTHON HE THONG!
    set /a ERRORS+=1
)

:: -------------------------------------------------------------------------------
:: 2. KIỂM TRA MÔI TRƯỜNG ẢO VENV
:: -------------------------------------------------------------------------------
echo.
echo [2/6] Kiem tra moi truong ao (venv)...
if exist "venv\Scripts\python.exe" (
    for /f "tokens=*" %%V in ('venv\Scripts\python.exe --version 2^>^&1') do echo         [OK] venv Python: %%V
) else (
    echo         [FAIL] CHUA CO THU MUC venv\Scripts\python.exe!
    set /a ERRORS+=1
)

:: -------------------------------------------------------------------------------
:: 3. KIỂM TRA CÁC THƯ VIỆN BẮT BUỘC
:: -------------------------------------------------------------------------------
echo.
echo [3/6] Kiem tra cac goi thu vien cot loi...
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe -c "import flask, sqlalchemy, openpyxl, dotenv, requests; print('OK')" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo         [OK] Tat ca thu vien (Flask, SQLAlchemy, openpyxl, requests...) da day du.
    ) else (
        echo         [FAIL] THIEU THU VIEN! Can chay pip install -r requirements.txt.
        set /a ERRORS+=1
    )
) else (
    echo         [SKIP] Khong the kiem tra thu vien vi chua co venv.
    set /a ERRORS+=1
)

:: -------------------------------------------------------------------------------
:: 4. KIỂM TRA CƠ SỞ DỮ LIỆU SQLITE
:: -------------------------------------------------------------------------------
echo.
echo [4/6] Kiem tra Co So Du Lieu (database\evi_center.db)...
if exist "database\evi_center.db" (
    for %%F in ("database\evi_center.db") do echo         [OK] File CSDL ton tai (Dung luong: %%~zF bytes)
    if exist "venv\Scripts\python.exe" (
        venv\Scripts\python.exe -c "import sqlite3; c=sqlite3.connect('database/evi_center.db'); cur=c.cursor(); s=cur.execute('SELECT COUNT(*) FROM students').fetchone()[0]; cl=cur.execute('SELECT COUNT(*) FROM class_schedules').fetchone()[0]; print(f'        [OK] Du lieu: {s} hoc sinh, {cl} lop hoc trong CSDL.'); c.close()"
    )
) else (
    echo         [FAIL] KHONG TIM THAY FILE database\evi_center.db!
    set /a ERRORS+=1
)

:: -------------------------------------------------------------------------------
:: 5. KIỂM TRA CÔNG CỤ TUNNEL (NGROK & CLOUDFLARED)
:: -------------------------------------------------------------------------------
echo.
echo [5/6] Kiem tra cong cu Online Tunnel...
if exist "ngrok.exe" (
    echo         [OK] ngrok.exe da san sang.
) else (
    echo         [CANH BAO] Chua co ngrok.exe (se tu tai khi chay).
)

if exist "cloudflared.exe" (
    echo         [OK] cloudflared.exe da san sang.
) else (
    echo         [CANH BAO] Chua co cloudflared.exe.
)

:: -------------------------------------------------------------------------------
:: 6. KIỂM TRA TRẠNG THÁI SERVER BACKEND (PORT 5001)
:: -------------------------------------------------------------------------------
echo.
echo [6/6] Kiem tra trang thai Flask Backend (Port 5001)...
powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('127.0.0.1', 5001); $client.Close(); Write-Host '        [OK] Backend Server DANG CHAY tren cong 5001!' -ForegroundColor Green } catch { Write-Host '        [OFFLINE] Backend Server chua chay.' -ForegroundColor Yellow }"

echo.
echo ===============================================================================
if %ERRORS% EQU 0 (
    color 0A
    echo   🎉 KET QUA: MOI TRUONG SERVER HOAN TOAN DAY DU VA SAN SANG!
    echo ===============================================================================
    echo.
    echo   Ban co the khoi chay Server ngay bang file: [2_CHAY_SERVER_VA_LINK_ONLINE.bat]
) else (
    color 0C
    echo   ⚠️ KET QUA: PHAT HIEN %ERRORS% MUC CHUA DAT YEU CAU!
    echo ===============================================================================
    echo.
    echo   [GIAI PHAP KHAC PHUC TU DONG]:
    echo   Chay file [CAI_DAT_VA_CHAY_TAT_CA.bat] de may tu dong sua toan bo loi tren!
)
echo.

set /p ACTION="Ban co muon chay file CAI_DAT_VA_CHAY_TAT_CA.bat ngay bay gio khong? (Y/N, mac dinh Y): "
if /i "%ACTION%"=="N" (
    echo Tam biet!
    pause
    exit /b 0
)

call "%~dp0CAI_DAT_VA_CHAY_TAT_CA.bat"
