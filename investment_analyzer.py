"""Grafik Analizi & Yatırım Tavsiyesi - Tüm Kripto & Hisseler"""
import requests
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import json

class InvestmentAnalyzer:
    def __init__(self):
        self.symbols_crypto = ["BTC", "ETH", "XRP", "BNB", "SOL", "ADA", "DOGE", "LINK"]
        self.symbols_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "JPM", "JNJ", "V"]
        self.symbols_turk = ["XRPTRY"]  # Türkiye spesifik
    
    def get_all_prices(self):
        """Tüm araçların fiyatlarını getir"""
        data = {}
        
        # BTCTurk kripto
        try:
            pairs = [("BTCTRY", "BTC"), ("ETHTRY", "ETH"), ("XRPTRY", "XRP")]
            for pair, symbol in pairs:
                resp = requests.get(f"https://api.btcturk.com/api/v2/ticker?pairSymbol={pair}", timeout=5)
                if resp.status_code == 200:
                    price = float(resp.json()['data'][0]['last'])
                    data[symbol] = {"price_try": price, "source": "BTCTurk"}
        except:
            pass
        
        # YFinance kripto
        for sym in ["BTC", "ETH", "XRP", "BNB", "SOL", "ADA", "DOGE", "LINK"]:
            if sym not in data:
                try:
                    ticker = yf.Ticker(f"{sym}-USD")
                    hist = ticker.history(period="30d")
                    if not hist.empty:
                        current = float(hist['Close'].iloc[-1])
                        prev_close = float(hist['Close'].iloc[-2])
                        change = ((current - prev_close) / prev_close * 100) if prev_close != 0 else 0
                        
                        data[sym] = {
                            "price": current,
                            "prev_close": prev_close,
                            "change_pct": change,
                            "source": "YFinance",
                            "hist": hist
                        }
                except:
                    pass
        
        # YFinance hisseler
        for sym in ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "JPM", "JNJ", "V"]:
            try:
                ticker = yf.Ticker(sym)
                hist = ticker.history(period="30d")
                if not hist.empty:
                    current = float(hist['Close'].iloc[-1])
                    prev_close = float(hist['Close'].iloc[-2])
                    change = ((current - prev_close) / prev_close * 100) if prev_close != 0 else 0
                    
                    data[sym] = {
                        "price": current,
                        "prev_close": prev_close,
                        "change_pct": change,
                        "source": "YFinance",
                        "hist": hist
                    }
            except:
                pass
        
        return data
    
    def calculate_rsi(self, prices, period=14):
        """RSI hesapla"""
        if len(prices) < period:
            return 50
        
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = 100 - 100 / (1 + rs) if rs >= 0 else 0
        return rsi
    
    def calculate_macd(self, prices):
        """MACD hesapla"""
        if len(prices) < 26:
            return 0, 0, 0
        
        ema_12 = np.mean(prices[-12:])
        ema_26 = np.mean(prices[-26:])
        macd = ema_12 - ema_26
        signal = np.mean([ema_12 - ema_26, np.mean(prices[-35:]) - np.mean(prices[-35:])]) if len(prices) >= 35 else macd
        histogram = macd - signal
        
        return macd, signal, histogram
    
    def get_signal(self, symbol_data):
        """Sinyal oluştur (AL/SAT/HOLD)"""
        if "hist" not in symbol_data:
            return "❓"
        
        hist = symbol_data["hist"]
        prices = hist['Close'].values
        
        rsi = self.calculate_rsi(prices)
        macd, signal, histogram = self.calculate_macd(prices)
        
        # Trend
        ma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else prices[-1]
        current_price = prices[-1]
        
        # Sinyal mantığı
        if rsi < 30 and current_price < ma_20:
            return "🟢 AL"  # Oversold + below MA
        elif rsi > 70 and current_price > ma_20:
            return "🔴 SAT"  # Overbought + above MA
        elif current_price > ma_20:
            return "⚪ HOLD+"  # Pozitif
        else:
            return "⚪ HOLD"  # Nötr
    
    def analyze_all(self):
        """Tüm araçları analiz et"""
        print("\n" + "="*80)
        print("📊 KAPSAMLI GRAFIK ANALİZİ - TÜM KRİPTO & HİSSELER")
        print("="*80 + "\n")
        
        data = self.get_all_prices()
        
        analysis_results = []
        
        # Kripto
        print("🪙 KRİPTOPARALAR:\n")
        crypto_data = []
        for sym in ["BTC", "ETH", "XRP", "BNB", "SOL", "ADA", "DOGE", "LINK"]:
            if sym in data:
                item = data[sym]
                if "price" in item:
                    price = item["price"]
                    change = item["change_pct"]
                    signal = self.get_signal(item)
                    
                    emoji = "📈" if change > 0 else "📉"
                    color = "🟢" if change > 0 else "🔴"
                    
                    print(f"{emoji} {sym:6} ${price:10,.2f}  {color} {change:+7.2f}%  Signal: {signal}")
                    
                    crypto_data.append({
                        "symbol": sym,
                        "price": price,
                        "change": change,
                        "signal": signal
                    })
                    
                    analysis_results.append((sym, price, change, signal))
        
        # Hisseler
        print("\n\n📈 HİSSE SENETLERİ:\n")
        stock_data = []
        for sym in ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "JPM", "JNJ", "V"]:
            if sym in data:
                item = data[sym]
                price = item["price"]
                change = item["change_pct"]
                signal = self.get_signal(item)
                
                emoji = "📈" if change > 0 else "📉"
                color = "🟢" if change > 0 else "🔴"
                
                print(f"{emoji} {sym:6} ${price:10,.2f}  {color} {change:+7.2f}%  Signal: {signal}")
                
                stock_data.append({
                    "symbol": sym,
                    "price": price,
                    "change": change,
                    "signal": signal
                })
                
                analysis_results.append((sym, price, change, signal))
        
        # Türkiye kripto
        print("\n\n🇹🇷 TÜRKIYE KRİPTO:\n")
        if "XRP" in data and "price_try" in data["XRP"]:
            xrp_try = data["XRP"]["price_try"]
            print(f"💱 XRP: {xrp_try:,.2f} TRY")
        
        # Önerileri sırala
        print("\n" + "="*80)
        print("🎯 YATIRIM ÖNERİLERİ\n")
        
        rising = [r for r in analysis_results if r[2] > 0]
        falling = [r for r in analysis_results if r[2] < 0]
        
        rising.sort(key=lambda x: x[2], reverse=True)
        
        if rising:
            print("🟢 YÜKSELENLER (Al tarafında):\n")
            for sym, price, change, signal in rising[:5]:
                print(f"   {sym:6} ${price:10,.2f}  +{change:.2f}%  {signal}")
        
        print("\n\n🔴 DÜŞENLER (SAT tarafında):\n")
        if falling:
            for sym, price, change, signal in falling[:5]:
                print(f"   {sym:6} ${price:10,.2f}  {change:.2f}%  {signal}")
        
        return {
            "crypto": crypto_data,
            "stocks": stock_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_html_report(self):
        """HTML grafik raporu oluştur"""
        data = self.get_all_prices()
        
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Investment Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; color: #00ff00; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .card { background: #2a2a2a; padding: 15px; border-radius: 8px; border-left: 3px solid #00ff00; }
        .card h3 { margin: 0 0 10px 0; }
        .price { font-size: 24px; color: #00ff00; }
        .change-pos { color: #00ff00; }
        .change-neg { color: #ff0000; }
        .chart { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Investment Analysis Dashboard</h1>
"""
        
        # Kripto kartları
        html += "<h2>🪙 Cryptocurrencies</h2><div class='grid'>"
        for sym in ["BTC", "ETH", "XRP"]:
            if sym in data and "price" in data[sym]:
                item = data[sym]
                price = item["price"]
                change = item["change_pct"]
                change_class = "change-pos" if change > 0 else "change-neg"
                
                html += f"""
<div class='card'>
    <h3>{sym}</h3>
    <div class='price'>${price:,.2f}</div>
    <div class='{change_class}'>{change:+.2f}%</div>
</div>
"""
        html += "</div>"
        
        # Hisse kartları
        html += "<h2>📈 Stocks</h2><div class='grid'>"
        for sym in ["AAPL", "MSFT", "GOOGL"]:
            if sym in data:
                item = data[sym]
                price = item["price"]
                change = item["change_pct"]
                change_class = "change-pos" if change > 0 else "change-neg"
                
                html += f"""
<div class='card'>
    <h3>{sym}</h3>
    <div class='price'>${price:,.2f}</div>
    <div class='{change_class}'>{change:+.2f}%</div>
</div>
"""
        html += "</div></div></body></html>"
        
        return html

# Test
if __name__ == "__main__":
    analyzer = InvestmentAnalyzer()
    analyzer.analyze_all()
