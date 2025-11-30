"""Multi-Symbol Tracking & Monitoring"""

class MultiSymbolTracker:
    def __init__(self):
        self.watchlist = {}
    
    def add_to_watchlist(self, symbols):
        """Watchlist'e ekle"""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        for symbol in symbols:
            self.watchlist[symbol] = {"status": "watching", "alerts": 0}
        
        return True, f"✅ {len(symbols)} symbol watchlist'e eklendi"
    
    def monitor_multiple(self, symbols):
        """Birden fazla symbol izle"""
        from symbol_analyzer import SymbolAnalyzer
        analyzer = SymbolAnalyzer()
        
        results = {}
        for symbol in symbols:
            result = analyzer.generate_signal(symbol)
            results[symbol] = result.get("signal", "?")
        
        return results
    
    def set_alerts(self, symbol, price_high=None, price_low=None):
        """Uyarı ayarla"""
        if symbol not in self.watchlist:
            self.watchlist[symbol] = {}
        
        self.watchlist[symbol]["high_alert"] = price_high
        self.watchlist[symbol]["low_alert"] = price_low
        
        return True, f"✅ {symbol} uyarıları: ${price_low}-${price_high}"
    
    def get_watchlist(self):
        """Watchlist'i göster"""
        return {
            "count": len(self.watchlist),
            "symbols": list(self.watchlist.keys()),
            "list": self.watchlist
        }
