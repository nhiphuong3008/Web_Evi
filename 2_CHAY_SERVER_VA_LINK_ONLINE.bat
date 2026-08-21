@echo off
chcp 65001 >nul
title [EVI] Đang Chạy Server & Mở Đường Link Online 24/7
color 0A

echo ===============================================================================
echo                🌟 KHỞI CHẠY EVI DASHBOARD SERVER 24/7
echo ===============================================================================
echo.

cd /d "%~dp0"

:: Chuẩn hóa cấu hình Port 5001 trong .env nếu có
if exist ".env" (
    powershell -NoProfile -Command "(Get-Content .env) -replace 'FLASK_PORT=5000', 'FLASK_PORT=5001' | Set-Content .env"
)

:: -------------------------------------------------------------------------------
:: 1. TẮT CÁC TIẾN TRÌNH CŨ
:: -------------------------------------------------------------------------------
echo [1/4] Đang dọn dẹp các tiến trình cũ (nếu có)...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance" >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1

:: -------------------------------------------------------------------------------
:: 2. XÁC ĐỊNH PYTHON VENV
:: -------------------------------------------------------------------------------
set "PY_CMD="
if exist "venv\Scripts\python.exe" (
    set "PY_CMD=venv\Scripts\python.exe"
    goto PYTHON_READY
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto PYTHON_READY
)
set "PY_CMD=python"

:PYTHON_READY
:: -------------------------------------------------------------------------------
:: 3. KHỞI ĐỘNG FLASK BACKEND
:: -------------------------------------------------------------------------------
echo [2/4] Đang khởi chạy Flask Backend Server (Port 5001)...
start "EVI Backend Server" /min "%PY_CMD%" app.py

:: Đợi backend sẵn sàng
set "COUNT=0"
:WAIT_SERVER
ping 127.0.0.1 -n 2 >nul
powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('127.0.0.1', 5001); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto SERVER_READY
set /a COUNT+=1
if %COUNT% GEQ 20 (
    echo [CẢNH BÁO] Backend khởi động lâu hơn dự kiến, đang tiếp tục mở Tunnel...
    goto SERVER_READY
)
echo       -> Đang chờ Backend phản hồi... (%COUNT%s)
goto WAIT_SERVER

:SERVER_READY
echo     -> Flask Backend đã sẵn sàng trên cổng 5001!
echo.

:: -------------------------------------------------------------------------------
:: 4. KHỞI TẠO ĐƯỜNG LINK ONLINE CỐ ĐỊNH (NGROK & CLOUDFLARE)
:: -------------------------------------------------------------------------------
echo [3/4] Đang kết nối đường link Online cố định (hardy-porthole-wildland.ngrok-free.dev)...

:: Đảm bảo ngrok.exe tồn tại
if not exist "ngrok.exe" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 'ngrok.zip'); Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force; Remove-Item 'ngrok.zip' -ErrorAction SilentlyContinue"
)

if exist "ngrok.exe" (
    "%~dp0ngrok.exe" config add-authtoken 3IBiTbkXguuBIBqAroSuk5Y3ugF_6yudsrKPch9sr97rURSqk
    start "EVI Ngrok Online Tunnel" "%~dp0ngrok.exe" http 5001 --domain=hardy-porthole-wildland.ngrok-free.dev
    echo     -> Đã khởi động Ngrok Tunnel cố định!
) else (
    echo     -> [LƯU Ý] Chưa tìm thấy ngrok.exe. Đang tải tự động...
)


:: Bật thêm Cloudflare Tunnel dự phòng song song
set "CF_LOG=%TEMP%\cloudflared_evi.log"
if exist "%CF_LOG%" del /f /q "%CF_LOG%" >nul 2>&1
set "CF_URL="

if exist "cloudflared.exe" (
    start "EVI Cloudflare Tunnel" /min "%~dp0cloudflared.exe" tunnel --url http://127.0.0.1:5001 --logfile "%CF_LOG%"
    ping 127.0.0.1 -n 3 >nul
    if exist "%CF_LOG%" (
        for /f "usebackq tokens=*" %%L in (`powershell -NoProfile -Command "(Get-Content -Path '%CF_LOG%' -ErrorAction SilentlyContinue | Select-String 'https://[a-zA-Z0-9-]+\.trycloudflare\.com').Matches.Value | Select-Object -First 1"`) do (
            set "CF_URL=%%L"
        )
    )
)

:: -------------------------------------------------------------------------------
:: 5. TÌM ĐỊA CHỈ IP MẠNG NỘI BỘ (LAN)
:: -------------------------------------------------------------------------------
set "LAN_IP=127.0.0.1"
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi*','Ethernet*','vEthernet*' | Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -notlike '127.*' } | Select-Object -First 1).IPAddress"`) do (
    set "LAN_IP=%%I"
)

echo.
echo ===============================================================================
echo   🎉 HỆ THỐNG EVI DASHBOARD ĐÃ SẴN SÀNG HOẠT ĐỘNG 24/7!
echo ===============================================================================
echo.
echo   🌐 1. ĐƯỜNG LINK ONLINE CỐ ĐỊNH VĨNH VIỄN (TRUY CẬP TỪ XA MỌI NƠI 24/7):
echo      👉 https://hardy-porthole-wildland.ngrok-free.dev
echo.
echo      (Link này cố định trọn đời, không bao giờ thay đổi dù tắt mở Server!)
echo.
if defined CF_URL (
    echo   🛡️ 2. ĐƯỜNG LINK ONLINE DỰ PHÒNG (CLOUDFLARE):
    echo      👉 %CF_URL%
    echo.
)
echo   📶 3. TRUY CẬP CÙNG MẠNG WI-FI / MẠNG NỘI BỘ (LAN):
echo      👉 http://%LAN_IP%:5001
echo.
echo   💻 4. TRUY CẬP TRỰC TIẾP TRÊN MÁY SERVER NÀY:
echo      👉 http://127.0.0.1:5001
echo.
echo ===============================================================================
echo   [LƯU Ý QUAN TRỌNG]:
echo   • Giữ cửa sổ này mở để Server và Link Online tiếp tục hoạt động.
echo   • Khi muốn dừng hệ thống, chạy file [4_DUNG_SERVER.bat] hoặc đóng cửa sổ này.
echo ===============================================================================
echo.

:: Tự động mở trình duyệt với domain cố định
start https://hardy-porthole-wildland.ngrok-free.dev

echo Nhấn phím bất kỳ hoặc thu nhỏ cửa sổ này để Server chạy ngầm...
pause >nul
