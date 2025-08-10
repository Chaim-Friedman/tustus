import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Set
from flight_scraper import FlightScraper
from config import DATA_FILE

class FlightMonitor:
    def __init__(self):
        self.data_file = DATA_FILE
        self.previous_flights = self.load_previous_flights()
        
    def load_previous_flights(self) -> Dict:
        """טעינת נתוני טיסות קודמים מקובץ"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logging.info(f"נטענו נתוני {len(data.get('flights', []))} טיסות קודמות")
                    return data
            except Exception as e:
                logging.error(f"שגיאה בטעינת נתונים קודמים: {e}")
        
        return {'flights': [], 'last_check': None}
    
    def save_flights_data(self, flights: List[Dict], new_flights: List[Dict]):
        """שמירת נתוני טיסות לקובץ"""
        data = {
            'flights': flights,
            'new_flights': new_flights,
            'last_check': datetime.now().isoformat(),
            'total_flights_found': len(flights),
            'new_flights_count': len(new_flights)
        }
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"נשמרו נתוני {len(flights)} טיסות לקובץ")
        except Exception as e:
            logging.error(f"שגיאה בשמירת נתונים: {e}")
    
    def create_flight_signature(self, flight: Dict) -> str:
        """יצירת חתימה ייחודית לטיסה"""
        # יצירת מזהה ייחודי על בסיס יעד, מחיר וטקסט
        destination = flight.get('destination', '')
        price = flight.get('price', 0)
        text_hash = hash(flight.get('full_text', ''))
        
        return f"{destination}_{price}_{abs(text_hash)}"
    
    def find_new_flights(self, current_flights: List[Dict]) -> List[Dict]:
        """זיהוי טיסות חדשות"""
        # יצירת סט של חתימות טיסות קודמות
        previous_signatures = set()
        for flight in self.previous_flights.get('flights', []):
            signature = self.create_flight_signature(flight)
            previous_signatures.add(signature)
        
        # חיפוש טיסות חדשות
        new_flights = []
        for flight in current_flights:
            signature = self.create_flight_signature(flight)
            if signature not in previous_signatures:
                new_flights.append(flight)
                logging.info(f"טיסה חדשה נמצאה: {flight['destination']} - {flight['price']}₪")
        
        return new_flights
    
    def find_price_changes(self, current_flights: List[Dict]) -> List[Dict]:
        """זיהוי שינויי מחירים"""
        price_changes = []
        
        # יצירת מיפוי של טיסות קודמות לפי יעד
        previous_by_destination = {}
        for flight in self.previous_flights.get('flights', []):
            dest = flight.get('destination')
            if dest:
                if dest not in previous_by_destination:
                    previous_by_destination[dest] = []
                previous_by_destination[dest].append(flight)
        
        # בדיקת שינויי מחירים
        for current_flight in current_flights:
            dest = current_flight.get('destination')
            current_price = current_flight.get('price')
            
            if dest in previous_by_destination and current_price:
                # חיפוש המחיר הנמוך ביותר הקודם ליעד זה
                previous_prices = [f.get('price') for f in previous_by_destination[dest] if f.get('price')]
                if previous_prices:
                    min_previous_price = min(previous_prices)
                    
                    # אם המחיר הנוכחי נמוך יותר ב-50 שקל או יותר
                    if current_price < min_previous_price - 50:
                        price_change = {
                            'destination': dest,
                            'previous_price': min_previous_price,
                            'current_price': current_price,
                            'discount': min_previous_price - current_price,
                            'flight_data': current_flight
                        }
                        price_changes.append(price_change)
                        logging.info(f"ירידת מחיר ל{dest}: {min_previous_price}₪ -> {current_price}₪")
        
        return price_changes
    
    def filter_relevant_flights(self, flights: List[Dict]) -> List[Dict]:
        """סינון טיסות רלוונטיות לפי קריטריונים"""
        relevant_flights = []
        
        for flight in flights:
            # בדיקת מחיר מקסימלי
            price = flight.get('price', 0)
            if price > 2000:  # מחיר מקסימלי 2000 שקל
                continue
            
            # בדיקה שיש יעד ומחיר
            if not flight.get('destination') or not price:
                continue
            
            # בדיקת תוקף (לא ישן מדי)
            scraped_at = flight.get('scraped_at')
            if scraped_at:
                try:
                    scraped_time = datetime.fromisoformat(scraped_at)
                    if datetime.now() - scraped_time > timedelta(hours=24):
                        continue
                except:
                    pass
            
            relevant_flights.append(flight)
        
        return relevant_flights
    
    def check_for_updates(self) -> Dict:
        """בדיקה עיקרית לעדכונים"""
        logging.info("מתחיל בדיקת עדכונים")
        
        scraper = FlightScraper()
        try:
            # סריקת טיסות נוכחיות
            current_flights = scraper.scrape_flights()
            
            # סינון טיסות רלוונטיות
            relevant_flights = self.filter_relevant_flights(current_flights)
            
            # זיהוי טיסות חדשות
            new_flights = self.find_new_flights(relevant_flights)
            
            # זיהוי שינויי מחירים
            price_changes = self.find_price_changes(relevant_flights)
            
            # שמירת נתונים
            self.save_flights_data(relevant_flights, new_flights)
            
            # עדכון נתונים פנימיים
            self.previous_flights = {
                'flights': relevant_flights,
                'last_check': datetime.now().isoformat()
            }
            
            result = {
                'total_flights': len(relevant_flights),
                'new_flights': new_flights,
                'price_changes': price_changes,
                'check_time': datetime.now().isoformat()
            }
            
            logging.info(f"בדיקה הושלמה: {len(relevant_flights)} טיסות, {len(new_flights)} חדשות, {len(price_changes)} שינויי מחיר")
            return result
            
        except Exception as e:
            logging.error(f"שגיאה בבדיקת עדכונים: {e}")
            return {
                'total_flights': 0,
                'new_flights': [],
                'price_changes': [],
                'error': str(e),
                'check_time': datetime.now().isoformat()
            }
        finally:
            scraper.close()
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות"""
        stats = {
            'total_flights_tracked': len(self.previous_flights.get('flights', [])),
            'last_check': self.previous_flights.get('last_check'),
            'destinations_found': set(),
            'price_range': {'min': None, 'max': None},
            'average_price': 0
        }
        
        flights = self.previous_flights.get('flights', [])
        if flights:
            prices = [f.get('price', 0) for f in flights if f.get('price')]
            destinations = [f.get('destination') for f in flights if f.get('destination')]
            
            if prices:
                stats['price_range']['min'] = min(prices)
                stats['price_range']['max'] = max(prices)
                stats['average_price'] = sum(prices) / len(prices)
            
            stats['destinations_found'] = set(destinations)
        
        return stats

