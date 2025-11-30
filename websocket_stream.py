"""Real-time WebSocket Stream"""
import asyncio
import json
from datetime import datetime

class WebSocketStream:
    def __init__(self):
        self.streaming = False
        self.symbols = []
        self.callback = None
    
    def start_stream(self, symbols, callback=None):
        """WebSocket stream başlat"""
        self.symbols = symbols if isinstance(symbols, list) else [symbols]
        self.streaming = True
        self.callback = callback
        
        return True, f"✅ Streaming başladı: {', '.join(self.symbols)}"
    
    def stop_stream(self):
        """Stream durdur"""
        self.streaming = False
        return True, "⛔ Stream durduruldu"
    
    def get_live_price(self, symbol):
        """Canlı fiyat (simüle)"""
        import random
        base_prices = {"AAPL": 230, "MSFT": 420, "BTC": 91000, "ETH": 3500}
        price = base_prices.get(symbol, 100)
        variation = random.uniform(-0.02, 0.02)
        
        return {
            "symbol": symbol,
            "price": price * (1 + variation),
            "time": datetime.now().isoformat(),
            "change": variation * 100
        }
    
    def subscribe(self, symbol):
        """Symbol'e abone ol"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
        return True, f"✅ {symbol}'e abone olundu"
    
    def unsubscribe(self, symbol):
        """Symbol'den abone ol"""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
        return True, f"✅ {symbol}'den abone kaldırıldı"
