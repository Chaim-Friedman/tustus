# 🚀 התחלה מהירה - מערכת ניטור טיסות רגע אחרון TusTus

## 🎯 מה המערכת עושה?

המערכת מתמקדת ב**טיסות רגע אחרון** באתר TusTus:
- ✈️ **זיהוי טיסות חדשות** שמתווספות לימים הקרובים
- 📧 **התראות מייל מיידיות** כשמתווספות טיסות חדשות  
- 💰 **מחירים קבועים** - אין צורך במעקב שינויי מחירים
- ⏰ **בדיקה כל שעה** - מתאים לקצב השינוי של טיסות רגע אחרון

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

# כל כמה דקות לבדוק (60 = כל שעה - מתאים לטיסות רגע אחרון)
CHECK_INTERVAL_MINUTES=60
```

## הפעלה מהירה

```bash
# בדיקת סטטוס
./run.sh status

# בדיקת מייל
./run.sh test

# הרצה חד-פעמית (בדיקה)
./run.sh once

# הפעלת ניטור רציף לטיסות רגע אחרון
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
    'איסטנבול',
    'בודפשט',
    # הוסף יעדים נוספים...
]
```

## איך זה עובד?

### 🔍 **מה המערכת בודקת:**
- טיסות חדשות שמתווספות לימים הקרובים (עד 14 יום)
- יעדים מהרשימה המועדפת שלך
- טיסות שלא היו קיימות בבדיקה הקודמת

### 📧 **מתי תקבל מייל:**
- כשמתווספת טיסה חדשה ליעד מועדף
- רק על טיסות **חדשות** (לא על שינויי מחירים)
- עם פרטי הטיסה: יעד, תאריכים, מידע נוסף

### ⏰ **תזמון החכם:**
- בדיקה כל שעה (מתאים לטיסות רגע אחרון)
- לא מעמיס על האתר
- מזהה טיסות מיד כשהן מתווספות

## הפעלה כשירות (אוטומטי)

```bash
# יצירת שירות
sudo nano /etc/systemd/system/flight-monitor.service

# הוסף תוכן:
[Unit]
Description=TusTus Last Minute Flight Monitor
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

## 🎯 מיוחד לטיסות רגע אחרון

### ⚡ **תגובה מהירה:**
- כשמגיע מייל - בדוק מיד! טיסות רגע אחרון נגמרות מהר
- המערכת בודקת כל שעה כדי לזהות טיסות חדשות בזמן

### 📱 **טיפים להצלחה:**
- הגדר התראות push על המייל
- בדוק את האתר מיד אחרי קבלת התראה
- הוסף יעדים גמישים - ככל שיותר יעדים, יותר הזדמנויות

### 🎯 **אופטימיזציה:**
- המערכת מתמקדת ב-14 הימים הקרובים
- מסננת רק יעדים מהרשימה שלך
- מתעלמת ממחירים (כי הם קבועים)

---

## ⚠️ הערות חשובות

- השתמש במערכת באופן אחראי
- המערכת מותאמת לטיסות רגע אחרון - מחירים קבועים
- מרווח של שעה מתאים לקצב השינוי של טיסות רגע אחרון
- ודא שאתה עומד בתנאי השימוש של האתר

## 🆘 עזרה

```bash
./run.sh help    # עזרה מהירה
python main.py --help    # עזרה מפורטת
```

---

**בהצלחה עם מעקב טיסות רגע אחרון! ⚡✈️**