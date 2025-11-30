"""Alpaca Broker API - Hisse İşlemleri"""
import os
import requests
from datetime import datetime

class AlpacaBroker:
    def __init__(self):
        # Demo credentials (Paper Trading)
        self.api_key = os.environ.get('ALPACA_API_KEY', 'PK123456789DEMO')
        self.secret_key = os.environ.get('ALPACA_SECRET_KEY', 'SECRET123456789DEMO')
        self.base_url = "https://paper-api.alpaca.markets"  # Paper trading (demo)
        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "Content-Type": "application/json"
        }
    
    def baglanti_testi(self):
        """Alpaca bağlantısını test et"""
        try:
            resp = requests.get(f"{self.base_url}/v2/account", headers=self.headers, timeout=5)
            if resp.status_code == 200:
                account = resp.json()
                return True, f"✅ Alpaca bağlantısı başarılı\n   Account: Paper Trading (Demo)\n   Bakiye: ${account.get('buying_power', 0)}"
            else:
                return False, f"❌ Bağlantı başarısız: {resp.status_code}"
        except Exception as e:
            return False, f"❌ Hata: {str(e)}"
    
    def al(self, sembol, miktar, fiyat=None):
        """Hisse al"""
        try:
            order_data = {
                "symbol": sembol.upper(),
                "qty": int(miktar),
                "side": "buy",
                "type": "market",
                "time_in_force": "day"
            }
            
            resp = requests.post(
                f"{self.base_url}/v2/orders",
                json=order_data,
                headers=self.headers,
                timeout=10
            )
            
            if resp.status_code == 201:
                order = resp.json()
                return True, f"""✅ AL ORDERİ BAŞARILI
                
   Sembol: {sembol}
   Miktar: {miktar}
   Tür: Market
   Status: {order.get('status')}
   ID: {order.get('id')}
   Zaman: {datetime.now().strftime('%H:%M:%S')}"""
            else:
                return False, f"❌ Order başarısız: {resp.text}"
        except Exception as e:
            return False, f"❌ Hata: {str(e)}"
    
    def sat(self, sembol, miktar):
        """Hisse sat"""
        try:
            order_data = {
                "symbol": sembol.upper(),
                "qty": int(miktar),
                "side": "sell",
                "type": "market",
                "time_in_force": "day"
            }
            
            resp = requests.post(
                f"{self.base_url}/v2/orders",
                json=order_data,
                headers=self.headers,
                timeout=10
            )
            
            if resp.status_code == 201:
                order = resp.json()
                return True, f"""✅ SAT ORDERİ BAŞARILI
                
   Sembol: {sembol}
   Miktar: {miktar}
   Tür: Market
   Status: {order.get('status')}
   ID: {order.get('id')}
   Zaman: {datetime.now().strftime('%H:%M:%S')}"""
            else:
                return False, f"❌ Order başarısız: {resp.text}"
        except Exception as e:
            return False, f"❌ Hata: {str(e)}"
    
    def pozisyon_goster(self):
        """Mevcut pozisyonları göster"""
        try:
            resp = requests.get(
                f"{self.base_url}/v2/positions",
                headers=self.headers,
                timeout=5
            )
            
            if resp.status_code == 200:
                positions = resp.json()
                if not positions:
                    return True, "Mevcut pozisyon yok"
                
                sonuc = "📊 MEVCUT POZİSYONLAR:\n\n"
                for pos in positions:
                    sonuc += f"• {pos['symbol']}: {pos['qty']} share @ ${pos['avg_fill_price']}\n"
                    sonuc += f"  PnL: ${pos['unrealized_pl']} ({pos['unrealized_plpc']}%)\n\n"
                return True, sonuc
            else:
                return False, f"❌ Pozisyon bilgisi alınamadı: {resp.text}"
        except Exception as e:
            return False, f"❌ Hata: {str(e)}"
    
    def bakiye_goster(self):
        """Hesap bakiyesi göster"""
        try:
            resp = requests.get(f"{self.base_url}/v2/account", headers=self.headers, timeout=5)
            
            if resp.status_code == 200:
                account = resp.json()
                return True, f"""💰 ALPACA HESAP:
   
   Bakiye: ${float(account.get('buying_power', 0)):.2f}
   Portföy Değeri: ${float(account.get('portfolio_value', 0)):.2f}
   Nakit: ${float(account.get('cash', 0)):.2f}
   Mod: Paper Trading (Demo)"""
            else:
                return False, f"❌ Hesap bilgisi alınamadı"
        except Exception as e:
            return False, f"❌ Hata: {str(e)}"

if __name__ == "__main__":
    broker = AlpacaBroker()
    ok, msg = broker.baglanti_testi()
    print(msg)
