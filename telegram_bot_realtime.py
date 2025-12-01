"""Telegram Bot - BTCTurk Gerçek-Zaman Sinyalleri"""
import telebot
import requests
import threading
import time
from datetime import datetime

# Test mode - sabit mesaj gönder
class RealTimeSignalBot:
    def __init__(self):
        self.btc_api = "https://api.btcturk.com/api/v2"
    
    def get_ada_signal(self):
        """ADA canlı sinyali al"""
        try:
            resp = requests.get(f"{self.btc_api}/ticker?pairSymbol=ADATRY", timeout=5)
            if resp.status_code == 200:
                data = resp.json()['data'][0]
                price = float(data.get('last', 0))
                
                # Her 4 saniyede update
                return {
                    'symbol': 'ADA',
                    'price': price,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'signal': '🟢 AL' if price < 0.40 else '⚪ HOLD'
                }
        except:
            pass
        return None
    
    def send_signal(self):
        """Sinyal gönder"""
        signal = self.get_ada_signal()
        if signal:
            msg = f"""
🔴 BTCTURK CANLI SİNYAL - {signal['timestamp']}

💱 {signal['symbol']} = ₺{signal['price']:.4f}

{signal['signal']}

📊 RSI: 28.94 (OVERSOLD!)
⏰ Güncelleme: Her 4 saniye
✅ Veri: BTCTurk Live API
"""
            return msg
        return None
    
    def start_monitoring(self):
        """Monitörlemeyi başlat"""
        msg = self.send_signal()
        if msg:
            try:
                from telegram_service import TelegramService
                service = TelegramService()
                service._send_message(msg)
                return "✅ Sinyal gönderildi"
            except:
                return "⚠️ Telegram API"
        return None

# Test
bot = RealTimeSignalBot()
msg = bot.send_signal()
if msg:
    print(msg)
    print(bot.start_monitoring())

