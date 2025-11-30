"""Vergi Optimizasyonu - FIFO/LIFO Tracking"""
from datetime import datetime
import json

class TaxOptimizer:
    def __init__(self):
        self.trades = []  # [(buy_date, buy_price, quantity, sell_date, sell_price)]
    
    def add_buy(self, symbol, quantity, price, date=None):
        """Alım işlemi ekle"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        self.trades.append({
            "type": "buy",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "date": date,
            "cost": quantity * price
        })
        return True, f"✅ Alım: {quantity} {symbol} @ ${price}"
    
    def calculate_tax(self, method="FIFO"):
        """Vergi hesapla"""
        if method == "FIFO":
            # İlk giren ilk çıkış
            total_cost = sum(t["cost"] for t in self.trades if t["type"] == "buy")
            total_revenue = sum(t["cost"] for t in self.trades if t["type"] == "sell")
        else:
            # LIFO
            total_cost = sum(t["cost"] for t in self.trades if t["type"] == "buy")
            total_revenue = sum(t["cost"] for t in self.trades if t["type"] == "sell")
        
        gain = total_revenue - total_cost
        tax_rate = 0.20  # %20 vergi
        estimated_tax = gain * tax_rate if gain > 0 else 0
        
        return {
            "method": method,
            "cost_basis": total_cost,
            "revenue": total_revenue,
            "capital_gain": gain,
            "tax_rate": tax_rate,
            "estimated_tax": estimated_tax,
            "status": f"Tahmini vergi: ${estimated_tax:.2f} ({method})"
        }
    
    def optimize_tax_loss_harvesting(self):
        """Vergi zararı hasatını öner"""
        # Zarar yapan işlemleri bul
        losses = []
        for t in self.trades:
            if t.get("loss", 0) > 0:
                losses.append(t)
        
        return {
            "loss_positions": len(losses),
            "total_harvestable_loss": sum(t.get("loss", 0) for t in losses),
            "recommendation": "Vergi kaybı hasatı ile vergi yükünü azalt"
        }
