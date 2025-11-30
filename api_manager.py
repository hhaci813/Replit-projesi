"""Real API Key Yönetimi - Güvenli Depolama"""
import os
from security_system import SecurityManager

class APIKeyManager:
    def __init__(self):
        self.security = SecurityManager()
        self.keys_file = "api_keys_config.json"
    
    def set_alpaca_keys(self, api_key, secret_key):
        """Alpaca API key'lerini kaydet"""
        encrypted_key = self.security.encrypt_api_key(api_key)
        encrypted_secret = self.security.encrypt_api_key(secret_key)
        
        # Environment'a da kaydet (production için)
        os.environ['ALPACA_API_KEY'] = api_key
        os.environ['ALPACA_SECRET_KEY'] = secret_key
        
        print("✅ Alpaca API key'leri kaydedildi")
        return True
    
    def set_binance_keys(self, api_key, secret_key):
        """Binance API key'lerini kaydet"""
        encrypted_key = self.security.encrypt_api_key(api_key)
        encrypted_secret = self.security.encrypt_api_key(secret_key)
        
        # Environment'a da kaydet
        os.environ['BINANCE_API_KEY'] = api_key
        os.environ['BINANCE_SECRET_KEY'] = secret_key
        
        print("✅ Binance API key'leri kaydedildi")
        return True
    
    def get_alpaca_keys(self):
        """Alpaca key'lerini al"""
        return {
            'api_key': os.environ.get('ALPACA_API_KEY', ''),
            'secret_key': os.environ.get('ALPACA_SECRET_KEY', '')
        }
    
    def get_binance_keys(self):
        """Binance key'lerini al"""
        return {
            'api_key': os.environ.get('BINANCE_API_KEY', ''),
            'secret_key': os.environ.get('BINANCE_SECRET_KEY', '')
        }
    
    def verify_keys(self):
        """Key'leri doğrula"""
        alpaca = self.get_alpaca_keys()
        binance = self.get_binance_keys()
        
        result = "🔑 API KEY DURUŞU:\n\n"
        result += f"Alpaca: {'✅ SET' if alpaca['api_key'] else '❌ EMPTY'}\n"
        result += f"Binance: {'✅ SET' if binance['api_key'] else '❌ EMPTY'}\n"
        return result

if __name__ == "__main__":
    manager = APIKeyManager()
    print(manager.verify_keys())
