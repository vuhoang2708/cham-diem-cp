@echo off
echo ========================================================
echo KHOI DONG CHROME CHO HE THONG CHAM DIEM CO PHIEU
echo ========================================================
echo.
echo Dang mo Chrome ho tro Automation...
echo Vui long dang nhap vao Fireant.vn (chi can lan dau tien).
echo KHONG DONG cua so Chrome nay trong qua trinh he thong dang chay!
echo.

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%CD%\chrome_profile"
