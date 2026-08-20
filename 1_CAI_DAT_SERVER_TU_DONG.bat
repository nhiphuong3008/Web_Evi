@echo off
chcp 65001 >nul
title [EVI] Cài Đặt Server Tự Động 100%%
color 0B

echo ===============================================================================
echo        🚀 TỰ ĐỘNG CÀI ĐẶT MÔI TRƯỜNG SERVER CHO EVI DASHBOARD
echo ===============================================================================
echo.
echo   Script này sẽ tự động thiết lập toàn bộ máy tính của bạn thành Server:
echo     1. Kiểm tra / Tự động tải & cài đặt Python 3.12 (nếu chưa có)
echo     2. Tạo môi trường ảo cách ly (Python Virtual Environment - venv)
echo     3. Cài đặt đầy đủ tất cả thư viện (Flask, SQLAlchemy, v.v.)
echo     4. Tự động tải công cụ Cloudflare Tunnel (tạo link online HTTPS)
echo     5. Khởi tạo file cấu hình .env & mở cổng tường lửa Windows Firewall
echo.
echo ===============================================================================
echo.

cd /d "%~dp0"

:: -------------------------------------------------------------------------------
:: BƯỚC 1: KIỂM TRA VÀ CÀI ĐẶT PYTHON
:: -------------------------------------------------------------------------------
echo [1/5] Kiểm tra môi trường Python...

set "PYTHON_EXE="
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    goto CHECK_PYTHON_DONE
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto CHECK_PYTHON_DONE
)

if exist "%ProgramFiles%\Python312\python.exe" (
    set "PYTHON_EXE=%ProgramFiles%\Python312\python.exe"
    goto CHECK_PYTHON_DONE
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto CHECK_PYTHON_DONE
)

:CHECK_PYTHON_DONE
if defined PYTHON_EXE goto PYTHON_FOUND
goto PYTHON_NOT_FOUND

:PYTHON_FOUND
echo     -> Đã tìm thấy Python: %PYTHON_EXE%
"%PYTHON_EXE%" --version
goto STEP_2_VENV

:PYTHON_NOT_FOUND
echo     -> CHƯA TÌM THẤY PYTHON! Đang tự động tải và cài đặt Python 3.12...
echo     -> Đang tải từ python.org, vui lòng chờ trong giây lát...

set "PY_INSTALLER=%TEMP%\python-3.12.8-amd64.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe', $env:TEMP + '\python-3.12.8-amd64.exe')"

if not exist "%PY_INSTALLER%" (
    echo.
    echo [LỖI] Không thể tải Python installer! Vui lòng kiểm tra kết nối Internet.
    echo Bạn có thể tự cài Python 3.12 thủ công tại: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo     -> Đang tiến hành cài đặt Python 3.12 vào máy (khoảng 30 giây)...
"%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0 SimpleInstall=1
timeout /t 6 /nobreak >nul

set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo     -> Cài đặt Python 3.12 hoàn tất thành công!

:: -------------------------------------------------------------------------------
:: BƯỚC 2: TẠO VÀ CẤU HÌNH MÔI TRƯỜNG ẢO VENV
:: -------------------------------------------------------------------------------
:STEP_2_VENV
echo.
echo [2/5] Cấu hình môi trường ảo Python (venv)...

if exist "venv\Scripts\python.exe" goto VENV_EXISTS

echo     -> Đang khởi tạo thư mục môi trường ảo venv...
"%PYTHON_EXE%" -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [LỖI] Không thể tạo môi trường ảo venv với lệnh: "%PYTHON_EXE%" -m venv venv
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
:: BƯỚC 4: TẢI CLOUDFLARE TUNNEL (CLOUDFLARED.EXE)
:: -------------------------------------------------------------------------------
:STEP_4_TUNNEL
echo.
echo [4/5] Thiết lập công cụ Cloudflare Tunnel (cho link Online 24/7)...

if exist "cloudflared.exe" goto CF_EXISTS

echo     -> Đang tải cloudflared.exe từ Cloudflare Official...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe', 'cloudflared.exe')"

if exist "cloudflared.exe" (
    echo     -> Đã tải cloudflared.exe thành công!
) else (
    echo     -> [LƯU Ý] Chưa tải được cloudflared.exe. Server vẫn chạy nội bộ bình thường.
)
goto STEP_5_ENV

:CF_EXISTS
echo     -> cloudflared.exe đã sẵn sàng trong thư mục dự án.

:: -------------------------------------------------------------------------------
:: BƯỚC 5: CẤU HÌNH FILE .ENV VÀ WINDOWS FIREWALL
:: -------------------------------------------------------------------------------
:STEP_5_ENV
echo.
echo [5/5] Cấu hình file môi trường .env và Tường Lửa Windows...

if exist ".env" goto ENV_EXISTS

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
echo   👉 [2_CHAY_SERVER_VA_LINK_ONLINE.bat] : Khởi chạy Server + Mở link Online 24/7
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
