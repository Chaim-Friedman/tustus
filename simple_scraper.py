#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקרפר פשוט ללא Selenium - לשימוש כ-fallback אם יש בעיות עם Chrome
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import logging
from datetime import datetime
from config import TUSTUS_URL, PREFERRED_DESTINATIONS, EXCLUDED_DESTINATIONS

class SimpleFlightScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def scrape_flights(self):
        """סריקת טיסות באמצעות requests + BeautifulSoup בלבד"""
        try:
            logging.info(f"מתחיל סריקה פשוטה של {TUSTUS_URL}")
            
            # שליחת בקשה לאתר
            response = self.session.get(TUSTUS_URL, timeout=30)
            response.raise_for_status()
            
            # פרסור HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            flights = []
            
            # חיפוש טקסטים שמכילים מילות מפתח
            text_elements = soup.find_all(text=True)
            combined_text = ' '.join([str(elem).strip() for elem in text_elements if str(elem).strip()])
            
            # חיפוש בטקסט המקובץ
            flight_data = self.extract_flights_from_text(combined_text)
            
            # חיפוש באלמנטים ספציפיים
            selectors = [
                'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '.flight', '.trip', '.offer', '.deal', '.card', '.product'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and any(dest in text for dest in PREFERRED_DESTINATIONS):
                        flight_info = self.extract_flight_info(text)
                        if flight_info:
                            flights.append(flight_info)
            
            # הסרת כפילויות
            unique_flights = self.remove_duplicates(flights)

            # סינון יעדים מוחרגים
            unique_flights = [f for f in unique_flights if f.get('destination') not in EXCLUDED_DESTINATIONS]
            
            logging.info(f"נמצאו {len(unique_flights)} טיסות רלוונטיות (סקרפר פשוט)")
            return unique_flights
            
        except Exception as e:
            logging.error(f"שגיאה בסריקה פשוטה: {e}")
            return []
    
    def extract_flights_from_text(self, text):
        """חילוץ טיסות מטקסט מקובץ"""
        flights = []
        
        # חיפוש יעדים בטקסט
        for dest in PREFERRED_DESTINATIONS:
            if dest in text:
                # חיפוש מחיר ליד היעד
                import re
                
                # חיפוש מחיר ליד היעד
                pattern = f"{dest}.*?(\d{{1,4}})\s*(₪|שח)"
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    price_str = match.group(1)
                    try:
                        price = int(price_str)
                        if 100 <= price <= 3000:  # מחיר סביר
                            flights.append({
                                'destination': dest,
                                'price': price,
                                'dates': [],
                                'full_text': match.group(0),
                                'scraped_at': datetime.now().isoformat(),
                                'url': TUSTUS_URL,
                                'method': 'simple_scraper'
                            })
                    except ValueError:
                        continue
        
        return flights
    
    def extract_flight_info(self, text):
        """חילוץ מידע על טיסה מטקסט"""
        try:
            if len(text) < 10 or len(text) > 500:
                return None
            
            # חיפוש יעד
            destination = None
            for dest in PREFERRED_DESTINATIONS:
                if dest in text:
                    destination = dest
                    break
            
            if not destination:
                return None

            # דילוג על יעדים מוחרגים
            if destination in EXCLUDED_DESTINATIONS:
                return None
            
            # חיפוש מחיר
            import re
            price_patterns = [
                r'(\d{1,4})\s*₪',
                r'(\d{1,4})\s*שח',
                r'₪\s*(\d{1,4})',
                r'שח\s*(\d{1,4})'
            ]
            
            price = None
            for pattern in price_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        price_val = int(match.group(1))
                        if 100 <= price_val <= 3000:
                            price = price_val
                            break
                    except ValueError:
                        continue
            
            if not price:
                return None
            
            # חיפוש תאריכים
            date_patterns = [
                r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
                r'(ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)'
            ]
            
            dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                dates.extend(matches)
            
            return {
                'destination': destination,
                'price': price,
                'dates': dates[:3],  # מקסימום 3 תאריכים
                'full_text': text[:200],  # מגביל אורך
                'scraped_at': datetime.now().isoformat(),
                'url': TUSTUS_URL,
                'method': 'simple_scraper'
            }
            
        except Exception as e:
            logging.warning(f"שגיאה בחילוץ מידע: {e}")
            return None
    
    def remove_duplicates(self, flights):
        """הסרת כפילויות"""
        seen = set()
        unique_flights = []
        
        for flight in flights:
            # יצירת מפתח ייחודי
            key = f"{flight['destination']}_{flight['price']}"
            if key not in seen:
                seen.add(key)
                unique_flights.append(flight)
        
        return unique_flights

def test_simple_scraper():
    """פונקציה לבדיקת הסקרפר הפשוט"""
    scraper = SimpleFlightScraper()
    flights = scraper.scrape_flights()
    
    print(f"נמצאו {len(flights)} טיסות (סקרפר פשוט):")
    for flight in flights:
        print(f"- {flight['destination']}: {flight['price']}₪")
        print(f"  תאריכים: {flight['dates']}")
        print(f"  טקסט: {flight['full_text'][:100]}...")
        print("-" * 50)
    
    return flights

if __name__ == "__main__":
    test_simple_scraper()