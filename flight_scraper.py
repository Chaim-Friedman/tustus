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

            # ניווט לחלקים רלוונטיים (רגע אחרון/מבצעים) אם קיימים
            self._try_open_last_minute_sections()

            # המתנה ממוקדת לנחיתה של רכיבי תוכן אופייניים
            focus_selectors = [
                "[class*='flight']", "[class*='result']", "[class*='item']", "[class*='card']"
            ]
            for sel in focus_selectors:
                try:
                    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, sel)))
                    logging.info(f"אלמנטים לפי {sel} נטענו")
                    break
                except Exception:
                    continue

            # ניסיון ללחוץ על כפתורי 'עוד'/'טען עוד' אם קיימים
            try:
                more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'עוד') or contains(., 'טען עוד') or contains(., 'הצג עוד') or contains(., 'Load more')]")
                for btn in more_buttons[:3]:
                    try:
                        btn.click()
                        logging.info("נלחץ כפתור 'עוד'/טעינה נוספת")
                        time.sleep(2)
                    except Exception:
                        continue
            except Exception:
                pass
            
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

            # איסוף מהמסמך הראשי
            flights.extend(self._collect_from_current_context(context_name="main"))

            # איסוף מכל iframes
            try:
                frames = self.driver.find_elements(By.TAG_NAME, 'iframe')
                logging.info(f"נמצאו {len(frames)} iframes בעמוד")
                for i, frame in enumerate(frames):
                    try:
                        self.driver.switch_to.frame(frame)
                        logging.info(f"עברנו ל-iframe #{i}")
                        flights.extend(self._collect_from_current_context(context_name=f"iframe#{i}"))
                    except Exception as e:
                        logging.debug(f"שגיאה במעבר ל-iframe #{i}: {e}")
                    finally:
                        self.driver.switch_to.default_content()
            except Exception:
                pass

            # הסרת כפילויות לפי יעד+תאריכים+טקסט
            unique = []
            seen = set()
            for f in flights:
                key = (f.get('destination'), tuple(f.get('dates') or []), f.get('full_text')[:80])
                if key in seen:
                    continue
                seen.add(key)
                unique.append(f)
            flights = unique

            logging.info(f"נמצאו {len(flights)} טיסות רלוונטיות מכל ההקשרים")
            if flights:
                return flights

            # fallback: סריקה על טקסט מלא של העמוד, ללא דרישת מחיר
            logging.info("לא נמצאו טיסות מתוך אלמנטים. מבצע סריקה מטקסט העמוד כחלופה.")
            try:
                page_text = self.driver.execute_script("return document.body.innerText || document.body.textContent || '';") or ""
                fallback_flights = self.extract_from_page_text(page_text)
                logging.info(f"Fallback: נמצאו {len(fallback_flights)} טיסות מטקסט העמוד")
                if fallback_flights:
                    return fallback_flights

                # ניסיון אינטראקטיבי: הקלקה על אלמנטים/כרטיסים כדי לחשוף טקסט ואז חילוץ
                interactive = self._try_click_expand_and_extract(limit_clicks=12)
                logging.info(f"Interactive: נמצאו {len(interactive)} טיסות לאחר הקלקות/הרחבות")
                if interactive:
                    return interactive

                # ניסיון נוסף: פרסינג של HTML מלא
                html = self.driver.page_source
                html_flights = self.extract_from_html(html)
                logging.info(f"HTML parse: נמצאו {len(html_flights)} טיסות מתוך HTML")
                return html_flights
            except Exception as e:
                logging.warning(f"Fallback נכשל: {e}")
                return []
            
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
            ".product",
            "[class*='dest']",
            "[class*='city']",
            "[class*='destination']",
            "[class*='arkia']",
            "[class*='result']",
            "[class*='item']"
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
 
        # חיפוש לפי מילות מפתח בטקסט (innerText)
        try:
            keywords = list(dict.fromkeys(PREFERRED_DESTINATIONS + [
                'Berlin','Paris','London','Rome','Madrid','Amsterdam','Prague','Vienna','Barcelona','Milan','Nice','Lisbon',
                'Athens','Istanbul','Budapest','Zagreb','Belgrade','Dubai','New York','Miami','Los Angeles'
            ]))
            kw_elems = self._find_elements_by_keywords(keywords)
            if kw_elems:
                unique_new = 0
                for el in kw_elems:
                    try:
                        el_id = el.id
                    except Exception:
                        el_id = id(el)
                    if el_id in seen_ids:
                        continue
                    seen_ids.add(el_id)
                    flight_elements.append(el)
                    unique_new += 1
                logging.info(f"(Keywords) נוספו {unique_new} אלמנטים שנמצאו לפי טקסט של יעדים")
        except Exception as e:
            logging.debug(f"חיפוש לפי מילות מפתח נכשל: {e}")

        # נסיון עומק ב-Shadow DOM
        try:
            deep_total = 0
            for selector in selectors:
                deep_elements = self._find_elements_deep(selector)
                if deep_elements:
                    unique_new = 0
                    for el in deep_elements:
                        try:
                            el_id = el.id
                        except Exception:
                            el_id = id(el)
                        if el_id in seen_ids:
                            continue
                        seen_ids.add(el_id)
                        flight_elements.append(el)
                        unique_new += 1
                    deep_total += unique_new
                    logging.info(f"(Shadow DOM) נמצאו {len(deep_elements)} (חדש ייחודיים: {unique_new}) אלמנטים עם סלקטור {selector}")
            if deep_total == 0:
                logging.debug("לא נמצאו אלמנטים עמוקים ב-Shadow DOM")
        except Exception as e:
            logging.debug(f"חיפוש Shadow DOM נכשל: {e}")

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

    def _find_elements_deep(self, selector: str):
        """חיפוש בכל העץ כולל Shadow DOM והחזרת אלמנטים תואמים"""
        js = r"""
        const sel = arguments[0];
        function collect(root){
          let out = Array.from(root.querySelectorAll(sel));
          const all = root.querySelectorAll('*');
          for (const el of all){
            if (el.shadowRoot){
              out = out.concat(collect(el.shadowRoot));
            }
          }
          return out;
        }
        try { return collect(document); } catch (e) { return []; }
        """
        try:
            elems = self.driver.execute_script(js, selector)
            return elems or []
        except Exception:
            return []

    def _find_elements_by_keywords(self, keywords):
        js = r"""
        const words = arguments[0] || [];
        const results = [];
        function scan(root){
          const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null);
          let node;
          while (node = walker.nextNode()){
            try{
              const text = (node.innerText || node.textContent || '').trim();
              if (!text) continue;
              for (const w of words){
                if (w && text.includes(w)) { results.push(node); break; }
              }
            }catch(e){continue}
          }
        }
        try { scan(document); } catch(e){}
        return results;
        """
        try:
            return self.driver.execute_script(js, keywords) or []
        except Exception:
            return []

    def _collect_from_current_context(self, context_name: str = "main"):
        """איסוף טיסות מהקשר מסוים (מסמך ראשי או iframe)."""
        collected = []
        flight_elements = self.find_flight_elements()
        
        if flight_elements:
            empty_text = 0
            non_empty_text = 0
            for idx, element in enumerate(flight_elements[:150]):  # בטיחות: עד 150 אלמנטים
                flight_data = self.extract_flight_data(element)
                if flight_data and self.is_relevant_destination(flight_data.get('destination', '')):
                    collected.append(flight_data)
                elif flight_data:
                    logging.info(f"[{context_name}] טיסה לא רלוונטית לפי סינון: {flight_data.get('destination')} - מוחרג/לא מועדף")
                # סטטיסטיקת טקסט
                try:
                    txt = (element.text or '').strip()
                    if not txt:
                        empty_text += 1
                    else:
                        non_empty_text += 1
                except Exception:
                    empty_text += 1
            logging.info(f"[{context_name}] סטטוס טקסט באלמנטים: עם טקסט={non_empty_text}, ללא טקסט={empty_text}")
        
        if not collected and flight_elements:
            # דיבוג: שמירת innerHTML של כמה אלמנטים ראשונים
            try:
                for i, el in enumerate(flight_elements[:5]):
                    try:
                        html = self.driver.execute_script("return arguments[0].innerHTML;", el)
                        with open(f"element_sample_{context_name}_{i}.html", "w", encoding="utf-8") as f:
                            f.write(html or "")
                    except Exception:
                        continue
                logging.info(f"נשמרו דוגמאות אלמנטים: element_sample_{context_name}_0.html ... {context_name}_4.html")
            except Exception:
                pass

            # דיבוג: שמירת טקסט/מידע בסיסי על אלמנטים
            try:
                lines = []
                for i, el in enumerate(flight_elements[:100]):
                    try:
                        cls = el.get_attribute('class') or ''
                        tid = el.get_attribute('id') or ''
                        txt = (el.text or '').strip()
                        if not txt:
                            try:
                                txt = self.driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", el) or ''
                                txt = txt.strip()
                            except Exception:
                                txt = ''
                        snippet = txt.replace('\n',' ')[:160]
                        lines.append(f"[{i}] id={tid} class={cls} | text={len(txt)}ch | snippet={snippet}")
                    except Exception:
                        continue
                with open(f"elements_dump_{context_name}.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                logging.info(f"נשמר דוח טקסט אלמנטים: elements_dump_{context_name}.txt")
            except Exception:
                pass
        
        return collected

    def extract_from_page_text(self, page_text: str):
        """Fallback: חילוץ טיסות מתוך טקסט מלא של הדף, ללא דרישת מחיר"""
        results = []
        if not page_text:
            return results
        text = page_text
        # יעד יכול להופיע בעברית או אנגלית
        extra_cities = [
            'Berlin', 'Paris', 'London', 'Rome', 'Madrid', 'Amsterdam', 'Prague', 'Vienna', 'Barcelona', 'Milan', 'Nice', 'Lisbon',
            'Athens', 'Istanbul', 'Budapest', 'Zagreb', 'Belgrade', 'Dubai', 'New York', 'Miami', 'Los Angeles'
        ]
        candidates = list(dict.fromkeys(PREFERRED_DESTINATIONS + extra_cities))
        seen = set()
        for dest in candidates:
            try:
                if not dest:
                    continue
                if dest in EXCLUDED_DESTINATIONS:
                    continue
                if dest in text:
                    key = dest
                    if key in seen:
                        continue
                    seen.add(key)
                    results.append({
                        'destination': dest,
                        'price': None,
                        'dates': None,
                        'full_text': f'זוהה יעד בטקסט העמוד: {dest}',
                        'scraped_at': datetime.now().isoformat(),
                        'url': TUSTUS_URL
                    })
            except Exception:
                continue
        return results

    def extract_from_html(self, html: str):
        """Fallback נוסף: פרסינג HTML מלא ושאיבת יעדים ממגוון מאפיינים/טקסטים"""
        results = []
        if not html:
            return results
        try:
            soup = BeautifulSoup(html, 'lxml')
        except Exception:
            try:
                soup = BeautifulSoup(html, 'html.parser')
            except Exception:
                return results

        def add_candidate(dest: str, node_text: str):
            if not dest:
                return
            if dest in EXCLUDED_DESTINATIONS:
                return
            results.append({
                'destination': dest,
                'price': None,
                'dates': None,
                'full_text': (node_text or '')[:500],
                'scraped_at': datetime.now().isoformat(),
                'url': TUSTUS_URL
            })

        # חיפוש לפי טקסט
        all_text = soup.get_text("\n", strip=True)
        for dest in set(PREFERRED_DESTINATIONS):
            if dest and dest in all_text and dest not in EXCLUDED_DESTINATIONS:
                add_candidate(dest, f"יעד מתוך HTML-טקסט: {dest}")

        # חיפוש לפי מאפיינים נפוצים
        attrs = ['title', 'alt', 'aria-label', 'data-destination', 'data-title']
        for tag in soup.find_all(True):
            # עצירה מוקדמת להיגיינה
            if len(results) > 100:
                break
            try:
                txt = (tag.get_text(" ", strip=True) or '')
                for dest in PREFERRED_DESTINATIONS:
                    if dest and dest in txt and dest not in EXCLUDED_DESTINATIONS:
                        add_candidate(dest, txt)
                        break
                for a in attrs:
                    val = tag.get(a)
                    if val:
                        for dest in PREFERRED_DESTINATIONS:
                            if dest and dest in val and dest not in EXCLUDED_DESTINATIONS:
                                add_candidate(dest, f"{a}={val}")
                                break
            except Exception:
                continue

        # ייחודיות
        unique = []
        seen = set()
        for f in results:
            key = (f['destination'], f['full_text'][:80])
            if key in seen:
                continue
            seen.add(key)
            unique.append(f)
        return unique

    def _try_open_last_minute_sections(self):
        """ניסיון ללחוץ על קישורים/כפתורים שמובילים לחלקי 'רגע אחרון'/מבצעים"""
        try:
            candidates = [
                "//a[contains(., 'רגע') and contains(., 'אחרון')]",
                "//button[contains(., 'רגע') and contains(., 'אחרון')]",
                "//a[contains(., 'מבצע') or contains(., 'מבצעים') or contains(., 'דילים')]",
                "//button[contains(., 'מבצע') or contains(., 'מבצעים') or contains(., 'דילים')]",
                "//a[contains(., 'טיסות')]",
                "//button[contains(., 'טיסות')]",
                "//a[contains(., 'חבילות')]",
                "//button[contains(., 'חבילות')]",
            ]
            clicked = 0
            for xp in candidates:
                try:
                    elems = self.driver.find_elements(By.XPATH, xp)
                    for el in elems[:2]:
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                            time.sleep(0.3)
                            el.click()
                            logging.info(f"נלחץ קישור/כפתור ניווט: {xp}")
                            time.sleep(2)
                            clicked += 1
                            if clicked >= 2:
                                return
                        except Exception:
                            continue
                except Exception:
                    continue
        except Exception:
            pass

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
            
            if destination:
                if price is not None:
                    logging.info(f"✅ טיסה נמצאה: {destination} - {price}₪")
                else:
                    logging.info(f"✅ טיסה נמצאה ללא מחיר: {destination}")
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
        cities_keywords = [
            'ברלין', 'פריז', 'לונדון', 'רומא', 'מדריד', 'אמסטרדם', 'פראג', 'ויאנה', 'ברצלונה', 'מילאנו', 'ניס', 'ליסבון',
            # אנגלית
            'Berlin', 'Paris', 'London', 'Rome', 'Madrid', 'Amsterdam', 'Prague', 'Vienna', 'Barcelona', 'Milan', 'Nice', 'Lisbon',
            'Athens', 'Istanbul', 'Budapest', 'Zagreb', 'Belgrade'
        ]
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
        # מספרים עם מפרידי אלפים (2-4 ספרות או 1-3 עם מפרידים 3 ספרות)
        num = r'(\d{1,3}(?:[.,\u00A0]\d{3})+|\d{2,4})'
        price_patterns = [
            rf'{num}\s*₪',
            rf'{num}\s*שח',
            rf'₪\s*{num}',
            rf'שח\s*{num}',
            rf'{num}\s*שקל',
            rf'מ\s*{num}',
            rf'החל\s*מ\s*{num}'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    numeric = match.group(1)
                    numeric = numeric.replace(',', '').replace('.', '').replace('\u00A0', '')
                    return int(numeric)
                except Exception:
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

    def _try_close_modals(self):
        """ניסיון לסגור דיאלוגים/מודלים אחרי הקלקות"""
        try:
            xpaths = [
                "//button[contains(., 'סגור') or contains(., 'Close') or contains(., 'X')]",
                "//div[contains(@class,'close') or contains(@class,'modal-close')]",
            ]
            for xp in xpaths:
                try:
                    for el in self.driver.find_elements(By.XPATH, xp)[:3]:
                        try:
                            self.driver.execute_script("arguments[0].click();", el)
                            time.sleep(0.3)
                        except Exception:
                            continue
                except Exception:
                    continue
        except Exception:
            pass

    def _try_click_expand_and_extract(self, limit_clicks: int = 12):
        """ניסיונות הקלקה על כרטיסים/אלמנטים כדי לחשוף טקסט, ואז חילוץ מטקסט העמוד."""
        results = []
        try:
            # בחר אלמנטים מועמדים להקלקה
            candidates = []
            for sel in ["[class*='flight']", "[class*='item']", "[class*='result']", "a", "button"]:
                try:
                    elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    candidates.extend(elems[:50])
                except Exception:
                    continue
            # הסר כפילויות
            seen = set()
            dedup = []
            for el in candidates:
                try:
                    el_id = el.id
                except Exception:
                    el_id = id(el)
                if el_id in seen:
                    continue
                seen.add(el_id)
                dedup.append(el)

            clicks = 0
            for el in dedup:
                if clicks >= limit_clicks:
                    break
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    time.sleep(0.2)
                    self.driver.execute_script("try{arguments[0].click();}catch(e){}", el)
                    clicks += 1
                    time.sleep(1.0)
                    # אחרי הקלקה: נסה חילוץ מטקסט הדף
                    page_text = self.driver.execute_script("return document.body.innerText || document.body.textContent || '';") or ""
                    extracted = self.extract_from_page_text(page_text)
                    # הוסף רק חדשים
                    for f in extracted:
                        key = (f['destination'], f.get('full_text'))
                        if key not in {(r['destination'], r.get('full_text')) for r in results}:
                            results.append(f)
                    # נסה לסגור מודלים כדי להמשיך
                    self._try_close_modals()
                except Exception:
                    continue
        except Exception:
            pass
        return results

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