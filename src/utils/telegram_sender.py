"""Telegram gönderici"""
import os
import requests

def send_to_telegram(message):
    """Telegram'a gönder"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        return False
    
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={'chat_id': 8391537149, 'text': message, 'parse_mode': 'Markdown'},
            timeout=10
        )
        return resp.status_code == 200
    except:
        return False

