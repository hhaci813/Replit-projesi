"""🌍 GLOBAL MARKETS - DÜNYA PİYASALARI
S&P500, DAX, Altın, Petrol, DXY takibi
"""
import yfinance as yf
from datetime import datetime
import numpy as np

class GlobalMarketsAnalyzer:
    """Global piyasa analizi"""
    
    def __init__(self):
        self.indices = {
            '^GSPC': {'name': 'S&P 500', 'region': 'US'},
            '^DJI': {'name': 'Dow Jones', 'region': 'US'},
            '^IXIC': {'name': 'NASDAQ', 'region': 'US'},
            '^GDAXI': {'name': 'DAX', 'region': 'EU'},
            '^FTSE': {'name': 'FTSE 100', 'region': 'UK'},
            '^N225': {'name': 'Nikkei 225', 'region': 'JP'},
        }
        
        self.commodities = {
            'GC=F': {'name': 'Altın', 'type': 'metal'},
            'SI=F': {'name': 'Gümüş', 'type': 'metal'},
            'CL=F': {'name': 'Petrol (WTI)', 'type': 'energy'},
            'BZ=F': {'name': 'Petrol (Brent)', 'type': 'energy'},
        }
        
        self.currencies = {
            'DX-Y.NYB': {'name': 'DXY (Dolar Endeksi)', 'impact': 'inverse'},
            'USDTRY=X': {'name': 'USD/TRY', 'impact': 'direct'},
            'EURTRY=X': {'name': 'EUR/TRY', 'impact': 'direct'},
        }
    
    def get_index_data(self, symbol):
        """Endeks verisi al"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d')
            
            if len(hist) < 2:
                return None
            
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = ((current - prev) / prev) * 100
            
            return {
                'price': round(current, 2),
                'change': round(change, 2),
                'high': round(hist['High'].iloc[-1], 2),
                'low': round(hist['Low'].iloc[-1], 2)
            }
        except:
            return None
    
    def get_all_indices(self):
        """Tüm endeksleri al"""
        results = {}
        
        for symbol, info in self.indices.items():
            data = self.get_index_data(symbol)
            if data:
                results[info['name']] = {
                    **data,
                    'region': info['region'],
                    'symbol': symbol
                }
        
        return results
    
    def get_commodities(self):
        """Emtia verilerini al"""
        results = {}
        
        for symbol, info in self.commodities.items():
            data = self.get_index_data(symbol)
            if data:
                results[info['name']] = {
                    **data,
                    'type': info['type'],
                    'symbol': symbol
                }
        
        return results
    
    def get_currencies(self):
        """Döviz verilerini al"""
        results = {}
        
        for symbol, info in self.currencies.items():
            data = self.get_index_data(symbol)
            if data:
                results[info['name']] = {
                    **data,
                    'impact': info['impact'],
                    'symbol': symbol
                }
        
        return results
    
    def analyze_market_sentiment(self):
        """Genel piyasa sentiment'i"""
        indices = self.get_all_indices()
        
        if not indices:
            return {'sentiment': 'UNKNOWN', 'message': 'Veri alınamadı'}
        
        positive = 0
        negative = 0
        
        for name, data in indices.items():
            if data['change'] > 0:
                positive += 1
            else:
                negative += 1
        
        total = positive + negative
        
        if positive > negative * 1.5:
            sentiment = 'RISK_ON'
            message = 'Risk iştahı yüksek - Kripto için olumlu'
            crypto_impact = 'BULLISH'
        elif negative > positive * 1.5:
            sentiment = 'RISK_OFF'
            message = 'Risk iştahı düşük - Kripto için olumsuz'
            crypto_impact = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
            message = 'Karışık piyasa - Temkinli ol'
            crypto_impact = 'NEUTRAL'
        
        return {
            'sentiment': sentiment,
            'message': message,
            'crypto_impact': crypto_impact,
            'positive_count': positive,
            'negative_count': negative,
            'total_indices': total
        }
    
    def get_crypto_correlation_signals(self):
        """Kripto ile korelasyon sinyalleri"""
        sentiment = self.analyze_market_sentiment()
        commodities = self.get_commodities()
        currencies = self.get_currencies()
        
        signals = []
        
        # S&P500 korelasyonu
        if sentiment['crypto_impact'] == 'BULLISH':
            signals.append('📈 Hisse piyasaları yükselişte - BTC için olumlu')
        elif sentiment['crypto_impact'] == 'BEARISH':
            signals.append('📉 Hisse piyasaları düşüşte - BTC için olumsuz')
        
        # Altın
        if commodities.get('Altın'):
            gold = commodities['Altın']
            if gold['change'] > 1:
                signals.append('🥇 Altın yükselişte - Enflasyon endişesi, BTC olumlu')
            elif gold['change'] < -1:
                signals.append('🥇 Altın düşüşte - Risk iştahı artıyor')
        
        # DXY (ters korelasyon)
        if currencies.get('DXY (Dolar Endeksi)'):
            dxy = currencies['DXY (Dolar Endeksi)']
            if dxy['change'] > 0.5:
                signals.append('💵 Dolar güçleniyor - BTC için olumsuz')
            elif dxy['change'] < -0.5:
                signals.append('💵 Dolar zayıflıyor - BTC için olumlu')
        
        return {
            'market_sentiment': sentiment,
            'signals': signals,
            'indices': self.get_all_indices(),
            'commodities': commodities,
            'currencies': currencies
        }


if __name__ == '__main__':
    analyzer = GlobalMarketsAnalyzer()
    
    print("🌍 GLOBAL PİYASA ANALİZİ\n")
    
    result = analyzer.get_crypto_correlation_signals()
    
    print(f"Piyasa Sentiment: {result['market_sentiment']['sentiment']}")
    print(f"Kripto Etkisi: {result['market_sentiment']['crypto_impact']}")
    print(f"\nSinyaller:")
    for signal in result['signals']:
        print(f"  {signal}")
    
    print(f"\nEndeksler:")
    for name, data in result.get('indices', {}).items():
        print(f"  {name}: {data['price']} ({'+' if data['change'] > 0 else ''}{data['change']}%)")
