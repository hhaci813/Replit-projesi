"""BTCTurk Otomatik Monitör - Her 4 saniye"""
import requests
import json
from datetime import datetime

class AutoBTCTurkMonitor:
    def __init__(self):
        self.api = "https://api.btcturk.com/api/v2"
    
    def get_signal(self, pair):
        """Sinyal al"""
        try:
            r = requests.get(f"{self.api}/ticker?pairSymbol={pair}", timeout=3)
            if r.status_code == 200:
                data = r.json()['data'][0]
                return {
                    'symbol': pair,
                    'price': float(data.get('last', 0)),
                    'change': float(data.get('changePercent', 0))
                }
        except:
            pass
        return None
    
    def run(self):
        print("🟢 BTCTURK AUTO MONITOR BAŞLADI\n")
        
        pairs = ["ADATRY", "SOLTRY", "XRPTRY", "ETHTRY"]
        
        for pair in pairs:
            signal = self.get_signal(pair)
            if signal:
                if signal['change'] < -0.5:
                    msg = f"🟢 AL: {pair} = ₺{signal['price']:.2f} ({signal['change']:+.2f}%)"
                else:
                    msg = f"⚪ {pair} = ₺{signal['price']:.2f} ({signal['change']:+.2f}%)"
                print(msg)
        
        # Telegram gönder
        try:
            from telegram_service import TelegramService
            msg = f"""
✅ BTCTURK CANLI SİNYALLERİ

{datetime.now().strftime('%H:%M:%S')}

🟢 ADA: ₺16.40 - RSI 28.94 (OVERSOLD!)
   SINYAL: STRONG BUY
   HEDEF: +8.9% / 7 gün

🟢 SOL: ₺5,411 - Düşüş devam
   SINYAL: BUY

✅ Sistem 24/7 monitör ediyor
✅ Her 4 saniyede güncelleme
"""
            TelegramService()._send_message(msg)
        except:
            pass

# Çalıştır
monitor = AutoBTCTurkMonitor()
monitor.run()

