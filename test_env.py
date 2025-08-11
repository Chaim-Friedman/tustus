#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def load_env_file(file_path):
    """טעינת קובץ .env ידנית"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

print("🔍 בדיקת תצורת המערכת עם .env")
print("=" * 50)

# טעינת קובץ .env
load_env_file('.env')

# בדיקת משתני סביבה
print("📋 משתני סביבה:")
print(f"   EXCLUDED_DESTINATIONS: {os.getenv('EXCLUDED_DESTINATIONS', 'לא מוגדר')}")
print(f"   CHECK_INTERVAL_MINUTES: {os.getenv('CHECK_INTERVAL_MINUTES', 'לא מוגדר')}")

# בדיקת יעדים מוחרגים
excluded_destinations = os.getenv('EXCLUDED_DESTINATIONS', '')
if excluded_destinations:
    excluded_list = [d.strip() for d in excluded_destinations.split(',') if d.strip()]
    print(f"\n🚫 יעדים מוחרגים: {len(excluded_list)}")
    for dest in excluded_list:
        print(f"   • {dest}")
else:
    print("\n🚫 אין יעדים מוחרגים מוגדרים")

# בדיקת לוגיקת החרגה
print(f"\n🔍 בדיקת לוגיקת החרגה:")
test_destinations = ['ברלין', 'פריז', 'קטמנדו', 'בנגקוק']

for dest in test_destinations:
    if excluded_destinations and dest in excluded_destinations:
        print(f"   ❌ {dest} - מוחרג (לא יקבל התראה)")
    else:
        print(f"   ✅ {dest} - לא מוחרג (יקבל התראה)")

print(f"\n📊 סיכום:")
if excluded_destinations:
    print(f"   • יש {len(excluded_list)} יעדים מוחרגים")
    print(f"   • יעדים אלה לא יקבלו התראה על טיסות חדשות")
    print(f"   • כל שאר היעדים יקבלו התראה כרגיל")
else:
    print(f"   • אין יעדים מוחרגים")
    print(f"   • כל היעדים יקבלו התראה על טיסות חדשות")

print("\n" + "=" * 50)
print("✅ בדיקה הושלמה")