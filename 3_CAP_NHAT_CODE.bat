@echo off
title [EVI] Cap Nhat Code Moi Tu GitHub
color 0E

echo ===============================================================================
echo            CAP NHAT CODE MOI NHAT CHO EVI DASHBOARD (GIT PULL)
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Dang keo cap nhat moi nhat tu GitHub Repository...
git fetch origin main
git reset --hard origin/main

echo.
echo [2/3] Kiem tra va cap nhat cac thu vien moi neu co...
if exist "venv\Scripts\pip.exe" (
    venv\Scripts\pip.exe install -r requirements.txt --quiet
    echo     -> Da dong bo thu vien thanh cong.
) else (
    pip install -r requirements.txt --quiet
)

echo.
echo [3/3] Hoan tat cap nhat phien ban moi nhat!
echo.
echo ===============================================================================
echo   CODE DA DUOC CAP NHAT THANH CONG VE MAY SERVER!
echo ===============================================================================
echo.

set /p RESTART="Ban co muon khoi dong lai Server ngay khong? (Y/N, mac dinh Y): "
if /i "%RESTART%"=="N" (
    echo Tam biet!
    pause
    exit /b 0
)

call "2_CHAY_SERVER_VA_LINK_ONLINE.bat"
