import os
from dotenv import load_dotenv

load_dotenv()

# הגדרות מייל
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# רשימת תפוצה
MAILING_LIST = os.getenv('MAILING_LIST', '').split(',')

# הגדרות סריקה
TUSTUS_URL = 'https://www.tustus.co.il/Arkia/Home'
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '60'))  # שעה במקום חצי שעה

# יעדים מועדפים - ניתן להוסיף או לשנות
PREFERRED_DESTINATIONS = [
    'ברלין',
    'פריז', 
    'לונדון',
    'רומא',
    'אמסטרדם',
    'פראג',
    'ויאנה',
    'מדריד',
    'ברצלונה',
    'אתונה',
    'דובאי',
    'בנגקוק',
    'קטמנדו',
    'נפאל',
    'הודו',
    'ניו יורק',
    'מיאמי',
    "לוס אנג'לס",
    'איסטנבול',
    'בודפשט',
    'מילאנו',
    'ניס',
    'ליסבון',
    'זאגרב',
    'בלגרד'
]

# רשימת יעדים לא רלוונטיים (יוצאים מההתראה)
EXCLUDED_DESTINATIONS = [d.strip() for d in os.getenv('EXCLUDED_DESTINATIONS', '').split(',') if d.strip()]

# רמת לוגים
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# סינון יעדים: אם True נתריע רק על יעדים מועדפים (למעט מוחרגים). אם False נתריע על כל יעד שאינו מוחרג.
FILTER_ONLY_PREFERRED = os.getenv('FILTER_ONLY_PREFERRED', 'false').lower() in ('1', 'true', 'yes', 'on')

# הגדרות נוספות
DATA_FILE = 'flights_data.json'
LOG_FILE = 'flight_monitor.log'

# הגדרות ספציפיות לאתר TusTus
# מאחר שהמחירים קבועים והטיסות לימים הקרובים
FOCUS_ON_NEW_FLIGHTS_ONLY = True  # התמקד רק בטיסות חדשות
IGNORE_PRICE_CHANGES = True  # התעלם משינויי מחירים
MAX_FLIGHT_AGE_HOURS = 72  # טיסות רק עד 3 ימים
MIN_DAYS_ADVANCE = 1  # טיסות החל ממחר