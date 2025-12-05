"""🤖 Telegram Bot - Polling Mode (Sürekli çalışır)"""
import os
import time
import requests
from telegram_btc_bot import StrongBuyAnalyzer
import threading

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = 8391537149
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

class TelegramPollingBot:
    def __init__(self):
        self.offset = 0
        self.analyzer = StrongBuyAnalyzer()
    
    def get_updates(self):
        """Telegram'dan mesaj al"""
        try:
            url = f"{BASE_URL}/getUpdates"
            params = {'offset': self.offset, 'timeout': 30}
            resp = requests.get(url, params=params, timeout=35)
            
            if resp.status_code == 200:
                return resp.json().get('result', [])
            return []
        except:
            return []
    
    def handle_btc_command(self):
        """/ btc komutu işle"""
        data = self.analyzer.get_strong_recommendations()
        message = self.analyzer.format_telegram_message(data)
        
        url = f"{BASE_URL}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=10)
            return resp.status_code == 200
        except:
            return False
    
    def start_polling(self):
        """Polling başlat"""
        print("🤖 Telegram Bot polling başlıyor...")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        msg = update['message']
                        text = msg.get('text', '').strip()
                        
                        if text == '/btc':
                            print("🔥 /btc komutu!")
                            self.handle_btc_command()
                
                time.sleep(1)
            
            except Exception as e:
                print(f"⚠️ Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = TelegramPollingBot()
    
    # Send test message
    print("📤 Test mesajı gönderiliyor...")
    data = bot.analyzer.get_strong_recommendations()
    msg = bot.analyzer.format_telegram_message(data)
    
    url = f"{BASE_URL}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': f"🤖 Bot aktif! /btc yazın\n\n{msg}",
        'parse_mode': 'Markdown'
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print("✅ Telegram'a gönderildi!")
        else:
            print(f"❌ Error: {resp.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Start polling
    # bot.start_polling()

