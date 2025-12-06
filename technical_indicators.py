"""📊 TECHNICAL INDICATORS - GERÇEK TEKNİK ANALİZ
RSI, MACD, Bollinger Bands, Moving Averages
"""
import numpy as np
from datetime import datetime

class TechnicalIndicators:
    """Gerçek teknik gösterge hesaplamaları"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """RSI (Relative Strength Index) hesapla"""
        if len(prices) < period + 1:
            return 50  # Yeterli veri yok
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """MACD hesapla"""
        if len(prices) < slow:
            return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'NEUTRAL'}
        
        prices = np.array(prices)
        
        # EMA hesapla
        def ema(data, period):
            alpha = 2 / (period + 1)
            result = [data[0]]
            for price in data[1:]:
                result.append(alpha * price + (1 - alpha) * result[-1])
            return np.array(result)
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        # Son değerler
        macd_val = macd_line[-1]
        signal_val = signal_line[-1]
        hist_val = histogram[-1]
        
        # Trend
        if hist_val > 0 and macd_val > signal_val:
            trend = 'BULLISH'
        elif hist_val < 0 and macd_val < signal_val:
            trend = 'BEARISH'
        else:
            trend = 'NEUTRAL'
        
        return {
            'macd': round(macd_val, 4),
            'signal': round(signal_val, 4),
            'histogram': round(hist_val, 4),
            'trend': trend
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Bollinger Bands hesapla"""
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'position': 'NEUTRAL'}
        
        prices = np.array(prices[-period:])
        
        middle = np.mean(prices)
        std = np.std(prices)
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        current_price = prices[-1]
        
        # Pozisyon
        if current_price > upper:
            position = 'OVERBOUGHT'
        elif current_price < lower:
            position = 'OVERSOLD'
        elif current_price > middle:
            position = 'UPPER_HALF'
        else:
            position = 'LOWER_HALF'
        
        return {
            'upper': round(upper, 4),
            'middle': round(middle, 4),
            'lower': round(lower, 4),
            'position': position
        }
    
    @staticmethod
    def calculate_moving_averages(prices):
        """Moving Averages hesapla"""
        result = {}
        
        if len(prices) >= 7:
            result['ma7'] = round(np.mean(prices[-7:]), 4)
        if len(prices) >= 20:
            result['ma20'] = round(np.mean(prices[-20:]), 4)
        if len(prices) >= 50:
            result['ma50'] = round(np.mean(prices[-50:]), 4)
        
        current = prices[-1] if prices else 0
        
        # Trend belirleme
        if 'ma7' in result and 'ma20' in result:
            if current > result['ma7'] > result['ma20']:
                result['trend'] = 'STRONG_BULLISH'
            elif current > result['ma7']:
                result['trend'] = 'BULLISH'
            elif current < result['ma7'] < result['ma20']:
                result['trend'] = 'STRONG_BEARISH'
            elif current < result['ma7']:
                result['trend'] = 'BEARISH'
            else:
                result['trend'] = 'NEUTRAL'
        else:
            result['trend'] = 'INSUFFICIENT_DATA'
        
        return result
    
    @staticmethod
    def get_full_analysis(prices):
        """Tüm teknik analizi birleştir"""
        if not prices or len(prices) < 14:
            return {'error': 'Yetersiz veri'}
        
        rsi = TechnicalIndicators.calculate_rsi(prices)
        macd = TechnicalIndicators.calculate_macd(prices)
        bb = TechnicalIndicators.calculate_bollinger_bands(prices)
        ma = TechnicalIndicators.calculate_moving_averages(prices)
        
        # Genel skor hesapla
        score = 50
        signals = []
        
        # RSI
        if rsi < 30:
            score += 20
            signals.append('RSI aşırı satım (AL sinyali)')
        elif rsi > 70:
            score -= 20
            signals.append('RSI aşırı alım (SAT sinyali)')
        elif rsi < 50:
            score += 5
        else:
            score -= 5
        
        # MACD
        if macd['trend'] == 'BULLISH':
            score += 15
            signals.append('MACD yükseliş')
        elif macd['trend'] == 'BEARISH':
            score -= 15
            signals.append('MACD düşüş')
        
        # Bollinger
        if bb['position'] == 'OVERSOLD':
            score += 15
            signals.append('Bollinger alt banda yakın (AL)')
        elif bb['position'] == 'OVERBOUGHT':
            score -= 15
            signals.append('Bollinger üst banda yakın (SAT)')
        
        # MA trend
        if ma.get('trend') == 'STRONG_BULLISH':
            score += 10
            signals.append('MA güçlü yükseliş trendi')
        elif ma.get('trend') == 'STRONG_BEARISH':
            score -= 10
            signals.append('MA güçlü düşüş trendi')
        
        # Sonuç
        if score >= 80:
            recommendation = 'STRONG_BUY'
        elif score >= 60:
            recommendation = 'BUY'
        elif score >= 40:
            recommendation = 'HOLD'
        elif score >= 20:
            recommendation = 'SELL'
        else:
            recommendation = 'STRONG_SELL'
        
        return {
            'rsi': rsi,
            'macd': macd,
            'bollinger': bb,
            'moving_averages': ma,
            'score': min(100, max(0, score)),
            'signals': signals,
            'recommendation': recommendation
        }


if __name__ == '__main__':
    # Test
    import random
    prices = [100 + random.uniform(-5, 5) for _ in range(50)]
    
    ti = TechnicalIndicators()
    result = ti.get_full_analysis(prices)
    
    print("📊 TEKNIK ANALIZ SONUCU")
    print(f"RSI: {result['rsi']}")
    print(f"MACD: {result['macd']}")
    print(f"Bollinger: {result['bollinger']}")
    print(f"MA: {result['moving_averages']}")
    print(f"Skor: {result['score']}/100")
    print(f"Tavsiye: {result['recommendation']}")
    print(f"Sinyaller: {result['signals']}")
