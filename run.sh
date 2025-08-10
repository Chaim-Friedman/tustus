#!/bin/bash

# סקריפט השקה מהיר למערכת ניטור טיסות TusTus

cd "$(dirname "$0")"

# בדיקה שהסביבה הוירטואלית קיימת
if [ ! -d "venv" ]; then
    echo "❌ סביבה וירטואלית לא נמצאה. הפעל: ./setup.sh"
    exit 1
fi

# בדיקה שקובץ .env קיים
if [ ! -f ".env" ]; then
    echo "❌ קובץ .env לא נמצא. העתק את .env.example ל-.env ומלא את הפרטים"
    exit 1
fi

# הפעלת הסביבה הוירטואלית
source venv/bin/activate

# הפעלת המערכת לפי הפרמטר
if [ "$1" = "status" ]; then
    python main.py --status
elif [ "$1" = "test" ]; then
    python main.py --test-email
elif [ "$1" = "once" ]; then
    python main.py --run-once
elif [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "🛫 מערכת ניטור טיסות TusTus"
    echo "================================="
    echo ""
    echo "שימוש: ./run.sh [פקודה]"
    echo ""
    echo "פקודות זמינות:"
    echo "  status    - הצגת סטטוס המערכת"
    echo "  test      - שליחת מייל בדיקה"
    echo "  once      - הרצה חד-פעמית"
    echo "  start     - הפעלת ניטור רציף (ברירת מחדל)"
    echo "  help      - הצגת עזרה זו"
    echo ""
    echo "דוגמאות:"
    echo "  ./run.sh status    # בדיקת סטטוס"
    echo "  ./run.sh test      # בדיקת מייל"
    echo "  ./run.sh once      # בדיקה חד-פעמית"
    echo "  ./run.sh           # הפעלת ניטור רציף"
else
    # ברירת מחדל - הפעלת ניטור רציף
    echo "🛫 מפעיל מערכת ניטור טיסות TusTus..."
    echo "לעצירה: Ctrl+C"
    echo "================================="
    python main.py --continuous
fi