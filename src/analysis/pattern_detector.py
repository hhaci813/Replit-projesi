"""
Pattern Detector - Mum Formasyonu ve Pump/Dump Tespiti
Candlestick patterns, pump exhaustion, trend reversal detection
"""

import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PatternDetector:
    def __init__(self):
        self.patterns_detected = []
    
    def detect_candlestick_patterns(self, ohlcv_data):
        """
        OHLCV verilerinden mum formasyonlarını tespit et
        ohlcv_data: list of dicts with open, high, low, close, volume
        """
        if len(ohlcv_data) < 3:
            return []
        
        patterns = []
        
        for i in range(1, len(ohlcv_data)):
            candle = ohlcv_data[i]
            prev = ohlcv_data[i-1]
            
            o, h, l, c = candle['open'], candle['high'], candle['low'], candle['close']
            body = abs(c - o)
            upper_wick = h - max(o, c)
            lower_wick = min(o, c) - l
            total_range = h - l if h != l else 0.0001
            
            if body / total_range < 0.1:
                patterns.append({
                    'type': 'DOJI',
                    'signal': 'REVERSAL',
                    'strength': 'MEDIUM',
                    'index': i,
                    'description': 'Kararsızlık - trend değişimi olabilir'
                })
            
            if upper_wick > body * 2 and lower_wick < body * 0.5 and c < o:
                patterns.append({
                    'type': 'SHOOTING_STAR',
                    'signal': 'BEARISH',
                    'strength': 'STRONG',
                    'index': i,
                    'description': 'Zirve sinyali - düşüş beklenir'
                })
            
            if lower_wick > body * 2 and upper_wick < body * 0.5 and c > o:
                patterns.append({
                    'type': 'HAMMER',
                    'signal': 'BULLISH',
                    'strength': 'STRONG',
                    'index': i,
                    'description': 'Dip sinyali - yükseliş beklenir'
                })
            
            if lower_wick > body * 2 and upper_wick < body * 0.5 and c < o:
                patterns.append({
                    'type': 'HANGING_MAN',
                    'signal': 'BEARISH',
                    'strength': 'MEDIUM',
                    'index': i,
                    'description': 'Zirve uyarısı - dikkat'
                })
            
            prev_body = abs(prev['close'] - prev['open'])
            if body > prev_body * 1.5:
                if prev['close'] < prev['open'] and c > o and c > prev['open']:
                    patterns.append({
                        'type': 'BULLISH_ENGULFING',
                        'signal': 'BULLISH',
                        'strength': 'STRONG',
                        'index': i,
                        'description': 'Güçlü yükseliş sinyali'
                    })
                elif prev['close'] > prev['open'] and c < o and c < prev['open']:
                    patterns.append({
                        'type': 'BEARISH_ENGULFING',
                        'signal': 'BEARISH',
                        'strength': 'STRONG',
                        'index': i,
                        'description': 'Güçlü düşüş sinyali'
                    })
        
        return patterns
    
    def detect_pump_dump(self, prices, volumes, threshold_price=0.15, threshold_vol=2.0):
        """
        Pump & Dump tespiti
        - Ani fiyat artışı (%15+)
        - Volume spike (2x ortalama)
        - Sonraki düşüş
        """
        if len(prices) < 10 or len(volumes) < 10:
            return None
        
        result = {
            'is_pump': False,
            'is_post_pump_dump': False,
            'pump_peak': None,
            'current_drawdown': 0,
            'signal': 'NEUTRAL'
        }
        
        recent_high = max(prices[-24:]) if len(prices) >= 24 else max(prices)
        current = prices[-1]
        drawdown = (recent_high - current) / recent_high * 100
        
        avg_vol = np.mean(volumes[:-5]) if len(volumes) > 5 else np.mean(volumes)
        max_recent_vol = max(volumes[-5:]) if len(volumes) >= 5 else volumes[-1]
        vol_spike = max_recent_vol / avg_vol if avg_vol > 0 else 1
        
        price_24h_change = (prices[-1] - prices[-24]) / prices[-24] * 100 if len(prices) >= 24 else 0
        
        if vol_spike > threshold_vol and price_24h_change > threshold_price * 100:
            result['is_pump'] = True
            result['signal'] = 'PUMP_ACTIVE'
        
        if drawdown > 10 and vol_spike > 1.5:
            result['is_post_pump_dump'] = True
            result['pump_peak'] = recent_high
            result['current_drawdown'] = drawdown
            result['signal'] = 'POST_PUMP_DUMP'
        
        return result
    
    def detect_trend_exhaustion(self, prices, rsi=None, macd_hist=None):
        """
        Trend bitim sinyalleri
        - Zirveye yakınlık
        - RSI aşırı bölge
        - MACD histogram azalması
        """
        if len(prices) < 14:
            return None
        
        recent_high = max(prices[-30:]) if len(prices) >= 30 else max(prices)
        recent_low = min(prices[-30:]) if len(prices) >= 30 else min(prices)
        current = prices[-1]
        price_range = recent_high - recent_low if recent_high != recent_low else 0.0001
        
        position_pct = (current - recent_low) / price_range * 100
        
        from_high_pct = (recent_high - current) / recent_high * 100
        from_low_pct = (current - recent_low) / recent_low * 100 if recent_low > 0 else 0
        
        result = {
            'position_pct': position_pct,
            'from_high_pct': from_high_pct,
            'from_low_pct': from_low_pct,
            'exhaustion_signal': 'NEUTRAL',
            'strength': 0
        }
        
        if position_pct > 85:
            result['exhaustion_signal'] = 'OVERBOUGHT_ZONE'
            result['strength'] = min(100, position_pct)
        elif position_pct < 15:
            result['exhaustion_signal'] = 'OVERSOLD_ZONE'
            result['strength'] = min(100, 100 - position_pct)
        
        if from_high_pct > 15 and position_pct < 50:
            result['exhaustion_signal'] = 'DOWNTREND_ACTIVE'
            result['strength'] = min(100, from_high_pct * 3)
        
        return result
    
    def calculate_pattern_score(self, patterns, pump_result, exhaustion):
        """
        Tüm pattern sinyallerinden birleşik skor hesapla
        Negatif = Bearish, Pozitif = Bullish
        """
        score = 0
        signals = []
        
        if patterns:
            for p in patterns[-3:]:
                if p['signal'] == 'BEARISH':
                    score -= 25 if p['strength'] == 'STRONG' else 15
                    signals.append(f"🔴 {p['type']}: {p['description']}")
                elif p['signal'] == 'BULLISH':
                    score += 25 if p['strength'] == 'STRONG' else 15
                    signals.append(f"🟢 {p['type']}: {p['description']}")
                else:
                    signals.append(f"🟡 {p['type']}: {p['description']}")
        
        if pump_result:
            if pump_result['signal'] == 'POST_PUMP_DUMP':
                score -= 40
                signals.append(f"⚠️ PUMP SONRASI DÜŞÜŞ: %{pump_result['current_drawdown']:.1f} aşağıda")
            elif pump_result['signal'] == 'PUMP_ACTIVE':
                score -= 20
                signals.append("⚠️ PUMP AKTİF - Riskli!")
        
        if exhaustion:
            if exhaustion['exhaustion_signal'] == 'OVERBOUGHT_ZONE':
                score -= 20
                signals.append(f"📊 ZİRVE BÖLGESİ: %{exhaustion['position_pct']:.0f}")
            elif exhaustion['exhaustion_signal'] == 'OVERSOLD_ZONE':
                score += 20
                signals.append(f"📊 DİP BÖLGESİ: %{exhaustion['position_pct']:.0f}")
            elif exhaustion['exhaustion_signal'] == 'DOWNTREND_ACTIVE':
                score -= 30
                signals.append(f"📉 DÜŞÜŞ TRENDİ: Zirveden %{exhaustion['from_high_pct']:.1f} aşağıda")
        
        return {
            'pattern_score': score,
            'signals': signals,
            'overall': 'BEARISH' if score < -20 else 'BULLISH' if score > 20 else 'NEUTRAL'
        }
    
    def analyze_full(self, ohlcv_data, volumes=None):
        """
        Tam pattern analizi yap
        """
        if not ohlcv_data or len(ohlcv_data) < 5:
            return None
        
        prices = [c['close'] for c in ohlcv_data]
        if volumes is None:
            volumes = [c.get('volume', 1) for c in ohlcv_data]
        
        patterns = self.detect_candlestick_patterns(ohlcv_data)
        pump_result = self.detect_pump_dump(prices, volumes)
        exhaustion = self.detect_trend_exhaustion(prices)
        
        score_result = self.calculate_pattern_score(patterns, pump_result, exhaustion)
        
        return {
            'candlestick_patterns': patterns,
            'pump_dump': pump_result,
            'trend_exhaustion': exhaustion,
            'pattern_score': score_result['pattern_score'],
            'signals': score_result['signals'],
            'overall_signal': score_result['overall']
        }


def ohlcv_from_yfinance(ticker_data):
    """YFinance DataFrame'i OHLCV listesine çevir"""
    ohlcv = []
    for idx, row in ticker_data.iterrows():
        ohlcv.append({
            'open': row['Open'],
            'high': row['High'],
            'low': row['Low'],
            'close': row['Close'],
            'volume': row.get('Volume', 0),
            'date': idx
        })
    return ohlcv


pattern_detector = PatternDetector()
