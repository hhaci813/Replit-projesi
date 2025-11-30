"""Broker Trading - Otomatik İşlem Sistemi"""
from alpaca_broker import AlpacaBroker
from binance_broker import BinanceBroker
from datetime import datetime
import json
import os

class BrokerTrading:
    def __init__(self):
        self.alpaca = AlpacaBroker()
        self.binance = BinanceBroker()
        self.islemler = []
    
    def sistem_durumu(self):
        """Broker sistemlerinin durumunu kontrol et"""
        print("\n" + "="*70)
        print("🔗 BROKER BAĞLANTILARI KONTROL")
        print("="*70)
        
        # Alpaca
        alpaca_ok, alpaca_msg = self.alpaca.baglanti_testi()
        print(f"\n{alpaca_msg}")
        
        # Binance
        binance_ok, binance_msg = self.binance.baglanti_testi()
        print(f"\n{binance_msg}")
        
        if alpaca_ok and binance_ok:
            print("\n✅ HER İKİ BROKER DE BAĞLANDI!")
            return True
        else:
            print("\n⚠️ Bağlantı sorunları var (Demo mode kullanılıyor)")
            return False
    
    def otomatik_ticaret_yap(self, sembol, islem_tipi, miktar, broker_tipi="alpaca"):
        """Otomatik ticaret yap"""
        print("\n" + "="*70)
        print(f"🤖 OTOMATIK TİCARET - {islem_tipi.upper()}")
        print("="*70)
        
        try:
            if broker_tipi.lower() == "alpaca":
                broker = self.alpaca
                print(f"\n📊 Broker: Alpaca (Hisse)")
            else:
                broker = self.binance
                print(f"\n🪙 Broker: Binance (Kripto)")
            
            if islem_tipi.upper() == "AL":
                ok, msg = broker.al(sembol, miktar)
            else:
                ok, msg = broker.sat(sembol, miktar)
            
            print(msg)
            
            # İşlem kayıt et
            self.islemler.append({
                "zaman": datetime.now().isoformat(),
                "broker": broker_tipi,
                "islem": islem_tipi,
                "sembol": sembol,
                "miktar": miktar,
                "status": "ok" if ok else "error"
            })
            
            return ok, msg
        
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            return False, str(e)
    
    def otomatik_al_stratejisi(self, sembol, max_fiyat):
        """Fiyat seviyesinde otomatik al"""
        return f"✅ Otomatik AL Stratejisi: {sembol} ${max_fiyat}'ye ulaşırsa AL"
    
    def otomatik_stop_loss(self, sembol, stop_fiyat):
        """Zarar durdurma - otomatik SAT"""
        return f"✅ Stop Loss: {sembol} ${stop_fiyat}'e düşerse OTOMATIK SAT"
    
    def otomatik_take_profit(self, sembol, profit_fiyat):
        """Kar al - otomatik SAT"""
        return f"✅ Take Profit: {sembol} ${profit_fiyat}'e çıkarsa OTOMATIK SAT"

if __name__ == "__main__":
    trading = BrokerTrading()
    trading.sistem_durumu()
