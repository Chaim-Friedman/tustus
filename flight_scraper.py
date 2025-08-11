import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import logging
import platform
import os
=======
from datetime import datetime
from config import TUSTUS_URL, PREFERRED_DESTINATIONS

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flight_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class FlightScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """הגדרת WebDriver עם Chrome - מותאם לWindows"""
=======
        """הגדרת WebDriver עם Chrome"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # ריצה ברקע
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # זיהוי מערכת הפעלה
            system = platform.system().lower()
            logging.info(f"מערכת הפעלה זוהתה: {system}")
            
            try:
                # ניסיון ראשון: ChromeDriverManager עם התאמה למערכת
                if system == "windows":
                    # עבור Windows - נסה לכפות 64-bit
                    os.environ['WDM_ARCH'] = 'win64'
                    logging.info("מגדיר WDM_ARCH=win64 עבור Windows")
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            except Exception as e:
                logging.warning(f"ChromeDriverManager נכשל: {e}")
                logging.info("מנסה פתרונות חלופיים...")
                
                # ניסיון שני: מחיקת cache ונסיון נוסף
                try:
                    import shutil
                    wdm_cache = os.path.expanduser("~/.wdm")
                    if os.path.exists(wdm_cache):
                        shutil.rmtree(wdm_cache)
                        logging.info("נוקה cache של WebDriverManager")
                    
                    # נסיון חוזר עם cache נקיה
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    
                except Exception as e2:
                    logging.warning(f"ניסיון שני נכשל: {e2}")
                    
                    # ניסיון שלישי: Chrome מותקן במערכת
                    try:
                        logging.info("מנסה להשתמש ב-Chrome ללא WebDriverManager...")
                        
                        # נתיבים אפשריים של Chrome ב-Windows
                        chrome_paths = [
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
                        ]
                        
                        chrome_path = None
                        for path in chrome_paths:
                            if os.path.exists(path):
                                chrome_path = path
                                break
                        
                        if chrome_path:
                            chrome_options.binary_location = chrome_path
                            logging.info(f"נמצא Chrome ב: {chrome_path}")
                            
                            # ניסיון עם chromedriver-binary
                            try:
                                import chromedriver_binary
                                self.driver = webdriver.Chrome(options=chrome_options)
                                logging.info("הצלחה עם chromedriver-binary")
                            except ImportError:
                                # התקנת chromedriver-binary אם לא קיים
                                logging.info("מתקין chromedriver-binary...")
                                os.system("pip install chromedriver-binary-auto")
                                import chromedriver_binary
                                self.driver = webdriver.Chrome(options=chrome_options)
                        else:
                            raise Exception("Chrome לא נמצא במערכת")
                    
                    except Exception as e3:
                        logging.error(f"כל הניסיונות נכשלו: {e3}")
                        # ניסיון אחרון עם Firefox
                        try:
                            logging.info("מנסה Firefox כחלופה...")
                            from selenium.webdriver.firefox.options import Options as FirefoxOptions
                            from selenium.webdriver.firefox.service import Service as FirefoxService
                            from webdriver_manager.firefox import GeckoDriverManager
                            
                            firefox_options = FirefoxOptions()
                            firefox_options.add_argument('--headless')
                            service = FirefoxService(GeckoDriverManager().install())
                            self.driver = webdriver.Firefox(service=service, options=firefox_options)
                            logging.info("הצלחה עם Firefox")
                            
                        except Exception as e4:
                            logging.error(f"גם Firefox נכשל: {e4}")
                            raise Exception("לא ניתן להגדיר browser. אנא התקן Chrome או Firefox")
            
            # הוספת הגדרות נוספות לאחר יצירת הדרייבר
            if self.driver:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logging.info("WebDriver הוגדר בהצלחה")
                
=======
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("WebDriver הוגדר בהצלחה")
        except Exception as e:
            logging.error(f"שגיאה בהגדרת WebDriver: {e}")
            raise
    
    def scrape_flights(self):
        """סריקת טיסות מהאתר"""
        try:
            logging.info(f"מתחיל סריקה של {TUSTUS_URL}")
            self.driver.get(TUSTUS_URL)
            
            # המתנה לטעינת הדף
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # המתנה נוספת לטעינת תוכן דינמי
            time.sleep(5)
            
            # חיפוש אלמנטים של טיסות
            flights = []
            
            # ניסיון לזהות טיסות על פי מבנים נפוצים
            flight_elements = self.find_flight_elements()
            
            for element in flight_elements:
                flight_data = self.extract_flight_data(element)
                if flight_data and self.is_relevant_destination(flight_data.get('destination', '')):
                    flights.append(flight_data)
            
            logging.info(f"נמצאו {len(flights)} טיסות רלוונטיות")
            return flights
            
        except Exception as e:
            logging.error(f"שגיאה בסריקת טיסות: {e}")
            return []
    
    def find_flight_elements(self):
        """חיפוש אלמנטים של טיסות בדף"""
        flight_elements = []
        
        # ניסיון מספר סלקטורים נפוצים
        selectors = [
            ".flight-item",
            ".flight",
            ".trip",
            ".offer",
            ".deal",
            "[class*='flight']",
            "[class*='trip']",
            "[class*='offer']",
            ".card",
            ".product"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logging.info(f"נמצאו {len(elements)} אלמנטים עם סלקטור {selector}")
                    flight_elements.extend(elements)
                    break
            except:
                continue
        
        # אם לא נמצאו אלמנטים ספציפיים, נחפש אלמנטים כלליים
        if not flight_elements:
            try:
                # חיפוש אלמנטים שמכילים מילות מפתח
                all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '₪') or contains(text(), 'שח') or contains(text(), 'טיסה') or contains(text(), 'יעד')]")
                flight_elements = all_elements[:20]  # מגבילים למקסימום 20 אלמנטים
                logging.info(f"נמצאו {len(flight_elements)} אלמנטים כלליים")
            except:
                pass
        
        return flight_elements
    
    def extract_flight_data(self, element):
        """חילוץ נתונים מאלמנט טיסה"""
        try:
            text = element.text.strip()
            if not text:
                return None
            
            # חיפוש יעד
            destination = self.extract_destination(text, element)
            
            # חיפוש מחיר
            price = self.extract_price(text, element)
            
            # חיפוש תאריכים
            dates = self.extract_dates(text, element)
            
            if destination and price:
                return {
                    'destination': destination,
                    'price': price,
                    'dates': dates,
                    'full_text': text,
                    'scraped_at': datetime.now().isoformat(),
                    'url': TUSTUS_URL
                }
        except Exception as e:
            logging.warning(f"שגיאה בחילוץ נתונים מאלמנט: {e}")
        
        return None
    
    def extract_destination(self, text, element):
        """חילוץ יעד מהטקסט"""
        # חיפוש יעדים מהרשימה המועדפת
        for dest in PREFERRED_DESTINATIONS:
            if dest in text:
                return dest
        
        # חיפוש מילות מפתח נוספות לערים
        cities_keywords = ['ברלין', 'פריז', 'לונדון', 'רומא', 'מדריד', 'אמסטרדם', 'פראג', 'ויאנה', 'ברצלונה', 'מילאנו', 'ניס', 'ליסבון']
        for city in cities_keywords:
            if city in text:
                return city
        
        return None
    
    def extract_price(self, text, element):
        """חילוץ מחיר מהטקסט"""
        import re
        
        # חיפוש מחירים בפורמטים שונים
        price_patterns = [
            r'(\d{1,4})\s*₪',
            r'(\d{1,4})\s*שח',
            r'₪\s*(\d{1,4})',
            r'שח\s*(\d{1,4})',
            r'(\d{1,4})\s*שקל',
            r'מ\s*(\d{1,4})',
            r'החל\s*מ\s*(\d{1,4})'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        
        return None
    
    def extract_dates(self, text, element):
        """חילוץ תאריכים מהטקסט"""
        import re
        
        # חיפוש תאריכים בפורמטים שונים
        date_patterns = [
            r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
            r'(\d{1,2}\s*[בב]\w+\s*\d{4})',
            r'(ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates if dates else None
    
    def is_relevant_destination(self, destination):
        """בדיקה אם היעד רלוונטי"""
        if not destination:
            return False
        return destination in PREFERRED_DESTINATIONS
    
    def close(self):
        """סגירת WebDriver"""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver נסגר")

def test_scraper():
    """פונקציה לבדיקת הסקרפר"""
    scraper = FlightScraper()
    try:
        flights = scraper.scrape_flights()
        print(f"נמצאו {len(flights)} טיסות:")
        for flight in flights:
            print(f"- {flight['destination']}: {flight['price']}₪")
            print(f"  תאריכים: {flight['dates']}")
            print(f"  טקסט מלא: {flight['full_text'][:100]}...")
            print("-" * 50)
    finally:
        scraper.close()

if __name__ == "__main__":
    test_scraper()