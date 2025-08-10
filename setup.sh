#!/bin/bash

# סקריפט התקנה אוטומטי למערכת ניטור טיסות TusTus
# Script for automatic installation of TusTus Flight Monitor

set -e

echo "🛫 מתחיל התקנת מערכת ניטור טיסות TusTus..."
echo "================================================"

# בדיקת Python
echo "🐍 בודק גרסת Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 לא מותקן. אנא התקן Python 3.7 ומעלה"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ נמצא Python $PYTHON_VERSION"

# בדיקת pip
echo "📦 בודק pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 לא מותקן. מתקין pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi
echo "✅ pip זמין"

# התקנת Chrome אם לא קיים
echo "🌐 בודק Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
    echo "📥 מתקין Google Chrome..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
fi
echo "✅ Google Chrome מותקן"

# יצירת סביבה וירטואלית
echo "🔧 יוצר סביבה וירטואלית..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "✅ סביבה וירטואלית מוכנה"

# התקנת תלויות
echo "📦 מתקין תלויות Python..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ תלויות הותקנו בהצלחה"

# יצירת קובץ .env אם לא קיים
if [ ! -f ".env" ]; then
    echo "⚙️ יוצר קובץ הגדרות..."
    cp .env.example .env
    echo "✅ נוצר קובץ .env"
    echo ""
    echo "🔧 אנא ערוך את הקובץ .env והגדר:"
    echo "   - EMAIL_USERNAME (המייל שלך)"
    echo "   - EMAIL_PASSWORD (App Password מ-Gmail)"
    echo "   - MAILING_LIST (רשימת המיילים לקבלת התראות)"
    echo ""
    echo "📖 להוראות מפורטות ראה README.md"
else
    echo "✅ קובץ .env כבר קיים"
fi

# הפיכת הקבצים לבני הפעלה
chmod +x main.py
chmod +x setup.sh

echo ""
echo "🎉 ההתקנה הושלמה בהצלחה!"
echo "================================================"
echo ""
echo "📋 צעדים הבאים:"
echo "1. ערוך את הקובץ .env עם הנתונים שלך"
echo "2. הפעל בדיקה: python main.py --test-email"
echo "3. הפעל בדיקה חד-פעמית: python main.py --run-once"
echo "4. הפעל ניטור רציף: python main.py --continuous"
echo ""
echo "📖 למידע נוסף: cat README.md"
echo ""
echo "✈️ בהצלחה עם מעקב הטיסות!"

# הפעלת הסביבה הוירטואלית
echo ""
echo "🔋 להפעלת הסביבה הוירטואלית בפעם הבאה:"
echo "source venv/bin/activate"