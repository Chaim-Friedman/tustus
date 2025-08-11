@echo off
REM סקריפט השקה מהיר למערכת ניטור טיסות TusTus - Windows

cd /d "%~dp0"

REM בדיקה שהסביבה הוירטואלית קיימת
if not exist venv (
    echo ❌ סביבה וירטואלית לא נמצאה. הפעל: setup_windows.bat
    pause
    exit /b 1
)

REM בדיקה שקובץ .env קיים
if not exist .env (
    echo ❌ קובץ .env לא נמצא. העתק את .env.example ל-.env ומלא את הפרטים
    pause
    exit /b 1
)

REM הפעלת הסביבה הוירטואלית
call venv\Scripts\activate.bat

REM הפעלת המערכת לפי הפרמטר
if "%1"=="status" (
    python main.py --status
) else if "%1"=="test" (
    python main.py --test-email
) else if "%1"=="once" (
    python main.py --run-once
) else if "%1"=="help" (
    echo 🛫 מערכת ניטור טיסות רגע אחרון TusTus
    echo =================================
    echo.
    echo שימוש: run_windows.bat [פקודה]
    echo.
    echo פקודות זמינות:
    echo   status    - הצגת סטטוס המערכת
    echo   test      - שליחת מייל בדיקה
    echo   once      - הרצה חד-פעמית
    echo   start     - הפעלת ניטור רציף (ברירת מחדל)
    echo   help      - הצגת עזרה זו
    echo.
    echo דוגמאות:
    echo   run_windows.bat status    # בדיקת סטטוס
    echo   run_windows.bat test      # בדיקת מייל
    echo   run_windows.bat once      # בדיקה חד-פעמית
    echo   run_windows.bat           # הפעלת ניטור רציף
) else (
    REM ברירת מחדל - הפעלת ניטור רציף
    echo 🛫 מפעיל מערכת ניטור טיסות רגע אחרון TusTus...
    echo לעצירה: Ctrl+C
    echo =================================
    python main.py --continuous
)

if "%1"=="status" pause
if "%1"=="test" pause
if "%1"=="help" pause