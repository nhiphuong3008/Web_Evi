@echo off
chcp 65001 >nul
title [EVI] Đang Chạy Server & Mở Đường Link Online
color 0A

echo ===============================================================================
echo                🌟 KHỞI CHẠY EVI DASHBOARD SERVER 24/7
echo ===============================================================================
echo.

cd /d "%~dp0"

:: -------------------------------------------------------------------------------
:: 1. TẮT CÁC TIẾN TRÌNH CŨ
:: -------------------------------------------------------------------------------
echo [1/4] Đang dọn dẹp các tiến trình cũ (nếu có)...
powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''python.exe'' AND CommandLine LIKE ''%%app.py%%''' | Remove-CimInstance" >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1

:: -------------------------------------------------------------------------------
:: 2. XÁC ĐỊNH PYTHON VENV
:: -------------------------------------------------------------------------------
set "PY_CMD="
if exist "venv\Scripts\python.exe" (
    set "PY_CMD=venv\Scripts\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    set "PY_CMD=python"
)

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
:: 4. KHỞI TẠO CLOUDFLARE TUNNEL ONLINE LINK
:: -------------------------------------------------------------------------------
echo [3/4] Đang tạo đường link Online HTTPS qua Cloudflare Tunnel...
set "CF_LOG=%TEMP%\cloudflared_evi.log"
if exist "%CF_LOG%" del /f /q "%CF_LOG%" >nul 2>&1

set "PUBLIC_URL="

if exist "cloudflared.exe" (
    start "EVI Cloudflare Tunnel" /min "%~dp0cloudflared.exe" tunnel --url http://127.0.0.1:5001 --logfile "%CF_LOG%"
    
    :: Đợi và trích xuất URL từ log
    set "TUNNEL_WAIT=0"
    :WAIT_TUNNEL
    ping 127.0.0.1 -n 2 >nul
    if exist "%CF_LOG%" (
        for /f "usebackq tokens=*" %%L in (`powershell -NoProfile -Command "(Get-Content -Path '%CF_LOG%' -ErrorAction SilentlyContinue | Select-String 'https://[a-zA-Z0-9-]+\.trycloudflare\.com').Matches.Value | Select-Object -First 1"`) do (
            set "PUBLIC_URL=%%L"
        )
    )
    if defined PUBLIC_URL goto TUNNEL_DONE
    set /a TUNNEL_WAIT+=1
    if %TUNNEL_WAIT% GEQ 15 goto TUNNEL_TIMEOUT
    echo       -> Đang kết nối Cloudflare mạng toàn cầu... (%TUNNEL_WAIT%s)
    goto WAIT_TUNNEL
) else (
    echo     -> [LƯU Ý] Chưa có cloudflared.exe. Bạn có thể chạy '1_CAI_DAT_SERVER_TU_DONG.bat' để tải tự động.
    goto SKIP_TUNNEL
)

:TUNNEL_TIMEOUT
echo     -> Đang tiếp tục lấy link, bạn có thể kiểm tra file log: %CF_LOG%
goto TUNNEL_DONE

:TUNNEL_DONE
echo     -> Tạo link Cloudflare Tunnel thành công!

:SKIP_TUNNEL
:: -------------------------------------------------------------------------------
:: 5. TÌM ĐỊA CHỈ IP MẠNG NỘI BỘ (LAN)
:: -------------------------------------------------------------------------------
set "LAN_IP=127.0.0.1"
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi*','Ethernet*','vEthernet*' | Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -notlike '127.*' } | Select-Object -First 1).IPAddress"`) do (
    set "LAN_IP=%%I"
)

echo.
echo ===============================================================================
echo   🎉 HỆ THỐNG EVI DASHBOARD ĐÃ SẴN SÀNG HOẠT ĐỘNG!
echo ===============================================================================
echo.
echo   💻 1. TRUY CẬP TRÊN MÁY SERVER NÀY:
echo      👉 http://127.0.0.1:5001
echo.
echo   📶 2. TRUY CẬP CÙNG MẠNG WI-FI / MẠNG NỘI BỘ (LAN):
echo      👉 http://%LAN_IP%:5001
echo.
if defined PUBLIC_URL (
    echo   🌐 3. ĐƯỜNG LINK ONLINE 24/7 (TRUY CẬP TỪ XA BẤT KỲ ĐÂU):
    echo      👉 %PUBLIC_URL%
    echo.
    echo      (Gửi link trên cho Giáo viên, Nhân viên CM hoặc mở trên Điện thoại)
) else (
    echo   🌐 3. ĐƯỜNG LINK ONLINE:
    echo      Đang tạo kết nối ngầm... Bạn có thể xem trong cửa sổ Cloudflare Tunnel.
)
echo.
echo ===============================================================================
echo   [LƯU Ý QUAN TRỌNG]:
echo   • Giữ cửa sổ này mở để Server và Link Online tiếp tục hoạt động 24/7.
echo   • Khi muốn dừng hệ thống, chạy file [4_DUNG_SERVER.bat] hoặc đóng cửa sổ này.
echo ===============================================================================
echo.

:: Tự động mở trình duyệt
start http://127.0.0.1:5001

echo Nhấn phím bất kỳ hoặc thu nhỏ cửa sổ này để Server chạy ngầm...
pause >nul