def test_monitor():
    """פונקציה לבדיקת המוניטור"""
    monitor = FlightMonitor()
    
    # הצגת סטטיסטיקות נוכחיות
    stats = monitor.get_statistics()
    print("סטטיסטיקות נוכחיות:")
    print(f"- טיסות במעקב: {stats['total_flights_tracked']}")
    print(f"- יעדים: {', '.join(stats['destinations_found']) if stats['destinations_found'] else 'אין'}")
    print(f"- טווח מחירים: {stats['price_range']['min']}-{stats['price_range']['max']}₪")
    print(f"- בדיקה אחרונה: {stats['last_check']}")
    print("-" * 50)
    
    # בדיקת עדכונים
    result = monitor.check_for_updates()
    
    print(f"תוצאות בדיקה:")
    print(f"- סה\"כ טיסות: {result['total_flights']}")
    print(f"- טיסות חדשות: {len(result['new_flights'])}")
    print(f"- שינויי מחיר: {len(result['price_changes'])}")
    
    if result['new_flights']:
        print("\nטיסות חדשות:")
        for flight in result['new_flights']:
            print(f"- {flight['destination']}: {flight['price']}₪")
    
    if result['price_changes']:
        print("\nשינויי מחיר:")
        for change in result['price_changes']:
            print(f"- {change['destination']}: {change['previous_price']}₪ -> {change['current_price']}₪ (הנחה: {change['discount']}₪)")

if __name__ == "__main__":
    test_monitor()