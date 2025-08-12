import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import logging
from datetime import datetime
from config import TUSTUS_URL, PREFERRED_DESTINATIONS, EXCLUDED_DESTINATIONS, LOG_LEVEL, FILTER_ONLY_PREFERRED

# הגדרת לוגים (נשלטים מהגדרה)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
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
        """הגדרת WebDriver עם Chrome"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Selenium Manager will locate/download the correct driver automatically
            self.driver = webdriver.Chrome(options=chrome_options)

            # Post-init stealth tweak
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
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
            wait = WebDriverWait(self.driver, 30)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # המתנה נוספת לטעינת תוכן דינמי
            time.sleep(6)

            # ניסיון לגלול כדי לטעון תוכן דינמי נוסף
            try:
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1.5)
            except Exception:
                pass

            # ניסיון לסגירת פופאפים/קוקיז
            self._dismiss_popups()
            
            # שמירת צילום מסך ותוכן HTML לעזרה בדיבוג
            try:
                with open('last_page.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                self.driver.save_screenshot('last_screenshot.png')
                logging.info("נשמר צילום מסך וקובץ HTML של הדף הנוכחי (last_screenshot.png, last_page.html)")
            except Exception:
                pass

            # חיפוש אלמנטים של טיסות
            flights = []
            
            # ניסיון לזהות טיסות על פי מבנים נפוצים
            flight_elements = self.find_flight_elements()
            
            for idx, element in enumerate(flight_elements):
                flight_data = self.extract_flight_data(element)
                if flight_data and self.is_relevant_destination(flight_data.get('destination', '')):
                    flights.append(flight_data)
                elif flight_data:
                    logging.info(f"טיסה לא רלוונטית לפי סינון: {flight_data.get('destination')} - מוחרג/לא מועדף")
            
            logging.info(f"נמצאו {len(flights)} טיסות רלוונטיות")
            return flights
            
        except Exception as e:
            logging.error(f"שגיאה בסריקת טיסות: {e}")
            return []
    
    def find_flight_elements(self):
        """חיפוש אלמנטים של טיסות בדף"""
        flight_elements = []
        seen_ids = set()
        
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
        
        total_found = 0
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    unique_new = 0
                    for el in elements:
                        try:
                            el_id = el.id
                        except Exception:
                            el_id = id(el)
                        if el_id in seen_ids:
                            continue
                        seen_ids.add(el_id)
                        flight_elements.append(el)
                        unique_new += 1
                    total_found += unique_new
                    logging.info(f"נמצאו {len(elements)} (חדש ייחודיים: {unique_new}) אלמנטים עם סלקטור {selector}")
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
            # טקסט מהאלמנט (כולל innerText/textContent/מאפיינים)
            text = element.text.strip()
            if not text:
                try:
                    text = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", element) or ""
                    text = text.strip()
                except Exception:
                    text = ""
            if not text:
                # נסיון ממאפיינים
                try:
                    attr_bits = []
                    for attr in ("aria-label", "title", "alt"): 
                        val = element.get_attribute(attr)
                        if val:
                            attr_bits.append(val)
                    text = " \n ".join(attr_bits).strip()
                except Exception:
                    pass
            if not text:
                logging.debug(f"אלמנט ריק - דילוג")
                return None
            
            logging.debug(f"מעבד אלמנט עם טקסט: {text[:100]}...")
            
            # חיפוש יעד
            destination = self.extract_destination(text, element)
            logging.debug(f"יעד שנמצא: {destination}")
            
            # דילוג על יעדים מוחרגים
            if destination and any(destination == ex for ex in EXCLUDED_DESTINATIONS):
                logging.debug(f"יעד {destination} מוחרג - דילוג")
                return None
            
            # חיפוש מחיר
            price = self.extract_price(text, element)
            logging.debug(f"מחיר שנמצא: {price}")
            
            # חיפוש תאריכים
            dates = self.extract_dates(text, element)
            logging.debug(f"תאריכים שנמצאו: {dates}")
            
            if destination and price:
                logging.info(f"✅ טיסה נמצאה: {destination} - {price}₪")
                return {
                    'destination': destination,
                    'price': price,
                    'dates': dates,
                    'full_text': text,
                    'scraped_at': datetime.now().isoformat(),
                    'url': TUSTUS_URL
                }
            else:
                logging.debug(f"❌ אלמנט לא עבר סינון: יעד={destination}, מחיר={price}")
                
        except Exception as e:
            logging.warning(f"שגיאה בחילוץ נתונים מאלמנט: {e}")
        
        return None
    
    def extract_destination(self, text, element):
        """חילוץ יעד מהטקסט"""
        # חיפוש יעדים מהרשימה המועדפת
        for dest in PREFERRED_DESTINATIONS:
            if dest in text:
                logging.debug(f"יעד נמצא ברשימה המועדפת: {dest}")
                return dest
        
        # חיפוש מילות מפתח נוספות לערים
        cities_keywords = ['ברלין', 'פריז', 'לונדון', 'רומא', 'מדריד', 'אמסטרדם', 'פראג', 'ויאנה', 'ברצלונה', 'מילאנו', 'ניס', 'ליסבון']
        for city in cities_keywords:
            if city in text:
                logging.debug(f"יעד נמצא במילות מפתח: {city}")
                return city
        
        logging.debug(f"לא נמצא יעד בטקסט: {text[:50]}...")
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
        # אם הוגדר החרגה - לא רלוונטי
        if any(destination == ex for ex in EXCLUDED_DESTINATIONS):
            return False
        if FILTER_ONLY_PREFERRED:
            return destination in PREFERRED_DESTINATIONS
        # אם לא מסננים רק מועדפים - כל יעד שאינו מוחרג רלוונטי
        return True
    
    def close(self):
        """סגירת WebDriver"""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver נסגר")

    def _dismiss_popups(self):
        """ניסיון לסגור פופאפים/קוקיז נפוצים"""
        try:
            candidates = [
                "//button[contains(., 'קבל') or contains(., 'אישור') or contains(., 'סגור') or contains(., 'הבנתי') or contains(., 'Accept') or contains(., 'OK') or contains(., 'Got it')]",
                "//a[contains(., 'קבל') or contains(., 'אישור') or contains(., 'סגור') or contains(., 'הבנתי') or contains(., 'Accept') or contains(., 'OK') or contains(., 'Got it')]",
                "//div[contains(@role,'dialog')]//button",
                "//button[contains(@id,'accept') or contains(@id,'ok') or contains(@id,'close') or contains(@class,'accept') or contains(@class,'ok') or contains(@class,'close') or contains(@class,'cookie')]",
            ]
            for xpath in candidates:
                try:
                    elems = self.driver.find_elements(By.XPATH, xpath)
                    for btn in elems[:3]:
                        try:
                            btn.click()
                            logging.info("נסגר פופאפ/קוקיז")
                            time.sleep(0.5)
                        except Exception:
                            continue
                except Exception:
                    continue
        except Exception:
            pass

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