"""
ALARM SİSTEMİ - Fiyat Hedefi ve Stop Loss Bildirimleri
Kripto fiyatları hedef veya stop loss'a ulaşınca anında Telegram bildirimi
"""

import os
import json
import requests
import threading
import time
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ALERTS_FILE = "active_alerts.json"

class PriceAlertSystem:
    def __init__(self):
        self.alerts = self.load_alerts()
        self.running = False
        self.check_interval = 60  # 1 dakikada bir kontrol
        
    def load_alerts(self):
        """Kayıtlı alarmları yükle"""
        try:
            if os.path.exists(ALERTS_FILE):
                with open(ALERTS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"price_alerts": [], "triggered_alerts": []}
    
    def save_alerts(self):
        """Alarmları kaydet"""
        with open(ALERTS_FILE, 'w') as f:
            json.dump(self.alerts, f, indent=2, default=str)
    
    def add_alert(self, symbol: str, target_price: float, stop_loss: float, 
                  entry_price: float, alert_type: str = "both"):
        """Yeni alarm ekle"""
        alert = {
            "id": len(self.alerts["price_alerts"]) + 1,
            "symbol": symbol.upper(),
            "entry_price": entry_price,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "alert_type": alert_type,  # "target", "stoploss", "both"
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.alerts["price_alerts"].append(alert)
        self.save_alerts()
        return alert
    
    def remove_alert(self, alert_id: int):
        """Alarm sil"""
        self.alerts["price_alerts"] = [
            a for a in self.alerts["price_alerts"] 
            if a.get("id") != alert_id
        ]
        self.save_alerts()
    
    def get_active_alerts(self):
        """Aktif alarmları getir"""
        return [a for a in self.alerts["price_alerts"] if a.get("status") == "active"]
    
    def get_current_price(self, symbol: str) -> float:
        """BTCTurk'ten güncel fiyat al"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            data = resp.json().get('data', [])
            
            for ticker in data:
                pair = ticker.get('pairNormalized', '')
                if pair == f"{symbol}_USDT":
                    return float(ticker.get('last', 0))
            return 0
        except:
            return 0
    
    def check_alerts(self):
        """Tüm alarmları kontrol et"""
        active_alerts = self.get_active_alerts()
        triggered = []
        
        for alert in active_alerts:
            symbol = alert["symbol"]
            current_price = self.get_current_price(symbol)
            
            if current_price <= 0:
                continue
            
            target = alert["target_price"]
            stop = alert["stop_loss"]
            entry = alert["entry_price"]
            
            # HEDEF FİYAT KONTROLÜ
            if current_price >= target:
                profit_pct = ((current_price - entry) / entry) * 100
                self.trigger_alert(alert, "TARGET_HIT", current_price, profit_pct)
                alert["status"] = "triggered"
                triggered.append(alert)
            
            # STOP LOSS KONTROLÜ
            elif current_price <= stop:
                loss_pct = ((current_price - entry) / entry) * 100
                self.trigger_alert(alert, "STOP_LOSS", current_price, loss_pct)
                alert["status"] = "triggered"
                triggered.append(alert)
        
        if triggered:
            self.save_alerts()
        
        return triggered
    
    def trigger_alert(self, alert: dict, alert_type: str, current_price: float, pnl_pct: float):
        """Alarm tetikle ve Telegram'a gönder"""
        symbol = alert["symbol"]
        
        if alert_type == "TARGET_HIT":
            emoji = "🎯✅"
            title = "HEDEF FİYAT ULAŞILDI!"
            color = "🟢"
            action = "KAR AL!"
        else:
            emoji = "🛑⚠️"
            title = "STOP LOSS TETİKLENDİ!"
            color = "🔴"
            action = "ÇIKIŞ YAP!"
        
        message = f"""
{emoji} <b>{title}</b>

🪙 <b>{symbol}</b>
{color} Durum: {alert_type}

💰 Giriş: ${alert['entry_price']:.6f}
📊 Şimdi: ${current_price:.6f}
🎯 Hedef: ${alert['target_price']:.6f}
🛑 Stop: ${alert['stop_loss']:.6f}

💹 <b>Kar/Zarar: {pnl_pct:+.2f}%</b>

⚡ <b>AKSİYON: {action}</b>

🤖 <i>Alarm Sistemi - Akıllı Yatırım Asistanı</i>
"""
        
        self.send_telegram(message)
        
        # Tetiklenen alarmları kaydet
        triggered_record = {
            **alert,
            "triggered_at": datetime.now().isoformat(),
            "trigger_type": alert_type,
            "trigger_price": current_price,
            "pnl_percent": pnl_pct
        }
        self.alerts["triggered_alerts"].append(triggered_record)
    
    def send_telegram(self, message: str):
        """Telegram'a mesaj gönder"""
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': message,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
        except Exception as e:
            print(f"Telegram hatası: {e}")
    
    def start_monitoring(self):
        """Arka planda alarm izleme başlat"""
        def monitor_loop():
            self.running = True
            while self.running:
                try:
                    self.check_alerts()
                except Exception as e:
                    print(f"Alarm kontrol hatası: {e}")
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        print("🔔 Alarm sistemi başlatıldı!")
    
    def stop_monitoring(self):
        """İzlemeyi durdur"""
        self.running = False
    
    def get_stats(self):
        """Alarm istatistikleri"""
        active = len(self.get_active_alerts())
        triggered = len(self.alerts.get("triggered_alerts", []))
        
        # Başarı oranı
        wins = sum(1 for t in self.alerts.get("triggered_alerts", []) 
                   if t.get("trigger_type") == "TARGET_HIT")
        losses = sum(1 for t in self.alerts.get("triggered_alerts", []) 
                     if t.get("trigger_type") == "STOP_LOSS")
        
        success_rate = (wins / triggered * 100) if triggered > 0 else 0
        
        return {
            "active_alerts": active,
            "triggered_total": triggered,
            "wins": wins,
            "losses": losses,
            "success_rate": success_rate
        }


# Auto-add alerts from recommendations
def auto_create_alerts_from_recommendations(recommendations: list):
    """Önerilerden otomatik alarm oluştur"""
    alert_system = PriceAlertSystem()
    
    for rec in recommendations:
        if rec.get('action') in ['STRONG_BUY', 'BUY']:
            alert_system.add_alert(
                symbol=rec['symbol'],
                target_price=rec.get('target_price', rec['price'] * 1.25),
                stop_loss=rec.get('stop_loss', rec['price'] * 0.92),
                entry_price=rec['price']
            )
    
    return alert_system.get_active_alerts()


if __name__ == "__main__":
    # Test
    system = PriceAlertSystem()
    
    # Örnek alarm ekle
    system.add_alert("SPELL", 0.00035, 0.00024, 0.000266)
    system.add_alert("CVC", 0.065, 0.045, 0.049)
    
    print(f"Aktif alarmlar: {len(system.get_active_alerts())}")
    print(system.get_stats())
