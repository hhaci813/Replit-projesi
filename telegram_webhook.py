"""Telegram Webhook Handler - Mesaj alma ve gönderme"""
from flask import Flask, request, jsonify
import json
from telegram_bot import TelegramBot
from datetime import datetime

telegram_app = Flask(__name__)

# Telegram webhook ayarları
TELEGRAM_WEBHOOK_PATH = "/telegram-webhook"
TELEGRAM_CHAT_ID = 8391537149  # Kullanıcı Chat ID

@telegram_app.route(TELEGRAM_WEBHOOK_PATH, methods=['POST'])
def telegram_webhook():
    """Telegram'dan gelen mesajları işle"""
    try:
        update = request.json
        
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            print(f"📨 Telegram Mesajı: {text}")
            print(f"   Chat ID: {chat_id}")
            
            # Komutları işle
            if text == "/tavsiye":
                tavsiye = "💼 Bugünün Tavsiyesi:\n\n60% Hisse, 30% Teknoloji, 10% Kripto\n\nAL: AAPL, MSFT, GOOGL\nTUT: TSLA, AMZN"
                return jsonify({"status": "ok"})
            
            elif text == "/portfoy":
                portfoy_msg = "📊 Portföy Durumuobanız..."
                return jsonify({"status": "ok"})
            
            elif text == "/start":
                welcome = """
🤖 AKILLI YATIRIM ASİSTANI'NA HOŞ GELDİNİZ!

Komutlar:
/tavsiye - Günlük tavsiye
/portfoy - Portföy durumu
/uyari - Uyarılar
/help - Yardım
                """
                return jsonify({"status": "ok"})
        
        return jsonify({"status": "ok"})
    
    except Exception as e:
        print(f"Webhook hatası: {e}")
        return jsonify({"status": "error", "message": str(e)})

def telegram_mesaj_gonder(bot_token, chat_id, mesaj):
    """Telegram'a mesaj gönder"""
    bot = TelegramBot(bot_token)
    return bot.tavsiye_gonder(chat_id, mesaj)

if __name__ == "__main__":
    telegram_app.run(port=8888, debug=False)
