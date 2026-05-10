@echo off
set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "PROFILE_PATH=%~dp0chrome_profile"

if not exist "%PROFILE_PATH%" mkdir "%PROFILE_PATH%"

echo Khoi dong Chrome voi CDP port 9222...
start "" "%CHROME_PATH%" ^
    --remote-debugging-port=9222 ^
    --user-data-dir="%PROFILE_PATH%" ^
    --no-first-run ^
    --no-default-browser-check ^
    "https://fireant.vn/dashboard/content/symbols/VCB"

echo Chrome da san sang. Hay dang nhap Fireant neu can.
timeout /t 3
