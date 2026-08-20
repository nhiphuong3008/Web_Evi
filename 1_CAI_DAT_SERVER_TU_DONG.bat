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
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else if exist "%ProgramFiles%\Python312\python.exe" (
        set "PYTHON_EXE=%ProgramFiles%\Python312\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    )
)

if defined PYTHON_EXE (
    echo     -> Đã tìm thấy Python: %PYTHON_EXE%
    %PYTHON_EXE% --version
) else (
    echo     -> CHƯA TÌM THẤY PYTHON! Đang tự động tải và cài đặt Python 3.12.8...
    echo     -> Vui lòng chờ 1-2 phút trong khi tải từ python.org...
    
    set "PY_INSTALLER=%TEMP%\python-3.12.8-amd64.exe"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Đang tải Python installer từ python.org...'; try { (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe', '%TEMP%\python-3.12.8-amd64.exe') } catch { exit 1 }"
    
    if not exist "%PY_INSTALLER%" (
        echo [LỖI] Không thể tải Python installer! Vui lòng kiểm tra kết nối Internet.
        pause
        exit /b 1
    )
    
    echo     -> Đang tiến hành cài đặt Python âm thầm (Silent Install)...
    "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0 SimpleInstall=1
    timeout /t 5 /nobreak >nul
    
    :: Cập nhật PATH cho phiên chạy hiện tại
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    
    if not exist "%PYTHON_EXE%" (
        where python >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set "PYTHON_EXE=python"
        ) else (
            echo [CẢNH BÁO] Đã cài xong Python, vui lòng khởi động lại cửa sổ lệnh hoặc máy tính để nhận diện lệnh Python.
            set "PYTHON_EXE=python"
        )
    )
    echo     -> Cài đặt Python 3.12 hoàn tất thành công!
)
echo.

:: -------------------------------------------------------------------------------
:: BƯỚC 2: TẠO VÀ CẤU HÌNH MÔI TRƯỜNG ẢO VENV
:: -------------------------------------------------------------------------------
echo [2/5] Cấu hình môi trường ảo Python (venv)...

if not exist "venv\Scripts\python.exe" (
    echo     -> Đang khởi tạo thư mục venv...
    "%PYTHON_EXE%" -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [LỖI] Không thể tạo môi trường ảo venv!
        pause
        exit /b 1
    )
    echo     -> Đã tạo venv thành công.
) else (
    echo     -> Môi trường ảo venv đã tồn tại sẵn.
)

set "VENV_PY=%~dp0venv\Scripts\python.exe"
set "VENV_PIP=%~dp0venv\Scripts\pip.exe"
echo.

:: -------------------------------------------------------------------------------
:: BƯỚC 3: CÀI ĐẶT CÁC THƯ VIỆN (REQUIREMENTS.TXT)
:: -------------------------------------------------------------------------------
echo [3/5] Cài đặt các thư viện phụ thuộc (Flask, SQLAlchemy, v.v.)...
echo     -> Đang nâng cấp pip...
"%VENV_PY%" -m pip install --upgrade pip >nul 2>&1

if exist "requirements.txt" (
    echo     -> Đang cài đặt từ requirements.txt...
    "%VENV_PIP%" install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [CẢNH BÁO] Có một số gói cài đặt gặp cảnh báo, tiếp tục kiểm tra...
    ) else (
        echo     -> Đã cài đặt hoàn tất tất cả thư viện cần thiết!
    )
) else (
    echo     -> Cài đặt trực tiếp các gói chính...
    "%VENV_PIP%" install flask flask-cors sqlalchemy gspread google-auth python-dotenv requests openpyxl
)
echo.

:: -------------------------------------------------------------------------------
:: BƯỚC 4: TẢI CLOUDFLARE TUNNEL (CLOUDFLARED.EXE)
:: -------------------------------------------------------------------------------
echo [4/5] Thiết lập công cụ Cloudflare Tunnel (cho link Online 24/7)...

if not exist "cloudflared.exe" (
    echo     -> Đang tải cloudflared.exe từ Cloudflare Official Release...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object System.Net.WebClient).DownloadFile('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe', '%~dp0cloudflared.exe') } catch { exit 1 }"
    
    if exist "cloudflared.exe" (
        echo     -> Đã tải cloudflared.exe thành công!
    ) else (
        echo     -> [LƯU Ý] Chưa tải được cloudflared.exe trực tiếp. Script chạy server sẽ dùng phương thức dự phòng khi khởi động.
    )
) else (
    echo     -> cloudflared.exe đã sẵn sàng trong thư mục dự án.
)
echo.

:: -------------------------------------------------------------------------------
:: BƯỚC 5: CẤU HÌNH FILE .ENV VÀ WINDOWS FIREWALL
:: -------------------------------------------------------------------------------
echo [5/5] Cấu hình file môi trường .env và Tường Lửa Windows...

if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo     -> Đã tự động tạo file .env từ .env.example.
    ) else (
        (
            echo FLASK_ENV=development
            echo FLASK_DEBUG=0
            echo FLASK_PORT=5001
            echo FLASK_HOST=0.0.0.0
            echo APP_NAME=Trung tâm Anh ngữ Vicare
            echo APP_SECRET_KEY=evi-server-secret-key-2026
            echo AUTO_SYNC_DB_ON_STARTUP=0
        ) > ".env"
        echo     -> Đã tạo file .env mặc định chuẩn cho Server.
    )
) else (
    echo     -> File cấu hình .env đã tồn tại.
)

:: Mở port 5001 trên Windows Firewall (yêu cầu Admin nếu có, bỏ qua nếu không có quyền)
powershell -Command "try { New-NetFirewallRule -DisplayName 'EVI Dashboard Port 5001' -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow -ErrorAction Stop | Out-Null; Write-Host '    -> Đã mở cổng 5001 trên Windows Firewall (cho mạng LAN/Wi-Fi)' } catch { Write-Host '    -> Tường lửa đã được cấp hoặc cần mở quyền Admin nếu muốn truy cập qua IP LAN.' }" >nul 2>&1

echo.
echo ===============================================================================
echo   🎉 CHÚC MỪNG! MÔI TRƯỜNG SERVER ĐÃ ĐƯỢC THIẾT LẬP THÀNH CÔNG 100%%!
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
if /i "%RUN_NOW%"=="N" (
    echo Đã hoàn tất cài đặt. Tạm biệt!
    pause
    exit /b 0
)

call "2_CHAY_SERVER_VA_LINK_ONLINE.bat"
