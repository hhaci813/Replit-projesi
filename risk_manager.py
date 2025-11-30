"""Risk Yönetimi - Korumalı Trading"""
import json
from datetime import datetime

class RiskManager:
    def __init__(self):
        self.daily_loss = 0
        self.trades_today = 0
        self.active_positions = {}
    
    def check_daily_loss_limit(self, loss_amount, limit=-5000):
        """Günlük zarar limitini kontrol et"""
        if self.daily_loss + loss_amount < limit:
            return False, f"❌ Günlük zarar limiti aşıldı (${self.daily_loss})"
        return True, "✅ Zarar limiti OK"
    
    def check_trade_limit(self, limit=10):
        """Gün içi işlem limitini kontrol et"""
        if self.trades_today >= limit:
            return False, f"❌ Günlük işlem limiti aşıldı ({self.trades_today})"
        return True, "✅ İşlem limiti OK"
    
    def apply_stop_loss(self, entry_price, current_price, stop_loss_pct=-5):
        """Stop Loss kontrol et"""
        change_pct = ((current_price - entry_price) / entry_price) * 100
        if change_pct <= stop_loss_pct:
            return True, f"🛑 STOP LOSS TETİKLENDİ ({change_pct:.2f}%)"
        return False, None
    
    def apply_take_profit(self, entry_price, current_price, take_profit_pct=20):
        """Take Profit kontrol et"""
        change_pct = ((current_price - entry_price) / entry_price) * 100
        if change_pct >= take_profit_pct:
            return True, f"💰 TAKE PROFIT TETİKLENDİ ({change_pct:.2f}%)"
        return False, None
    
    def check_position_size(self, bakiye, position_value, max_risk_pct=2):
        """Pozisyon büyüklüğü riskli mi?"""
        risk = (position_value / bakiye) * 100
        if risk > max_risk_pct:
            return False, f"❌ Pozisyon çok büyük ({risk:.1f}%)"
        return True, f"✅ Pozisyon güvenli ({risk:.1f}%)"

if __name__ == "__main__":
    risk = RiskManager()
    print(risk.check_daily_loss_limit(-1000))
