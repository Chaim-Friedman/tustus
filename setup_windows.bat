@echo off
REM סקריפט התקנה אוטומטי למערכת ניטור טיסות TusTus - Windows
REM Script for automatic installation of TusTus Flight Monitor - Windows

echo 🛫 מתחיל התקנת מערכת ניטור טיסות TusTus על Windows...
echo ================================================

REM בדיקת Python
echo 🐍 בודק גרסת Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא מותקן או לא זמין ב-PATH
    echo אנא התקן Python 3.7+ מ: https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ נמצא Python %PYTHON_VERSION%

REM בדיקת pip
echo 📦 בודק pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip לא זמין
    echo נסה: python -m ensurepip --upgrade
    pause
    exit /b 1
)
echo ✅ pip זמין

REM יצירת סביבה וירטואלית
echo 🔧 יוצר סביבה וירטואלית...
if not exist venv (
    python -m venv venv
)
echo ✅ סביבה וירטואלית מוכנה

REM הפעלת סביבה וירטואלית
echo 📦 מפעיל סביבה וירטואלית ומתקין תלויות...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ שגיאה בהתקנת תלויות
    pause
    exit /b 1
)
echo ✅ תלויות הותקנו בהצלחה

REM יצירת קובץ .env אם לא קיים
if not exist .env (
    echo ⚙️ יוצר קובץ הגדרות...
    copy .env.example .env
    echo ✅ נוצר קובץ .env
    echo.
    echo 🔧 אנא ערוך את הקובץ .env והגדר:
    echo    - EMAIL_USERNAME (המייל שלך)
    echo    - EMAIL_PASSWORD (App Password מ-Gmail)
    echo    - MAILING_LIST (רשימת המיילים לקבלת התראות)
    echo.
    echo 📖 להוראות מפורטות ראה README.md
) else (
    echo ✅ קובץ .env כבר קיים
)

echo.
echo 🎉 ההתקנה הושלמה בהצלחה!
echo ================================================
echo.
echo 📋 צעדים הבאים:
echo 1. ערוך את הקובץ .env עם הנתונים שלך
echo 2. הפעל בדיקה: run_windows.bat test
echo 3. הפעל בדיקה חד-פעמית: run_windows.bat once  
echo 4. הפעל ניטור רציף: run_windows.bat
echo.
echo 📖 למידע נוסף: type README.md
echo.
echo ✈️ בהצלחה עם מעקב הטיסות!

REM הוראות להפעלה
echo.
echo 🔋 להפעלה בפעם הבאה:
echo venv\Scripts\activate.bat
pause