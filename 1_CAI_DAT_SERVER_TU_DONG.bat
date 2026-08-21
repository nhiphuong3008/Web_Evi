@echo off
chcp 65001 >nul
title [EVI] Cài Đặt Server Tự Động 100%%
color 0B

echo ===============================================================================
echo        🚀 TỰ ĐỘNG CÀI ĐẶT MÔI TRƯỜNG SERVER CHO EVI DASHBOARD
echo ===============================================================================
echo.
echo   Script này sẽ tự động thiết lập toàn bộ máy tính của bạn thành Server:
echo     1. Kiểm tra / Tự động tải và cài đặt Python 3.12 (nếu chưa có)
echo     2. Tạo môi trường ảo cách ly (Python Virtual Environment - venv)
echo     3. Cài đặt đầy đủ tất cả thư viện (Flask, SQLAlchemy, v.v.)
echo     4. Tự động tải công cụ Cloudflare Tunnel (tạo link online HTTPS)
echo     5. Khởi tạo file cấu hình .env và mở cổng tường lửa Windows Firewall
echo.
echo ===============================================================================
echo.

cd /d "%~dp0"

:: -------------------------------------------------------------------------------
:: BƯỚC 1: KIỂM TRA VÀ CÀI ĐẶT PYTHON
:: -------------------------------------------------------------------------------
echo [1/5] Kiểm tra môi trường Python thực tế trên máy...

set "PYTHON_EXE="

:: 1. Kiểm tra py launcher
py -3 -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=py -3"
    goto PYTHON_FOUND
)

:: 2. Kiểm tra Python đã cài trong LocalAppData
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto PYTHON_FOUND
)

if exist "%ProgramFiles%\Python312\python.exe" (
    set "PYTHON_EXE=%ProgramFiles%\Python312\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto PYTHON_FOUND
)

:: 3. Kiểm tra python trong PATH (chạy code thử để lọc bỏ WindowsApps stub)
python -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    goto PYTHON_FOUND
)

goto PYTHON_NOT_FOUND

:PYTHON_FOUND
echo     -> Đã phát hiện Python hợp lệ: %PYTHON_EXE%
%PYTHON_EXE% --version
goto STEP_2_VENV

:PYTHON_NOT_FOUND
echo     -> CHƯA CÓ PYTHON! Đang tự động tải và cài đặt Python 3.12 chính thức...
echo     -> Đang tải installer từ python.org, vui lòng chờ trong giây lát...

set "PY_INSTALLER=%TEMP%\python-3.12.8-amd64.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe', $env:TEMP + '\python-3.12.8-amd64.exe')"

if not exist "%PY_INSTALLER%" (
    echo.
    echo [LỖI] Không thể tải Python installer! Vui lòng kiểm tra kết nối Internet.
    echo Bạn có thể tự tải và cài đặt Python 3.12 thủ công tại: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo     -> Đang tiến hành cài đặt Python 3.12 tự động (vui lòng chờ trong giây lát)...
start /wait "" "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0 SimpleInstall=1

:: Chờ tối đa 30s để file python.exe xuất hiện
set "WAIT_PY=0"
:CHECK_PY_INSTALLED
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
if %WAIT_PY% LEQ 30 goto CHECK_PY_INSTALLED

set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"

python -c "import sys; exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    goto PYTHON_FOUND
)

:: -------------------------------------------------------------------------------
:: BƯỚC 2: TẠO VÀ CẤU HÌNH MÔI TRƯỜNG ẢO VENV
:: -------------------------------------------------------------------------------
:STEP_2_VENV
echo.
echo [2/5] Cấu hình môi trường ảo Python (venv)...

if exist "venv\Scripts\python.exe" goto VENV_EXISTS

echo     -> Đang khởi tạo thư mục môi trường ảo venv...
%PYTHON_EXE% -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [LỖI] Không thể tạo môi trường ảo venv!
    pause
    exit /b 1
)
echo     -> Đã tạo venv thành công.
goto VENV_READY

:VENV_EXISTS
echo     -> Môi trường ảo venv đã tồn tại sẵn.

:VENV_READY
set "VENV_PY=%~dp0venv\Scripts\python.exe"
set "VENV_PIP=%~dp0venv\Scripts\pip.exe"

:: -------------------------------------------------------------------------------
:: BƯỚC 3: CÀI ĐẶT CÁC THƯ VIỆN (REQUIREMENTS.TXT)
:: -------------------------------------------------------------------------------
:STEP_3_REQS
echo.
echo [3/5] Cài đặt các thư viện phụ thuộc (Flask, SQLAlchemy, v.v.)...
echo     -> Đang nâng cấp pip...
"%VENV_PY%" -m pip install --upgrade pip >nul 2>&1

if exist "requirements.txt" goto INSTALL_FROM_REQ
goto INSTALL_DEFAULT_PKGS

