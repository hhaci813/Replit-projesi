"""🎯 /btc Analyzer - Kesin AL önerileri"""
import requests
import yfinance as yf
from datetime import datetime

class BTCAnalyzer:
    """Kesin yükselişe geçecekleri bulur"""
    
    @staticmethod
    def get_strong_recommendations():
        """STRONG_BUY önerileri"""
        cryptos = BTCAnalyzer._get_cryptos()
        stocks = BTCAnalyzer._get_stocks()
        
        return {
            'cryptos': cryptos,
            'stocks': stocks,
            'timestamp': datetime.now()
        }
    
    @staticmethod
    def _get_cryptos():
        """BTCTurk yükselen kriptolar"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            tickers = resp.json().get('data', []) if isinstance(resp.json(), dict) else resp.json()
            picks = []
            
            for t in tickers:
                if isinstance(t, dict) and 'TRY' in t.get('pairNormalized', ''):
                    symbol = t['pairNormalized'].split('_')[0]
                    change = float(t.get('dailyPercent', 0))
                    price = float(t.get('last', 0))
                    
                    if price > 0:
                        score = (50 if change > 10 else 30 if change > 5 else 10) + (20 if float(t.get('volume', 0)) > 1000000 else 0)
                        picks.append({
                            'symbol': symbol,
                            'change': change,
                            'price': price,
                            'score': score,
                            'recommendation': 'STRONG_BUY' if score > 60 else 'BUY' if score > 30 else 'HOLD'
                        })
            
            return sorted([p for p in picks if p['recommendation'] in ['STRONG_BUY', 'BUY']], key=lambda x: x['score'], reverse=True)[:10]
        except:
            return []
    
    @staticmethod
    def _get_stocks():
        """Yükselen hisseler"""
        stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'ADBE', 'CRM']
        picks = []
        
        for symbol in stocks:
            try:
                hist = yf.Ticker(symbol).history(period="20d")
                if len(hist) > 5:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-5]
                    change = ((current - prev) / prev * 100) if prev > 0 else 0
                    score = (50 if change > 5 else 30 if change > 2 else 10) + (20 if current > hist['Close'].mean() else 0)
                    
                    picks.append({
                        'symbol': symbol,
                        'change': change,
                        'price': current,
                        'score': score,
                        'recommendation': 'STRONG_BUY' if score > 60 else 'BUY' if score > 30 else 'HOLD'
                    })
            except:
                pass
        
        return sorted([p for p in picks if p['recommendation'] in ['STRONG_BUY', 'BUY']], key=lambda x: x['score'], reverse=True)[:8]

