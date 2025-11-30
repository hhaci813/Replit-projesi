"""Broker Kimlik Doğrulama Sistemi"""
import json
import os
from datetime import datetime

class BrokerAuth:
    def __init__(self):
        self.users_file = "broker_kullanicilar.json"
        self.current_user = None
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Dosya kontrol et"""
        if not os.path.exists(self.users_file):
            self.init_users()
    
    def init_users(self):
        """Başlangıç kullanıcısı oluştur"""
        users = {
            "demo": {
                "password": "1234",
                "alpaca_keys": {"api_key": "DEMO", "secret": "DEMO"},
                "binance_keys": {"api_key": "DEMO", "secret": "DEMO"},
                "created": datetime.now().isoformat()
            }
        }
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def register(self, username, password):
        """Yeni kullanıcı kaydı"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            if username in users:
                return False, "❌ Kullanıcı adı zaten var"
            
            users[username] = {
                "password": password,
                "alpaca_keys": {"api_key": "", "secret": ""},
                "binance_keys": {"api_key": "", "secret": ""},
                "created": datetime.now().isoformat()
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            return True, f"✅ Kullanıcı '{username}' oluşturuldu"
        except Exception as e:
            return False, f"❌ Kayıt hatası: {str(e)}"
    
    def login(self, username, password):
        """Giriş"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            if username not in users:
                return False, "❌ Kullanıcı bulunamadı"
            
            if users[username]['password'] != password:
                return False, "❌ Şifre yanlış"
            
            self.current_user = username
            return True, f"✅ Hoşgeldin {username}!"
        except Exception as e:
            return False, f"❌ Giriş hatası: {str(e)}"
    
    def set_api_keys(self, broker, api_key, secret):
        """API key'leri kaydet"""
        if not self.current_user:
            return False, "❌ Giriş yapmalısınız"
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            if broker.lower() == "alpaca":
                users[self.current_user]["alpaca_keys"]["api_key"] = api_key
                users[self.current_user]["alpaca_keys"]["secret"] = secret
            else:
                users[self.current_user]["binance_keys"]["api_key"] = api_key
                users[self.current_user]["binance_keys"]["secret"] = secret
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            return True, f"✅ {broker} API key'leri kaydedildi"
        except Exception as e:
            return False, f"❌ Hata: {str(e)}"

if __name__ == "__main__":
    auth = BrokerAuth()
    print("✅ Broker Auth Sistemi Hazır")
