"""BTCTurk API Connector - Gerçek Zamanlı Ticaret"""
import requests
import time
import base64
import hmac
import hashlib
import json

class BTCTurkConnector:
    """BTCTurk API ile bağlantı - Real-time fiyatlar ve trading"""
    
    BASE_URL = "https://api.btcturk.com"
    
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
    
    def get_ticker(self, pair_symbol="BTCTRY"):
        """Public - Fiyat bilgisi al"""
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/api/v2/ticker?pairSymbol={pair_symbol}",
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                ticker = data.get('data', [{}])[0]
                return {
                    'last': float(ticker.get('last', 0)),
                    'bid': float(ticker.get('bid', 0)),
                    'ask': float(ticker.get('ask', 0)),
                    'volume': float(ticker.get('volume24h', 0)),
                    'change': float(ticker.get('change24h', 0))
                }
        except Exception as e:
            print(f"❌ Ticker hata: {str(e)[:50]}")
        return None
    
    def get_order_book(self, pair_symbol="BTCTRY", limit=20):
        """Public - Order book al"""
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/api/v2/orderbook?pairSymbol={pair_symbol}&limit={limit}",
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json().get('data', {})
        except:
            pass
        return None
    
    def _get_auth_headers(self):
        """Private - Authentication headers oluştur"""
        if not self.api_key or not self.api_secret:
            return None
        
        try:
            api_secret = base64.b64decode(self.api_secret)
            stamp = str(int(time.time() * 1000))
            data = f"{self.api_key}{stamp}".encode('utf-8')
            signature = hmac.new(api_secret, data, hashlib.sha256).digest()
            signature = base64.b64encode(signature).decode()
            
            return {
                "X-PCK": self.api_key,
                "X-Stamp": stamp,
                "X-Signature": signature,
                "Content-Type": "application/json"
            }
        except:
            return None
    
    def get_balance(self):
        """Private - Hesap bakiyesi al"""
        headers = self._get_auth_headers()
        if not headers:
            print("❌ API key gerekli")
            return None
        
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/api/v1/users/balances",
                headers=headers,
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json().get('data', [])
        except Exception as e:
            print(f"❌ Balance hata: {str(e)[:50]}")
        return None
    
    def get_open_orders(self, pair_symbol="BTCTRY"):
        """Private - Açık emirler al"""
        headers = self._get_auth_headers()
        if not headers:
            return None
        
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/api/v1/openOrders?pairSymbol={pair_symbol}",
                headers=headers,
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json().get('data', [])
        except:
            pass
        return None
    
    def place_order(self, pair_symbol, order_type, order_method, quantity, price=None):
        """Private - Emir gönder"""
        headers = self._get_auth_headers()
        if not headers:
            return None
        
        payload = {
            "pairSymbol": pair_symbol,
            "orderType": order_type,  # "buy" or "sell"
            "orderMethod": order_method,  # "limit" or "market"
            "quantity": quantity,
        }
        
        if order_method == "limit" and price:
            payload["price"] = price
        
        try:
            resp = self.session.post(
                f"{self.BASE_URL}/api/v1/order",
                headers=headers,
                json=payload,
                timeout=5
            )
            if resp.status_code == 201:
                return resp.json().get('data')
            else:
                print(f"❌ Order hata: {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            print(f"❌ Order exception: {str(e)[:50]}")
        return None
    
    def cancel_order(self, order_id):
        """Private - Emir iptal et"""
        headers = self._get_auth_headers()
        if not headers:
            return None
        
        try:
            resp = self.session.delete(
                f"{self.BASE_URL}/api/v1/order/{order_id}",
                headers=headers,
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json().get('data')
        except:
            pass
        return None
    
    def get_user_trades(self, pair_symbol="BTCTRY", limit=50):
        """Private - İşlem geçmişi"""
        headers = self._get_auth_headers()
        if not headers:
            return None
        
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/api/v1/userTransactions?pairSymbol={pair_symbol}&limit={limit}",
                headers=headers,
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json().get('data', [])
        except:
            pass
        return None


# Test
if __name__ == "__main__":
    # Public endpoints test (API key gerekmez)
    btc = BTCTurkConnector()
    
    ticker = btc.get_ticker("BTCTRY")
    if ticker:
        print(f"\n💰 BTCTurk BTCTRY:")
        print(f"   Son Fiyat: ₺{ticker['last']:,.0f}")
        print(f"   Bid: ₺{ticker['bid']:,.0f}")
        print(f"   Ask: ₺{ticker['ask']:,.0f}")
        print(f"   24h Değişim: {ticker['change']:+.2f}%")
        print(f"   24h Hacim: {ticker['volume']:,.0f}")
    
    # Order book
    ob = btc.get_order_book("BTCTRY", limit=5)
    if ob:
        bids = ob.get('bids', [])
        asks = ob.get('asks', [])
        if bids:
            print(f"\n📊 Order Book:")
            print(f"   En Yüksek Bid: ₺{bids[0]['price']:,.0f}")
            print(f"   En Düşük Ask: ₺{asks[0]['price']:,.0f}")
