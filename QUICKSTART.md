# 🚀 התחלה מהירה - מערכת ניטור טיסות TusTus

## התקנה מהירה (Linux)

```bash
# 1. הורד את הקוד
git clone <repository-url>
cd flight-monitor

# 2. הפעל התקנה אוטומטית
./setup.sh

# 3. ערוך את הגדרות המייל
nano .env
```

## הגדרת קובץ .env

```env
# המייל שלך (Gmail)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-from-gmail

# רשימת מיילים לקבלת התראות
MAILING_LIST=email1@example.com,email2@example.com

# כל כמה דקות לבדוק (30 = כל חצי שעה)
CHECK_INTERVAL_MINUTES=30
```

## הפעלה מהירה

```bash
# בדיקת סטטוס
./run.sh status

# בדיקת מייל
./run.sh test

# הרצה חד-פעמית (בדיקה)
./run.sh once

# הפעלת ניטור רציף
./run.sh
```

## יצירת App Password ב-Gmail

1. עבור ל: [Google Account Settings](https://myaccount.google.com)
2. Security → 2-Step Verification (הפעל אם לא מופעל)
3. Security → App passwords
4. צור סיסמה חדשה עבור "Mail"
5. השתמש בסיסמה זו ב-`.env`

## עריכת יעדים מועדפים

ערוך `config.py`:

```python
PREFERRED_DESTINATIONS = [
    'ברלין',
    'פריז', 
    'לונדון',
    'רומא',
    'דובאי',
    # הוסף יעדים נוספים...
]
```

## הפעלה כשירות (אוטומטי)

```bash
# יצירת שירות
sudo nano /etc/systemd/system/flight-monitor.service

# הוסף תוכן:
[Unit]
Description=TusTus Flight Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/flight-monitor
ExecStart=/path/to/flight-monitor/run.sh
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target

# הפעלת השירות
sudo systemctl daemon-reload
sudo systemctl enable flight-monitor
sudo systemctl start flight-monitor
```

## צפייה בלוגים

```bash
# לוגים מקומיים
tail -f flight_monitor.log

# לוגי השירות
sudo journalctl -u flight-monitor -f
```

---

## ⚠️ הערות חשובות

- השתמש במערכת באופן אחראי
- אל תגדיר מרווח בדיקות קצר מדי (מינימום 15 דקות)
- ודא שאתה עומד בתנאי השימוש של האתר

## 🆘 עזרה

```bash
./run.sh help    # עזרה מהירה
python main.py --help    # עזרה מפורטת
```

---

**בהצלחה! ✈️**