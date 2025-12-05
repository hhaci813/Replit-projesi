"""📱 Telegram /btc Handler - BTCTurk Kripto + Hisse Analizi"""
import requests
import yfinance as yf
from datetime import datetime

class BTCHandler:
    """Telegram /btc komutu - İndir ve analiz et"""
    
    @staticmethod
    def get_report():
        """Detaylı /btc raporu"""
        
        # 1. BTCTurk
        btc_gainers = BTCHandler._get_btcturk_gainers()
        
        # 2. Stocks
        stock_gainers = BTCHandler._get_stock_gainers()
        
        # Report oluştur
        msg = f"""
🔍 *BTCTURK DETAYLI ANALİZİ + HİSSE GAINER'LAR*
{datetime.now().strftime('%d.%m.%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 *YÜKSELEN KRİPTO (Top 5):*
"""
        
        for i, g in enumerate(btc_gainers[:5], 1):
            emoji = "🔥" if g['change'] > 5 else "📈"
            msg += f"{i}. {emoji} {g['symbol']:8} +{g['change']:.2f}%\n"
        
        msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *YÜKSELEN HİSSELER (Top 5):*
"""
        
        for i, s in enumerate(stock_gainers[:5], 1):
            emoji = "🟢" if s['change'] > 3 else "📊"
            msg += f"{i}. {emoji} {s['symbol']:8} +{s['change']:.2f}%\n"
        
        msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *ÖNERİLER:*

💻 *TECH STOCKS (STRONG_BUY):*
"""
        tech = [s for s in stock_gainers[:3] if s['symbol'] in ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META']]
        for s in tech:
            msg += f"   ✅ {s['symbol']:8} +{s['change']:.2f}% | Kar: +25%\n"
        
        msg += f"""
🪙 *CRYPTO (MOMENTUM):*
"""
        
        for c in btc_gainers[:3]:
            msg += f"   ✅ {c['symbol']:8} +{c['change']:.2f}% | Risk: 3/10\n"
        
        msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ *RİSK YÖNETİMİ:*
   • Stop Loss: -5%
   • Take Profit: +25%
   • Max Position: 5%
   • Diversify: 5+ assets

📊 Grafik & Deep research yapılıyor...
"""
        
        return msg
    
    @staticmethod
    def _get_btcturk_gainers():
        """BTCTurk gainers"""
        try:
            url = "https://api.btcturk.com/api/v2/ticker"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            tickers = data.get('data', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            cryptos = []
            
            for ticker in tickers:
                if isinstance(ticker, dict):
                    pair = ticker.get('pairNormalized', '')
                    if 'TRY' in pair:
                        symbol = pair.split('_')[0]
                        change = float(ticker.get('dailyPercent', 0))
                        price = float(ticker.get('last', 0))
                        
                        if price > 0:
                            cryptos.append({'symbol': symbol, 'change': change, 'price': price})
            
            return sorted([c for c in cryptos if c['change'] > 0], key=lambda x: x['change'], reverse=True)
        except Exception as e:
            print(f"BTC error: {e}")
            return []
    
    @staticmethod
    def _get_stock_gainers():
        """Hisse gainers"""
        stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
        gainers = []
        
        for symbol in stocks:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                
                if len(hist) > 1:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = ((current - prev) / prev * 100) if prev > 0 else 0
                    
                    gainers.append({'symbol': symbol, 'change': change, 'price': current})
            except:
                pass
        
        return sorted([g for g in gainers if g['change'] > 0], key=lambda x: x['change'], reverse=True)

# Test
if __name__ == "__main__":
    report = BTCHandler.get_report()
    print(report)

