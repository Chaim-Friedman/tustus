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
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '30'))

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
    'לוס אנג\'לס'
]

# הגדרות נוספות
DATA_FILE = 'flights_data.json'
LOG_FILE = 'flight_monitor.log'