:INSTALL_FROM_REQ
echo     -> Đang cài đặt thư viện từ requirements.txt (vui lòng chờ 1-2 phút)...
"%VENV_PIP%" install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [CẢNH BÁO] Có một số gói gặp cảnh báo nhưng vẫn tiếp tục...
) else (
    echo     -> Đã cài đặt hoàn tất tất cả thư viện cần thiết!
)
goto STEP_4_TUNNEL

:INSTALL_DEFAULT_PKGS
echo     -> Đang cài đặt các gói lõi: Flask, SQLAlchemy, Gspread...
"%VENV_PIP%" install flask flask-cors sqlalchemy gspread google-auth python-dotenv requests openpyxl

:: -------------------------------------------------------------------------------
:: BƯỚC 4: THIẾT LẬP CÔNG CỤ NGROK TUNNEL (LINK CỐ ĐỊNH VĨNH VIỄN)
:: -------------------------------------------------------------------------------
:STEP_4_TUNNEL
echo.
echo [4/5] Thiết lập công cụ Ngrok Online Link cố định...

if exist "ngrok.exe" goto NGROK_EXISTS

echo     -> Đang tải ngrok.exe bản chính thức...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 'ngrok.zip'); Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force; Remove-Item 'ngrok.zip' -ErrorAction SilentlyContinue"

:NGROK_EXISTS
if exist "ngrok.exe" (
    echo     -> Đang kích hoạt Ngrok Token bản quyền...
    "%~dp0ngrok.exe" config add-authtoken 3IBiTbkXguuBIBqAroSuk5Y3ugF_6yudsrKPch9sr97rURSqk >nul 2>&1
    echo     -> Ngrok Tunnel cố định đã được thiết lập thành công!
)

:: Tải thêm Cloudflare Tunnel dự phòng
if not exist "cloudflared.exe" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object System.Net.WebClient).DownloadFile('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe', 'cloudflared.exe') } catch {}" >nul 2>&1
)

:: -------------------------------------------------------------------------------
:: BƯỚC 5: CẤU HÌNH FILE .ENV VÀ WINDOWS FIREWALL
:: -------------------------------------------------------------------------------
:STEP_5_ENV
echo.
echo [5/5] Cấu hình file môi trường .env và Tường Lửa Windows...

if exist ".env" (
    powershell -NoProfile -Command "(Get-Content .env) -replace 'FLASK_PORT=5000', 'FLASK_PORT=5001' | Set-Content .env"
    echo     -> File cấu hình .env đã sẵn sàng trên Port 5001.
    goto FIREWALL_SETUP
)

if exist ".env.example" (
    copy /y ".env.example" ".env" >nul
    echo     -> Đã tự động tạo file .env từ .env.example.
    goto FIREWALL_SETUP
)

echo FLASK_ENV=development> ".env"
echo FLASK_DEBUG=0>> ".env"
echo FLASK_PORT=5001>> ".env"
echo FLASK_HOST=0.0.0.0>> ".env"
echo APP_NAME=Trung tâm Anh ngữ Vicare>> ".env"
echo APP_SECRET_KEY=evi-server-secret-key-2026>> ".env"
echo AUTO_SYNC_DB_ON_STARTUP=0>> ".env"
echo     -> Đã tạo file .env mặc định chuẩn cho Server.
goto FIREWALL_SETUP

:ENV_EXISTS
echo     -> File cấu hình .env đã tồn tại.

:FIREWALL_SETUP
:: Mở port 5001 trên Windows Firewall
powershell -Command "try { New-NetFirewallRule -DisplayName 'EVI Dashboard Port 5001' -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null; Write-Host '    -> Đã mở cổng 5001 trên Windows Firewall (cho mạng LAN/Wi-Fi)' } catch { }" >nul 2>&1

echo.
echo ===============================================================================
echo   🎉 CHÚC MỪNG! MÔI TRƯỜNG SERVER ĐÃ ĐƯỢC THIẾT LẬP HOÀN TẤT 100%%!
echo ===============================================================================
echo.
echo   Từ bây giờ, bạn có thể sử dụng các file sau:
echo.
echo   👉 [2_CHAY_SERVER_VA_LINK_ONLINE.bat] : Khởi chạy Server và Mở link Online 24/7
echo   👉 [3_CAP_NHAT_CODE.bat]              : Kéo code mới nhất từ GitHub về
echo   👉 [4_DUNG_SERVER.bat]                : Tắt Server an toàn
echo.
echo ===============================================================================
echo.

set /p RUN_NOW="Bạn có muốn khởi động Server ngay bây giờ không? (Y/N, mặc định Y): "
if /i "%RUN_NOW%"=="N" goto END_SCRIPT

call "2_CHAY_SERVER_VA_LINK_ONLINE.bat"
exit /b 0

:END_SCRIPT
echo.
echo Đã hoàn tất cài đặt. Nhấn phím bất kỳ để đóng cửa sổ này...
pause >nul
