#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

def load_env_file(file_path):
    """טעינת קובץ .env ידנית"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

print("🔍 בדיקה מקיפה של מערכת ניטור הטיסות")
print("=" * 60)

# טעינת קובץ .env
load_env_file('.env')

# בדיקת משתני סביבה
print("📋 משתני סביבה:")
print(f"   EXCLUDED_DESTINATIONS: {os.getenv('EXCLUDED_DESTINATIONS', 'לא מוגדר')}")
print(f"   CHECK_INTERVAL_MINUTES: {os.getenv('CHECK_INTERVAL_MINUTES', 'לא מוגדר')}")

# קריאת קובץ config.py
try:
    with open('config.py', 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    print(f"\n📄 תצורת המערכת:")
    
    # חיפוש יעדים מועדפים
    if 'PREFERRED_DESTINATIONS = [' in config_content:
        start = config_content.find('PREFERRED_DESTINATIONS = [')
        end = config_content.find(']', start) + 1
        preferred_section = config_content[start:end]
        
        destinations = [line.strip().strip("'\"") for line in preferred_section.split('\n') 
                       if line.strip().startswith("'") or line.strip().startswith('"')]
        print(f"   ✅ יעדים מועדפים: {len(destinations)} יעדים")
        
    # חיפוש הגדרות נוספות
    if 'FOCUS_ON_NEW_FLIGHTS_ONLY = True' in config_content:
        print("   ✅ התמקדות בטיסות חדשות בלבד")
    if 'IGNORE_PRICE_CHANGES = True' in config_content:
        print("   ✅ מעקב שינויי מחירים מושבת")
    if 'MAX_FLIGHT_AGE_HOURS = 72' in config_content:
        print("   ✅ טיסות עד 72 שעות (3 ימים)")
        
except Exception as e:
    print(f"   ❌ שגיאה בקריאת config.py: {e}")

# בדיקת לוגיקת החרגה
print(f"\n🔍 בדיקת לוגיקת החרגה:")
excluded_destinations = os.getenv('EXCLUDED_DESTINATIONS', '')
if excluded_destinations:
    excluded_list = [d.strip() for d in excluded_destinations.split(',') if d.strip()]
    
    # בדיקה עם יעדים שונים
    test_cases = [
        ('ברלין', 'יעד אירופאי פופולרי'),
        ('פריז', 'יעד אירופאי פופולרי'),
        ('קטמנדו', 'יעד אסייתי מוחרג'),
        ('בנגקוק', 'יעד אסייתי מוחרג'),
        ('לונדון', 'יעד אירופאי פופולרי'),
        ('הודו', 'יעד אסייתי מוחרג')
    ]
    
    for dest, description in test_cases:
        if dest in excluded_list:
            print(f"   ❌ {dest} - מוחרג ({description})")
        else:
            print(f"   ✅ {dest} - לא מוחרג ({description})")
else:
    print("   ⚠️  אין יעדים מוחרגים מוגדרים")

# בדיקת קבצי המערכת
print(f"\n📁 בדיקת קבצי המערכת:")
system_files = [
    'flight_monitor.py',
    'flight_scraper.py', 
    'simple_scraper.py',
    'email_sender.py',
    'main.py'
]

for file in system_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - חסר")

# בדיקת לוגים
print(f"\n📊 בדיקת לוגים:")
if os.path.exists('flight_monitor.log'):
    with open('flight_monitor.log', 'r', encoding='utf-8') as f:
        log_content = f.read()
    print(f"   ✅ קובץ לוג קיים")
    if 'לא הוגדרו נתוני מייל' in log_content:
        print(f"   ⚠️  אזהרה: לא הוגדרו נתוני מייל")
else:
    print(f"   ❌ קובץ לוג לא קיים")

# בדיקת נתונים
print(f"\n💾 בדיקת נתונים:")
if os.path.exists('flights_data.json'):
    try:
        with open('flights_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   ✅ קובץ נתונים קיים")
        print(f"   📊 טיסות במעקב: {len(data.get('flights', []))}")
        print(f"   🆕 טיסות חדשות: {len(data.get('new_flights', []))}")
    except:
        print(f"   ❌ שגיאה בקריאת קובץ נתונים")
else:
    print(f"   ⚠️  קובץ נתונים לא קיים (טרם בוצעה סריקה)")

# סיכום והמלצות
print(f"\n📋 סיכום והמלצות:")
print("=" * 60)

if excluded_destinations:
    print(f"✅ המערכת מוגדרת כראוי עם {len(excluded_list)} יעדים מוחרגים")
    print(f"✅ יעדים מוחרגים: {', '.join(excluded_list)}")
    print(f"✅ כל שאר היעדים יקבלו התראה על טיסות חדשות")
else:
    print(f"⚠️  המערכת לא מוגדרת עם יעדים מוחרגים")
    print(f"⚠️  כל היעדים יקבלו התראה על טיסות חדשות")

print(f"\n🔧 הגדרות נוספות:")
print(f"   • תדירות בדיקה: כל {os.getenv('CHECK_INTERVAL_MINUTES', '60')} דקות")
print(f"   • התמקדות: טיסות חדשות בלבד")
print(f"   • מחירים: מעקב שינויי מחירים מושבת")

if 'your-email@gmail.com' in os.getenv('EMAIL_USERNAME', ''):
    print(f"\n⚠️  אזהרה: יש להגדיר נתוני מייל אמיתיים ב-.env")
    print(f"⚠️  המערכת לא תוכל לשלוח התראות ללא הגדרת מייל")

print(f"\n" + "=" * 60)
print("✅ בדיקה מקיפה הושלמה")