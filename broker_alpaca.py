"""Alpaca Broker API - Paper Trading & Real Trading"""
import os
from datetime import datetime

class AlpacaBrokerEngine:
    """Paper & Real Trading Engine"""
    
    def __init__(self):
        self.api_key = "PAPER_KEY_demo"  # Demo
        self.api_secret = "PAPER_SECRET_demo"  # Demo
        self.base_url = "https://paper-api.alpaca.markets"
        
        # Paper trading simülatörü
        self.positions = {}
        self.cash = 100000  # Başlangıç
        self.trades = []
    
    def buy(self, symbol, shares, price):
        """Satın al"""
        cost = shares * price
        if cost > self.cash:
            return False, f"❌ Yeterli para yok (${self.cash:.2f})"
        
        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + shares
        
        trade = {
            'type': 'BUY',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'cost': cost,
            'timestamp': datetime.now(),
            'cash_remaining': self.cash
        }
        self.trades.append(trade)
        
        return True, f"✅ {symbol}: {shares} hisse @ ${price:.2f} = ${cost:,.2f}"
    
    def sell(self, symbol, shares, price):
        """Sat"""
        if symbol not in self.positions or self.positions[symbol] < shares:
            return False, f"❌ Yeterli hisse yok"
        
        proceeds = shares * price
        self.cash += proceeds
        self.positions[symbol] -= shares
        
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        
        trade = {
            'type': 'SELL',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'proceeds': proceeds,
            'timestamp': datetime.now(),
            'cash_remaining': self.cash
        }
        self.trades.append(trade)
        
        return True, f"✅ {symbol}: {shares} hisse @ ${price:.2f} = ${proceeds:,.2f}"
    
    def get_portfolio_value(self, current_prices):
        """Portföy değerini hesapla"""
        positions_value = sum(
            shares * current_prices.get(sym, 0)
            for sym, shares in self.positions.items()
        )
        return self.cash + positions_value
    
    def get_positions(self):
        """Pozisyonları göster"""
        return self.positions
    
    def get_cash(self):
        """Kalan nakit"""
        return self.cash
    
    def get_trades(self):
        """Trade history"""
        return self.trades
