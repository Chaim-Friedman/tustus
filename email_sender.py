import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import logging
from typing import List, Dict
from config import (
    EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_USERNAME, 
    EMAIL_PASSWORD, MAILING_LIST, TUSTUS_URL
)

class EmailSender:
    def __init__(self):
        self.smtp_server = EMAIL_SMTP_SERVER
        self.smtp_port = EMAIL_SMTP_PORT
        self.username = EMAIL_USERNAME
        self.password = EMAIL_PASSWORD
        self.mailing_list = [email.strip() for email in MAILING_LIST if email.strip()]
        
        if not self.username or not self.password:
            logging.warning("לא הוגדרו נתוני מייל - שליחת מיילים לא תעבוד")
    
    def create_flights_html(self, flights: List[Dict], title: str) -> str:
        """יצירת HTML לטיסות"""
        if not flights:
            return ""
        
        html = f"""
        <div style="margin: 20px 0;">
            <h2 style="color: #2c5aa0; border-bottom: 2px solid #2c5aa0; padding-bottom: 10px;">
                {title}
            </h2>
            <div style="display: grid; gap: 15px;">
        """
        
        for flight in flights:
            destination = flight.get('destination', 'לא זמין')
            price = flight.get('price', 0)
            dates = flight.get('dates', [])
            full_text = flight.get('full_text', '')[:200] + '...' if len(flight.get('full_text', '')) > 200 else flight.get('full_text', '')
            
            dates_str = ', '.join(dates) if dates else 'תאריכים לא זמינים'
            
            html += f"""
                <div style="
                    border: 1px solid #ddd; 
                    border-radius: 8px; 
                    padding: 15px; 
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <h3 style="color: #495057; margin: 0; font-size: 18px;">
                            ✈️ {destination}
                        </h3>
                        <span style="
                            background: #28a745; 
                            color: white; 
                            padding: 5px 15px; 
                            border-radius: 20px; 
                            font-weight: bold;
                            font-size: 16px;
                        ">
                            {price}₪
                        </span>
                    </div>
                    <div style="color: #6c757d; margin-bottom: 8px;">
                        📅 תאריכים: {dates_str}
                    </div>
                    <div style="color: #6c757d; font-size: 14px; line-height: 1.4;">
                        {full_text}
                    </div>
                </div>
            """
        
        html += "</div></div>"
        return html
    
    def create_price_changes_html(self, price_changes: List[Dict]) -> str:
        """יצירת HTML לשינויי מחירים"""
        if not price_changes:
            return ""
        
        html = """
        <div style="margin: 20px 0;">
            <h2 style="color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 10px;">
                🔥 ירידות מחיר
            </h2>
            <div style="display: grid; gap: 15px;">
        """
        
        for change in price_changes:
            destination = change.get('destination', 'לא זמין')
            previous_price = change.get('previous_price', 0)
            current_price = change.get('current_price', 0)
            discount = change.get('discount', 0)
            
            html += f"""
                <div style="
                    border: 1px solid #dc3545; 
                    border-radius: 8px; 
                    padding: 15px; 
                    background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
                    box-shadow: 0 2px 4px rgba(220,53,69,0.2);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="color: #721c24; margin: 0; font-size: 18px;">
                            🎯 {destination}
                        </h3>
                        <div style="text-align: right;">
                            <div style="color: #6c757d; text-decoration: line-through; font-size: 14px;">
                                {previous_price}₪
                            </div>
                            <div style="
                                background: #dc3545; 
                                color: white; 
                                padding: 5px 15px; 
                                border-radius: 20px; 
                                font-weight: bold;
                                font-size: 16px;
                            ">
                                {current_price}₪
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; color: #155724; font-weight: bold;">
                        💰 חיסכון: {discount}₪
                    </div>
                </div>
            """
        
        html += "</div></div>"
        return html
    
    def create_email_html(self, new_flights: List[Dict], price_changes: List[Dict], stats: Dict) -> str:
        """יצירת תבנית HTML למייל"""
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # התחלת HTML
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>עדכון טיסות</title>
        </head>
        <body style="
            font-family: Arial, Helvetica, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f8f9fa;
            direction: rtl;
        ">
            <div style="
                max-width: 800px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 10px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            ">
                <!-- Header -->
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px 20px; 
                    text-align: center;
                ">
                    <h1 style="margin: 0; font-size: 28px;">
                        ✈️ עדכון טיסות TusTus
                    </h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                        {current_time}
                    </p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
        """
        
        # סיכום מהיר
        summary = f"""
                    <div style="
                        background: #e3f2fd; 
                        border-left: 4px solid #2196f3; 
                        padding: 20px; 
                        margin-bottom: 25px;
                        border-radius: 0 8px 8px 0;
                    ">
                        <h3 style="color: #1976d2; margin: 0 0 10px 0;">📊 סיכום</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold; color: #2196f3;">
                                    {len(new_flights)}
                                </div>
                                <div style="color: #666; font-size: 14px;">טיסות חדשות</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold; color: #f44336;">
                                    {len(price_changes)}
                                </div>
                                <div style="color: #666; font-size: 14px;">ירידות מחיר</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold; color: #4caf50;">
                                    {stats.get('total_flights_tracked', 0)}
                                </div>
                                <div style="color: #666; font-size: 14px;">סה\"כ טיסות</div>
                            </div>
                        </div>
                    </div>
        """
        
        html += summary
        
        # הוספת טיסות חדשות
        if new_flights:
            html += self.create_flights_html(new_flights, "🆕 טיסות חדשות")
        
        # הוספת שינויי מחירים
        if price_changes:
            html += self.create_price_changes_html(price_changes)
        
        # אם אין עדכונים
        if not new_flights and not price_changes:
            html += """
                    <div style="
                        text-align: center; 
                        padding: 40px; 
                        color: #6c757d;
                        background: #f8f9fa;
                        border-radius: 8px;
                        margin: 20px 0;
                    ">
                        <div style="font-size: 48px; margin-bottom: 15px;">😴</div>
                        <h3 style="color: #495057;">אין עדכונים חדשים</h3>
                        <p>לא נמצאו טיסות חדשות או שינויי מחיר מהבדיקה האחרונה.</p>
                    </div>
            """
        
        # Footer
        html += f"""
                    <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                    
                    <div style="text-align: center; color: #6c757d; font-size: 14px;">
                        <p>
                            <a href="{TUSTUS_URL}" style="
                                color: #667eea; 
                                text-decoration: none; 
                                font-weight: bold;
                            ">🌐 בקר באתר TusTus</a>
                        </p>
                        <p style="margin: 5px 0;">
                            המערכת בודקת עדכונים באופן אוטומטי כל 30 דקות
                        </p>
                        <p style="margin: 5px 0; font-size: 12px;">
                            נוצר על ידי מערכת ניטור טיסות אוטומטית
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_update_email(self, new_flights: List[Dict], price_changes: List[Dict], stats: Dict) -> bool:
        """שליחת מייל עדכון"""
        if not self.mailing_list:
            logging.warning("רשימת תפוצה ריקה")
            return False
        
        if not self.username or not self.password:
            logging.error("נתוני מייל לא הוגדרו")
            return False
        
        try:
            # קביעת נושא המייל
            if new_flights and price_changes:
                subject = f"🔥 {len(new_flights)} טיסות חדשות ו-{len(price_changes)} ירידות מחיר!"
            elif new_flights:
                subject = f"✈️ {len(new_flights)} טיסות חדשות נמצאו!"
            elif price_changes:
                subject = f"💰 {len(price_changes)} ירידות מחיר מעולות!"
            else:
                subject = "📊 עדכון שגרתי - אין שינויים"
                # אם אין עדכונים, לא שולחים מייל
                logging.info("אין עדכונים לשליחה")
                return True
            
            # יצירת HTML
            html_content = self.create_email_html(new_flights, price_changes, stats)
            
            # הגדרת המייל
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = ', '.join(self.mailing_list)
            
            # הוספת תוכן HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # שליחת המייל
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logging.info(f"מייל נשלח בהצלחה ל-{len(self.mailing_list)} נמענים")
            return True
            
        except Exception as e:
            logging.error(f"שגיאה בשליחת מייל: {e}")
            return False
    
    def test_email(self) -> bool:
        """שליחת מייל בדיקה"""
        test_flights = [
            {
                'destination': 'ברלין',
                'price': 599,
                'dates': ['15/03/2024', '22/03/2024'],
                'full_text': 'טיסה לברלין במחיר מעולה! כולל מזווה ועוד הטבות.',
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        test_price_changes = [
            {
                'destination': 'פריז',
                'previous_price': 850,
                'current_price': 650,
                'discount': 200
            }
        ]
        
        test_stats = {
            'total_flights_tracked': 25,
            'last_check': datetime.now().isoformat()
        }
        
        return self.send_update_email(test_flights, test_price_changes, test_stats)

def test_email_sender():
    """פונקציה לבדיקת שליחת מייל"""
    sender = EmailSender()
    
    print(f"רשימת תפוצה: {sender.mailing_list}")
    print(f"שרת מייל: {sender.smtp_server}:{sender.smtp_port}")
    
    if sender.username and sender.password:
        print("שולח מייל בדיקה...")
        success = sender.test_email()
        if success:
            print("✅ מייל בדיקה נשלח בהצלחה!")
        else:
            print("❌ שגיאה בשליחת מייל")
    else:
        print("❌ נתוני מייל לא הוגדרו - לא ניתן לשלוח מייל")

if __name__ == "__main__":
    test_email_sender()