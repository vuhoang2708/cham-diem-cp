@echo off
title VN100 Stock Scorer - ALL IN ONE
cls

echo ==================================================
echo   HE THONG CHAM DIEM CO PHIEU VN100 - KHOI DONG
echo ==================================================

:: 0. Don dep cac tien trinh cu de tranh xung dot
echo Dang don dep cac server cu...
taskkill /F /IM python.exe /T >nul 2>&1

:: 1. Khoi dong Chrome CDP (neu chua co)
echo [1/2] Dang kiem tra va mo Chrome CDP...
start "" "start_chrome.bat"
timeout /t 5

:: 2. Khoi dong Backend & Frontend (Hien cua so LOG de kiem tra)
echo [2/2] Dang mo Scoring Server & Dashboard (Port 8000)...
:: Khong dung /min de ban co the thay LOG
start "BACKEND_LOG" cmd /k ".\venv\Scripts\python backend\main.py"

:: 3. Mo Dashboard tren trinh duyet
echo Dang cho Server san sang...
timeout /t 8
echo.
echo === HE THONG DA SAN SANG! ===
echo Dang mo Dashboard tai: http://localhost:8000
start http://localhost:8000

echo.
echo (!) Luu y: Cua so "BACKEND_LOG" se hien thi chi tiet qua trinh quet du lieu.
echo     Khong dong cua so do khi dang su dung.
echo.
pause
