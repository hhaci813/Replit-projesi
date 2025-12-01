"""ADA Prediction Tracking - 7 Günlük İzleme"""
import json
from datetime import datetime, timedelta
import requests
import yfinance as yf

class ADAPredictionTracker:
    def __init__(self):
        self.prediction = {
            'start_date': datetime.now().isoformat(),
            'start_price': 0.39,
            'target_price': 0.42,
            'expected_change': 8.9,
            'confidence': 75,
            'timeframe_days': 7,
            'daily_tracking': []
        }
    
    def get_current_ada_price(self):
        """ADA canlı fiyatı al"""
        try:
            # USD fiyat
            ticker = yf.Ticker("ADA-USD")
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                return price
        except:
            pass
        
        try:
            # TRY fiyat (BTCTurk)
            resp = requests.get("https://api.btcturk.com/api/v2/ticker?pairSymbol=ADATRY", timeout=5)
            if resp.status_code == 200:
                price_try = float(resp.json()['data'][0]['last'])
                return price_try / 42  # Yaklaşık USD
        except:
            pass
        
        return None
    
    def track_daily(self):
        """Günlük izleme yap"""
        current_price = self.get_current_ada_price()
        
        if not current_price:
            return None
        
        # Hesapla
        start = self.prediction['start_price']
        change_pct = ((current_price - start) / start * 100)
        days_elapsed = len(self.prediction['daily_tracking']) + 1
        
        # Kayıt
        entry = {
            'day': days_elapsed,
            'date': datetime.now().isoformat(),
            'price': current_price,
            'change_from_start': change_pct,
            'vs_target': current_price - self.prediction['target_price']
        }
        
        self.prediction['daily_tracking'].append(entry)
        
        return entry
    
    def get_accuracy(self):
        """Tahminin doğruluğunu hesapla"""
        if not self.prediction['daily_tracking']:
            return None
        
        latest = self.prediction['daily_tracking'][-1]
        days_elapsed = latest['day']
        current_price = latest['price']
        
        # Doğruluk hesaplaması
        expected_at_today = self.prediction['start_price'] + (
            (self.prediction['target_price'] - self.prediction['start_price']) 
            * (days_elapsed / self.prediction['timeframe_days'])
        )
        
        accuracy = (1 - abs(current_price - expected_at_today) / expected_at_today) * 100
        
        return {
            'days_elapsed': days_elapsed,
            'expected_price': expected_at_today,
            'actual_price': current_price,
            'accuracy_pct': max(0, accuracy),
            'on_track': current_price >= (expected_at_today * 0.95)  # %95 tolerance
        }
    
    def generate_report(self):
        """Rapor oluştur"""
        accuracy = self.get_accuracy()
        
        if not accuracy:
            return "Henüz veri yok"
        
        report = f"""
📊 ADA PREDICTION TRACKING - GÜN {accuracy['days_elapsed']}/7

🎯 HEDEF:
   • Başlangıç: ${self.prediction['start_price']:.4f}
   • Hedef: ${self.prediction['target_price']:.4f}
   • Beklenen: +{self.prediction['expected_change']:.1f}%

📈 GERÇEKLEŞEN:
   • Mevcut: ${accuracy['actual_price']:.4f}
   • Değişim: {((accuracy['actual_price'] - self.prediction['start_price']) / self.prediction['start_price'] * 100):+.2f}%

✅ DOĞRULUK:
   • Beklenen: ${accuracy['expected_price']:.4f}
   • Gerçek: ${accuracy['actual_price']:.4f}
   • Tahmin Doğruluğu: {accuracy['accuracy_pct']:.1f}%
   • Yolda Mı: {'🟢 EVET' if accuracy['on_track'] else '🔴 HAYIR'}

⏰ Zaman: Gün {accuracy['days_elapsed']}/{self.prediction['timeframe_days']}
"""
        return report
    
    def save_tracking(self):
        """Verileri kaydet"""
        with open('ada_tracking_data.json', 'w') as f:
            json.dump(self.prediction, f, indent=2)
    
    def load_tracking(self):
        """Verileri yükle"""
        try:
            with open('ada_tracking_data.json', 'r') as f:
                self.prediction = json.load(f)
        except:
            pass

# Test
if __name__ == "__main__":
    tracker = ADAPredictionTracker()
    tracker.load_tracking()
    
    # Track
    entry = tracker.track_daily()
    if entry:
        print(f"✅ Gün {entry['day']} takip edildi")
    
    # Report
    print(tracker.generate_report())
    
    # Save
    tracker.save_tracking()
    print("✅ Veri kaydedildi")
