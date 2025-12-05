"""Telegram Service - Token-based messaging"""
import os
import requests

class TelegramService:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = 8391537149
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
    
    def test_connection(self):
        if not self.token:
            return False, "Token not set"
        try:
            resp = requests.get(f"{self.base_url}/getMe", timeout=5)
            if resp.status_code == 200:
                return True, f"Connected: {resp.json()['result']['username']}"
            return False, f"Error: {resp.status_code}"
        except Exception as e:
            return False, str(e)
    
    def _send_message(self, message):
        if not self.base_url:
            return False
        try:
            resp = requests.post(
                f"{self.base_url}/sendMessage",
                json={'chat_id': self.chat_id, 'text': message, 'parse_mode': 'Markdown'},
                timeout=10
            )
            return resp.status_code == 200
        except:
            return False

