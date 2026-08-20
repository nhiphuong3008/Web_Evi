@echo off
chcp 65001 >nul
title [EVI] Cập Nhật Code Mới Từ GitHub
color 0E

echo ===============================================================================
echo            🔄 CẬP NHẬT CODE MỚI NHẤT CHO EVI DASHBOARD (GIT PULL)
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Đang kéo cập nhật mới nhất từ GitHub Repository...
git pull origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [LỖI] Không thể kéo code từ Git. Vui lòng kiểm tra kết nối mạng hoặc xung đột file local.
    pause
    exit /b 1
)

echo.
echo [2/3] Kiểm tra và cập nhật các thư viện mới (nếu có)...
if exist "venv\Scripts\pip.exe" (
    venv\Scripts\pip.exe install -r requirements.txt --quiet
    echo     -> Đã đồng bộ thư viện thành công.
) else (
    pip install -r requirements.txt --quiet
)

echo.
echo [3/3] Hoàn tất cập nhật phiên bản mới nhất!
echo.
echo ===============================================================================
echo   🎉 CODE ĐÃ ĐƯỢC CẬP NHẬT THÀNH CÔNG VỀ MÁY SERVER!
echo ===============================================================================
echo.

set /p RESTART="Bạn có muốn khởi động lại Server ngay không? (Y/N, mặc định Y): "
if /i "%RESTART%"=="N" (
    echo Tạm biệt!
    pause
    exit /b 0
)

call "2_CHAY_SERVER_VA_LINK_ONLINE.bat"
