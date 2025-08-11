@echo off
echo 🔧 תיקון בעיות Chrome Driver ב-Windows...
echo ================================================

REM ניקוי cache של WebDriverManager
echo 📦 מנקה cache של WebDriverManager...
rmdir /s /q "%USERPROFILE%\.wdm" 2>nul
echo ✅ Cache נוקה

REM הפעלת סביבה וירטואלית
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ❌ סביבה וירטואלית לא נמצאה. הפעל קודם: setup_windows.bat
    pause
    exit /b 1
)

REM הגדרת משתנה סביבה לכפיית 64-bit
echo 🔧 מגדיר WDM_ARCH=win64...
set WDM_ARCH=win64

REM התקנת חבילות נוספות
echo 📦 מתקין חבילות נוספות...
pip install chromedriver-binary-auto
pip install --upgrade selenium webdriver-manager

echo ✅ תיקון הושלם!
echo.
echo 📋 נסה עכשיו:
echo   run_windows.bat test
echo.
pause