# 🛫 מערכת ניטור טיסות TusTus

מערכת אוטומטית לניטור טיסות באתר TusTus (tustus.co.il) ושליחת התראות מייל על טיסות חדשות וירידות מחיר.

## ✨ תכונות

- 🔍 **סריקה אוטומטית** של טיסות באתר TusTus
- 🆕 **זיהוי טיסות חדשות** ליעדים מועדפים
- 💰 **מעקב אחר שינויי מחירים** וירידות מחיר
- 📧 **שליחת התראות מייל** עם עיצוב יפה בעברית
- ⏰ **תזמון אוטומטי** לבדיקות תקופתיות
- 📊 **רישום פעילות** מפורט
- 🎯 **סינון יעדים** לפי העדפות אישיות

## 📋 דרישות מערכת

- Python 3.7+
- Chrome browser (לסריקת האתר)
- חיבור לאינטרנט
- חשבון Gmail (לשליחת מיילים)

## ⚙️ התקנה

### 1. הורדת הקוד
```bash
git clone <repository-url>
cd flight-monitor
```

### 2. התקנת תלויות Python
```bash
pip install -r requirements.txt
```

### 3. הגדרת משתני סביבה
העתק את הקובץ `.env.example` ל-`.env` ומלא את הפרטים:

```bash
cp .env.example .env
```

ערוך את הקובץ `.env`:
```env
# הגדרות מייל
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# רשימת תפוצה
MAILING_LIST=email1@example.com,email2@example.com,email3@example.com

# מרווח זמן בין בדיקות (בדקות)
CHECK_INTERVAL_MINUTES=30
```

### 4. הגדרת App Password ל-Gmail
1. עבור להגדרות החשבון ב-Google
2. הפעל "2-Step Verification"
3. צור "App Password" ספציפי לאפליקציה
4. השתמש ב-App Password במקום הסיסמה הרגילה

## 🚀 הפעלה

### הרצה חד-פעמית (בדיקה)
```bash
python main.py --run-once
```

### הרצה רציפה (ניטור אוטומטי)
```bash
python main.py --continuous
```

### הצגת סטטוס המערכת
```bash
python main.py --status
```

### בדיקת שליחת מייל
```bash
python main.py --test-email
```

## 📁 מבנה הקבצים

```
flight-monitor/
├── main.py                 # סקריפט ראשי
├── config.py              # הגדרות המערכת
├── flight_scraper.py      # מודול לסריקת טיסות
├── flight_monitor.py      # מודול לניטור ושוואה
├── email_sender.py        # מודול לשליחת מיילים
├── requirements.txt       # תלויות Python
├── .env.example          # דוגמה למשתני סביבה
├── .env                  # משתני סביבה (לא כלול)
├── flights_data.json     # נתוני טיסות (נוצר אוטומטית)
├── flight_monitor.log    # קובץ לוג (נוצר אוטומטית)
└── README.md            # המדריך הזה
```

## ⚙️ התאמה אישית

### עריכת יעדים מועדפים
ערוך את הקובץ `config.py` והוסף/הסר יעדים:

```python
PREFERRED_DESTINATIONS = [
    'ברלין',
    'פריז', 
    'לונדון',
    'רומא',
    # הוסף יעדים נוספים כאן...
]
```

### שינוי מרווח בדיקות
ערוך את הקובץ `.env`:
```env
CHECK_INTERVAL_MINUTES=15  # בדיקה כל 15 דקות
```

### שינוי קריטריונים לסינון
ערוך את הפונקציה `filter_relevant_flights` בקובץ `flight_monitor.py`:

```python
def filter_relevant_flights(self, flights: List[Dict]) -> List[Dict]:
    # שנה קריטריונים כמו מחיר מקסימלי, תוקף וכו'
    if price > 1500:  # מחיר מקסימלי 1500 שקל
        continue
```

## 🔧 הפעלה כשירות (Linux)

### יצירת קובץ systemd service
```bash
sudo nano /etc/systemd/system/flight-monitor.service
```

```ini
[Unit]
Description=Flight Monitor Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/flight-monitor
ExecStart=/usr/bin/python3 /path/to/flight-monitor/main.py --continuous
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### הפעלת השירות
```bash
sudo systemctl daemon-reload
sudo systemctl enable flight-monitor.service
sudo systemctl start flight-monitor.service
sudo systemctl status flight-monitor.service
```

## 📊 מעקב ולוגים

### צפייה בלוגים
```bash
tail -f flight_monitor.log
```

### בדיקת סטטוס
```bash
python main.py --status
```

## 🐛 פתרון בעיות

### בעיות Chrome Driver
אם יש בעיות עם Chrome Driver:
```bash
# בדיקת גרסת Chrome
google-chrome --version

# התקנה ידנית של ChromeDriver
wget https://chromedriver.storage.googleapis.com/XX.X.XXXX.XX/chromedriver_linux64.zip
```

### בעיות מייל
1. ודא ש-App Password נוצר נכון
2. בדוק שהמייל מאושר ל-"Less secure app access"
3. נסה עם שרת SMTP אחר

### בעיות סריקה
1. ודא חיבור לאינטרנט יציב
2. בדוק שהאתר זמין
3. נסה להפעיל ללא `--headless` mode לדיבוג

## 📈 שיפורים עתידיים

- [ ] תמיכה בחנויות טיסות נוספות
- [ ] ממשק web לניהול המערכת
- [ ] התראות Telegram/WhatsApp
- [ ] גרפים ודוחות מפורטים
- [ ] הגדרות מתקדמות לכל יעד
- [ ] תמיכה במטבעות זרים

## 📄 רישיון

פרויקט זה הוא בקוד פתוח לשימוש אישי. שימוש אחראי בלבד!

## ⚠️ הערות חשובות

1. **שימוש אחראי**: המערכת מיועדת לשימוש אישי בלבד
2. **תנאי שימוש**: הקפד לעמוד בתנאי השימוש של האתר
3. **מהירות בדיקות**: אל תגדיר מרווח בדיקות קצר מדי
4. **בדיקת חוקיות**: ודא שהשימוש חוקי במדינתך

## 🤝 תמיכה

לשאלות או בעיות, פתח issue ב-GitHub או צור קשר עם המפתח.

---

**בהצלחה עם מעקב הטיסות! ✈️** 
