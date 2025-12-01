"""🌍 Global Markets Analyzer - Dünya borsaları analizi"""
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

class GlobalMarketsAnalyzer:
    """Dünya borsaları - S&P 500, DAX, NIKKEI, vb"""
    
    GLOBAL_INDICES = {
        'S&P 500': '^GSPC',      # USA
        'NASDAQ': '^IXIC',       # USA Tech
        'DOW': '^DJI',           # USA Industrial
        'DAX': '^GDAXI',         # Germany
        'CAC 40': '^FCHI',       # France
        'FTSE 100': '^FTSE',     # UK
        'NIKKEI': '^N225',       # Japan
        'Hang Seng': '^HSI',     # Hong Kong
        'Shanghai': '000001.SS', # China
        'STOXX 600': '^STOXX',   # Europe
    }
    
    def get_global_status(self):
        """Tüm global indices'in durumunu al"""
        results = []
        
        for name, symbol in self.GLOBAL_INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='5d')
                
                if data.empty:
                    continue
                
                current = data['Close'].iloc[-1]
                previous = data['Close'].iloc[-2] if len(data) > 1 else current
                change_pct = ((current - previous) / previous * 100) if previous != 0 else 0
                
                # RSI hesapla
                rsi = self._calculate_rsi(data['Close'].values)
                
                # Trend
                ma5 = data['Close'].rolling(5).mean().iloc[-1]
                ma20 = data['Close'].rolling(20).mean().iloc[-1] if len(data) >= 20 else ma5
                
                if current > ma5 > ma20:
                    trend = "STRONG_UP"
                    emoji = "📈📈"
                elif current < ma5 < ma20:
                    trend = "STRONG_DOWN"
                    emoji = "📉📉"
                elif current > ma5:
                    trend = "UP"
                    emoji = "📈"
                elif current < ma5:
                    trend = "DOWN"
                    emoji = "📉"
                else:
                    trend = "SIDEWAYS"
                    emoji = "➡️"
                
                results.append({
                    'index': name,
                    'symbol': symbol,
                    'price': current,
                    'change': change_pct,
                    'rsi': rsi,
                    'trend': trend,
                    'emoji': emoji,
                    'ma5': ma5,
                    'ma20': ma20
                })
            
            except Exception as e:
                print(f"⚠️ {name} error: {e}")
        
        return results
    
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """RSI hesaplama"""
        if len(prices) < period:
            return 50
        
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        
        up = seed[seed >= 0].sum() / period if len(seed) > 0 else 0
        down = -seed[seed < 0].sum() / period if len(seed) > 0 else 0
        
        rs = up / down if down != 0 else 0
        rsi = 100 - 100 / (1 + rs) if rs != 0 else 50
        
        return rsi
    
    def get_market_summary(self):
        """Market özeti"""
        indices = self.get_global_status()
        
        rising = [i for i in indices if i['change'] > 0]
        falling = [i for i in indices if i['change'] < 0]
        
        avg_change = np.mean([i['change'] for i in indices]) if indices else 0
        
        if avg_change > 1:
            overall = "BULLISH 🟢"
        elif avg_change < -1:
            overall = "BEARISH 🔴"
        else:
            overall = "NEUTRAL ⚪"
        
        return {
            'overall': overall,
            'avg_change': avg_change,
            'rising_count': len(rising),
            'falling_count': len(falling),
            'indices': indices
        }

class SectorAnalyzer:
    """Sektör analizi - Technology, Finance, Energy, vb"""
    
    SECTOR_ETFS = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Finance': 'XLF',
        'Energy': 'XLE',
        'Materials': 'XLB',
        'Industrials': 'XLI',
        'Consumer': 'XLY',
        'Utilities': 'XLU',
        'Real Estate': 'XLRE',
        'Communication': 'XLC',
    }
    
    def get_sector_performance(self):
        """Sektör performansı"""
        sectors = []
        
        for name, symbol in self.SECTOR_ETFS.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1y')
                
                if data.empty or len(data) < 2:
                    continue
                
                current = data['Close'].iloc[-1]
                year_ago = data['Close'].iloc[0]
                year_change = ((current - year_ago) / year_ago * 100) if year_ago != 0 else 0
                
                month_ago = data['Close'].iloc[-20] if len(data) > 20 else year_ago
                month_change = ((current - month_ago) / month_ago * 100) if month_ago != 0 else 0
                
                if year_change > 10:
                    rating = "STRONG_BUY"
                    emoji = "🟢🟢"
                elif year_change > 0:
                    rating = "BUY"
                    emoji = "🟢"
                elif year_change < -10:
                    rating = "SELL"
                    emoji = "🔴🔴"
                else:
                    rating = "HOLD"
                    emoji = "🟡"
                
                sectors.append({
                    'sector': name,
                    'symbol': symbol,
                    'year_change': year_change,
                    'month_change': month_change,
                    'rating': rating,
                    'emoji': emoji
                })
            
            except Exception as e:
                print(f"⚠️ Sector {name} error: {e}")
        
        return sectors

if __name__ == "__main__":
    analyzer = GlobalMarketsAnalyzer()
    summary = analyzer.get_market_summary()
    print(f"Market: {summary['overall']}")
    print(f"Avg Change: {summary['avg_change']:+.2f}%")
    
    sector = SectorAnalyzer()
    sectors = sector.get_sector_performance()
    print(f"\nSectors: {len(sectors)} analyzed")
