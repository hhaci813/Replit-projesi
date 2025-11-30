"""Otomatik Trading Engine - 24/7 Gerçek Para İşlemleri"""
from real_data_broker import RealBrokerData
from broker_persistence import BrokerPersistence
from logging_system import LoggingManager
import json
from datetime import datetime

class AutomatedTradingEngine:
    def __init__(self):
        self.real_data = RealBrokerData()
        self.persistence = BrokerPersistence()
        self.logger = LoggingManager()
        self.is_running = False
        self.rules = self.load_rules()
    
    def load_rules(self):
        """Trading kurallarını yükle"""
        return {
            "enabled": False,
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "max_position_size": 1000,  # Maksimum 1000$ pozisyon
            "stop_loss": -5,  # %5 zarar
            "take_profit": 20,  # %20 kar
            "daily_loss_limit": -5000,  # Günlük max zarar
            "max_trades_per_day": 10,
            "trading_hours": "09:30-16:00"
        }
    
    def can_trade(self, symbol):
        """Trading yapabilir mi kontrol et"""
        if not self.is_running:
            return False, "❌ Trading kapalı"
        
        if symbol not in self.rules["symbols"]:
            return False, f"❌ {symbol} izin listesinde değil"
        
        price = self.real_data.get_real_price(symbol)
        if not price:
            return False, "❌ Fiyat alınamadı"
        
        return True, price
    
    def calculate_position_size(self, bakiye, symbol):
        """Pozisyon boyutunu hesapla"""
        price = self.real_data.get_real_price(symbol)
        max_amount = self.rules["max_position_size"]
        
        if price:
            shares = min(int(max_amount / price), int(bakiye / price))
            return max(1, shares)
        return 0
    
    def check_signals(self, symbol):
        """AL/SAT sinyalini kontrol et"""
        stock_data = self.real_data.get_stock_data(symbol, period="5d")
        if not stock_data:
            return "HOLD"
        
        change = stock_data['change_pct']
        
        # Basit strateji:
        # -2% altında AL, +3% üstünde SAT
        if change < -2:
            return "AL"
        elif change > 3:
            return "SAT"
        else:
            return "HOLD"
    
    def execute_trade(self, broker, symbol, signal, quantity, price):
        """İşlem yap"""
        try:
            if signal == "AL":
                if broker == "alpaca":
                    from alpaca_broker_real import AlpacaBrokerReal
                    broker_obj = AlpacaBrokerReal()
                    ok, msg = broker_obj.al(symbol, quantity)
                else:
                    from binance_broker_real import BinanceBrokerReal
                    broker_obj = BinanceBrokerReal()
                    ok, msg = broker_obj.al(symbol, quantity)
            else:
                if broker == "alpaca":
                    from alpaca_broker_real import AlpacaBrokerReal
                    broker_obj = AlpacaBrokerReal()
                    ok, msg = broker_obj.sat(symbol, quantity)
                else:
                    from binance_broker_real import BinanceBrokerReal
                    broker_obj = BinanceBrokerReal()
                    ok, msg = broker_obj.sat(symbol, quantity)
            
            if ok:
                self.persistence.islem_kaydet(broker, signal, symbol, quantity, price)
                self.logger.log_trade(broker, symbol, signal, quantity, price, "executed")
                return True, msg
            else:
                return False, msg
        except Exception as e:
            self.logger.log_error(f"Trade execution error: {str(e)}")
            return False, str(e)
    
    def run_trading_cycle(self, broker_type="alpaca"):
        """Bir trading döngüsü yap"""
        if not self.is_running:
            return "❌ Trading kapalı"
        
        results = []
        
        for symbol in self.rules["symbols"]:
            can_trade, price = self.can_trade(symbol)
            
            if not can_trade:
                continue
            
            signal = self.check_signals(symbol)
            
            if signal != "HOLD":
                quantity = self.calculate_position_size(10000, symbol)  # Demo bakiye
                ok, msg = self.execute_trade(broker_type, symbol, signal, quantity, price)
                results.append(f"{'✅' if ok else '❌'} {symbol}: {signal} x{quantity}")
            else:
                results.append(f"⏸️ {symbol}: HOLD")
        
        return "\n".join(results) if results else "Sinyal yok"
    
    def start(self):
        """Otomatik trading başlat"""
        self.is_running = True
        self.logger.log_info("Automated trading started")
        return "✅ Otomatik Trading BAŞLADI"
    
    def stop(self):
        """Otomatik trading durdur"""
        self.is_running = False
        self.logger.log_info("Automated trading stopped")
        return "⛔ Otomatik Trading DURDURULDU"
    
    def emergency_close_all(self):
        """Acil durum - tüm pozisyonları kapat"""
        self.logger.log_alert("EMERGENCY CLOSE ALL - Tüm pozisyonlar kapatılıyor!")
        self.is_running = False
        return "🚨 ACIL KAPAT - Tüm pozisyonlar kapatılıyor"

if __name__ == "__main__":
    engine = AutomatedTradingEngine()
    print(engine.load_rules())
