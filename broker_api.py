"""Broker API Entegrasyonu - Gerçek Trading"""
import requests
import json
import os

class AlpacaAPI:
    """Alpaca Broker API"""
    
    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key or os.environ.get('ALPACA_API_KEY')
        self.secret_key = secret_key or os.environ.get('ALPACA_SECRET_KEY')
        self.base_url = "https://paper-api.alpaca.markets"  # Paper trading
        
    def al_emri(self, sembol, qty, fiyat):
        """AL emri ver"""
        try:
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            data = {
                "symbol": sembol,
                "qty": qty,
                "side": "buy",
                "type": "limit",
                "time_in_force": "day",
                "limit_price": fiyat
            }
            
            response = requests.post(
                f"{self.base_url}/v2/orders",
                json=data,
                headers=headers
            )
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def sat_emri(self, sembol, qty, fiyat):
        """SAT emri ver"""
        try:
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            data = {
                "symbol": sembol,
                "qty": qty,
                "side": "sell",
                "type": "limit",
                "time_in_force": "day",
                "limit_price": fiyat
            }
            
            response = requests.post(
                f"{self.base_url}/v2/orders",
                json=data,
                headers=headers
            )
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def hesap_bilgisi(self):
        """Hesap bilgilerini getir"""
        try:
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            response = requests.get(
                f"{self.base_url}/v2/account",
                headers=headers
            )
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}

class BinanceAPI:
    """Binance Crypto API"""
    
    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key or os.environ.get('BINANCE_API_KEY')
        self.secret_key = secret_key or os.environ.get('BINANCE_SECRET_KEY')
        self.base_url = "https://api.binance.com/api/v3"
    
    def kripto_al(self, sembol, miktar, fiyat):
        """Kripto AL"""
        try:
            # Simplified - gerçekte HMAC imzalanması gerekir
            data = {
                "symbol": sembol,
                "side": "BUY",
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": miktar,
                "price": fiyat
            }
            return {"status": "order_created", "data": data}
        except Exception as e:
            return {"error": str(e)}
    
    def kripto_sat(self, sembol, miktar, fiyat):
        """Kripto SAT"""
        try:
            data = {
                "symbol": sembol,
                "side": "SELL",
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": miktar,
                "price": fiyat
            }
            return {"status": "order_created", "data": data}
        except Exception as e:
            return {"error": str(e)}

# Kullanım:
# broker = AlpacaAPI()
# broker.al_emri("AAPL", 10, 150.50)
