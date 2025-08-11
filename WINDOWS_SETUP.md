# 🚀 התקנה מהירה ל-Windows - מערכת ניטור טיסות רגע אחרון TusTus

## ⚡ התקנה אוטומטית (מומלץ)

1. **הורד את כל הקבצים** לתיקייה (למשל: `C:\TusTus\`)

2. **הפעל התקנה אוטומטית:**
   ```cmd
   setup_windows.bat
   ```

3. **ערוך הגדרות מייל:**
   ```cmd
   notepad .env
   ```

4. **הפעל את המערכת:**
   ```cmd
   run_windows.bat
   ```

## 🔧 התקנה ידנית (אם האוטומטית לא עובדת)

### שלב 1: בדיקת Python
```cmd
python --version
```
אם לא עובד, התקן Python מ: [python.org](https://python.org)

### שלב 2: יצירת סביבה וירטואלית
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### שלב 3: התקנת תלויות
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### שלב 4: הגדרת קונפיגורציה
```cmd
copy .env.example .env
notepad .env
```

## ⚙️ הגדרת קובץ .env

ערוך את הקובץ `.env` עם הנתונים שלך:

```env
# המייל שלך (Gmail)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-from-gmail

# רשימת מיילים לקבלת התראות
MAILING_LIST=email1@example.com,email2@example.com

# כל כמה דקות לבדוק (60 = כל שעה)
CHECK_INTERVAL_MINUTES=60
```

## 🚀 הפעלה

### עם הסקריפטים:
```cmd
run_windows.bat status    # בדיקת סטטוס
run_windows.bat test      # בדיקת מייל
run_windows.bat once      # בדיקה חד-פעמית
run_windows.bat           # ניטור רציף
```

### הפעלה ידנית:
```cmd
venv\Scripts\activate.bat
python main.py --status
python main.py --test-email
python main.py --run-once
python main.py --continuous
```

## 🔍 פתרון בעיות נפוצות

### בעיה: "ModuleNotFoundError: No module named 'schedule'"
**פתרון:**
```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### בעיה: "[WinError 193] %1 is not a valid Win32 application"
**פתרון:**
```cmd
fix_windows_chrome.bat
```
או באופן ידני:
```cmd
rmdir /s /q "%USERPROFILE%\.wdm"
set WDM_ARCH=win64
pip install chromedriver-binary-auto
```

### בעיה: Python לא מוכר
**פתרון:**
1. התקן Python מ: https://python.org
2. וודא שסימנת "Add Python to PATH" בהתקנה

### בעיה: Chrome Driver
**פתרון:**
1. התקן Google Chrome
2. המערכת תוריד אוטומטית את ה-driver הנדרש

### בעיה: שגיאות מייל
**פתרון:**
1. בדוק שיצרת App Password ב-Gmail
2. וודא ש-2-Step Verification מופעל
3. השתמש ב-App Password ולא בסיסמה הרגילה

## 📧 יצירת App Password ב-Gmail

1. עבור ל: [Google Account Settings](https://myaccount.google.com)
2. Security → 2-Step Verification (הפעל אם לא מופעל)
3. Security → App passwords
4. בחר "Mail" וצור סיסמה חדשה
5. השתמש בסיסמה זו ב-`.env`

## 🔄 הפעלה אוטומטית (Windows Service)

ליצירת שירות Windows שרץ אוטומטית:

1. **התקן NSSM** (Non-Sucking Service Manager):
   - הורד מ: https://nssm.cc/download
   - חלץ ל: `C:\nssm\`

2. **יצירת השירות:**
   ```cmd
   cd C:\nssm\win64
   nssm install "TusTus Flight Monitor"
   ```

3. **הגדרת השירות:**
   - Path: `C:\TusTus\run_windows.bat`
   - Startup directory: `C:\TusTus\`
   - Arguments: (השאר ריק)

4. **הפעלת השירות:**
   ```cmd
   nssm start "TusTus Flight Monitor"
   ```

## 📊 מעקב ובדיקה

### צפייה בלוגים:
```cmd
type flight_monitor.log
```

### בדיקת סטטוס:
```cmd
run_windows.bat status
```

### עצירת המערכת:
לחץ `Ctrl+C` במסוף

## 🎯 טיפים לWindows

1. **הפעל כמנהל** אם יש בעיות הרשאות
2. **השבת אנטי-ווירוס זמנית** אם חוסם התקנה
3. **וודא חיבור אינטרנט יציב**
4. **סגור PyCharm** לפני הרצת המערכת (למניעת קונפליקטים)

---

## 🆘 עזרה

אם יש בעיות:
1. הפעל: `run_windows.bat help`
2. בדוק את הקובץ `flight_monitor.log`
3. ודא שכל התלויות מותקנות

---

**בהצלחה עם מעקב טיסות רגע אחרון על Windows! ✈️🪟**