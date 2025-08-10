#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import schedule
import time
import logging
import signal
import sys
from datetime import datetime
from flight_monitor import FlightMonitor
from email_sender import EmailSender
from config import CHECK_INTERVAL_MINUTES

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flight_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class FlightAlertSystem:
    def __init__(self):
        self.monitor = FlightMonitor()
        self.email_sender = EmailSender()
        self.running = True
        
        # הגדרת טיפול בסיגנלים לסיום נקי
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """טיפול בסיגנל סיום"""
        logging.info(f"התקבל סיגנל {signum}, מתחיל סיום נקי...")
        self.running = False
    
    def check_and_notify(self):
        """פונקציה עיקרית לבדיקה ושליחת התראות"""
        try:
            logging.info("מתחיל בדיקת טיסות...")
            
            # בדיקת עדכונים
            result = self.monitor.check_for_updates()
            
            if 'error' in result:
                logging.error(f"שגיאה בבדיקת טיסות: {result['error']}")
                return
            
            new_flights = result.get('new_flights', [])
            price_changes = result.get('price_changes', [])
            
            # שליחת מייל רק אם יש עדכונים
            if new_flights or price_changes:
                logging.info(f"נמצאו עדכונים: {len(new_flights)} טיסות חדשות, {len(price_changes)} שינויי מחיר")
                
                # קבלת סטטיסטיקות
                stats = self.monitor.get_statistics()
                
                # שליחת מייל
                success = self.email_sender.send_update_email(new_flights, price_changes, stats)
                
                if success:
                    logging.info("מייל התראה נשלח בהצלחה")
                else:
                    logging.error("שגיאה בשליחת מייל התראה")
            else:
                logging.info("לא נמצאו עדכונים חדשים")
                
        except Exception as e:
            logging.error(f"שגיאה כללית בבדיקת טיסות: {e}")
    
    def run_once(self):
        """הרצה חד-פעמית"""
        logging.info("מריץ בדיקה חד-פעמית...")
        self.check_and_notify()
        logging.info("בדיקה חד-פעמית הושלמה")
    
    def run_continuous(self):
        """הרצה רציפה עם שדולר"""
        logging.info(f"מתחיל ניטור רציף - בדיקה כל {CHECK_INTERVAL_MINUTES} דקות")
        
        # הגדרת תזמון
        schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(self.check_and_notify)
        
        # הרצת בדיקה ראשונית
        logging.info("מריץ בדיקה ראשונית...")
        self.check_and_notify()
        
        # לולאה עיקרית
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # בדיקה כל 30 שניות אם יש משימות ממתינות
            except KeyboardInterrupt:
                logging.info("התקבל Ctrl+C, יוצא...")
                break
            except Exception as e:
                logging.error(f"שגיאה בלולאה העיקרית: {e}")
                time.sleep(60)  # המתנה דקה לפני המשך
        
        logging.info("מערכת הניטור נסגרה")
    
    def show_status(self):
        """הצגת סטטוס המערכת"""
        try:
            stats = self.monitor.get_statistics()
            
            print("=" * 60)
            print("🛫 סטטוס מערכת ניטור טיסות TusTus")
            print("=" * 60)
            
            print(f"📊 טיסות במעקב: {stats['total_flights_tracked']}")
            print(f"🎯 יעדים נמצאים: {len(stats['destinations_found'])}")
            if stats['destinations_found']:
                print(f"   {', '.join(sorted(stats['destinations_found']))}")
            
            if stats['price_range']['min'] and stats['price_range']['max']:
                print(f"💰 טווח מחירים: {stats['price_range']['min']}-{stats['price_range']['max']}₪")
                print(f"📈 מחיר ממוצע: {stats['average_price']:.0f}₪")
            
            print(f"🕒 בדיקה אחרונה: {stats['last_check'] or 'טרם בוצעה'}")
            print(f"⏱️  מרווח בדיקות: {CHECK_INTERVAL_MINUTES} דקות")
            
            print(f"📧 רשימת תפוצה: {len(self.email_sender.mailing_list)} נמענים")
            if self.email_sender.mailing_list:
                for email in self.email_sender.mailing_list:
                    print(f"   • {email}")
            
            print("=" * 60)
            
        except Exception as e:
            logging.error(f"שגיאה בהצגת סטטוס: {e}")

def main():
    """פונקציה עיקרית"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='מערכת ניטור והתראות לטיסות TusTus',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
דוגמאות שימוש:
  python main.py --run-once          # הרצה חד-פעמית
  python main.py --continuous        # הרצה רציפה (ברירת מחדל)
  python main.py --status            # הצגת סטטוס
  python main.py --test-email        # בדיקת מייל
        """
    )
    
    parser.add_argument('--run-once', action='store_true', 
                       help='הרצה חד-פעמית של בדיקת טיסות')
    parser.add_argument('--continuous', action='store_true', 
                       help='הרצה רציפה עם שדולר (ברירת מחדל)')
    parser.add_argument('--status', action='store_true',
                       help='הצגת סטטוס המערכת')
    parser.add_argument('--test-email', action='store_true',
                       help='שליחת מייל בדיקה')
    
    args = parser.parse_args()
    
    # יצירת מערכת ההתראות
    alert_system = FlightAlertSystem()
    
    try:
        if args.status:
            alert_system.show_status()
        elif args.test_email:
            print("שולח מייל בדיקה...")
            success = alert_system.email_sender.test_email()
            if success:
                print("✅ מייל בדיקה נשלח בהצלחה!")
            else:
                print("❌ שגיאה בשליחת מייל בדיקה")
        elif args.run_once:
            alert_system.run_once()
        else:
            # ברירת מחדל - הרצה רציפה
            alert_system.run_continuous()
            
    except KeyboardInterrupt:
        logging.info("המערכת נסגרה על ידי המשתמש")
    except Exception as e:
        logging.error(f"שגיאה כללית: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()