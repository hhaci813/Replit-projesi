"""
Composite Signal Engine - MAX VERSION
- Multi-timeframe analiz
- Fear & Greed Index
- Funding Rates
- Dengeli skor sistemi
"""

import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CompositeSignalEngine:
    def __init__(self):
        # Dengeli eşikler (önceki çok sıkıydı)
        self.thresholds = {
            'STRONG_BUY': 75,    # Güçlü sinyal
            'BUY': 65,           # Al sinyali
            'WATCH': 50,         # İzle
            'NEUTRAL': 40,       # Nötr
            'AVOID': 25,         # Uzak dur
            'SELL': 0            # Sat
        }
        
        # Market data provider
        self.market_data = None
        self._init_market_data()
        
        # Timeframe ağırlıkları
        self.tf_weights = {
            '15m': 0.15,
            '1h': 0.25,
            '4h': 0.35,
            '1d': 0.25
        }
    
    def _init_market_data(self):
        try:
            from src.analysis.market_data import MarketDataProvider
            self.market_data = MarketDataProvider()
        except Exception as e:
            logger.warning(f"Market data init failed: {e}")
            self.market_data = None
    
    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 1)
    
    def calculate_macd(self, prices):
        if len(prices) < 26:
            return {'trend': 'NEUTRAL', 'histogram': 0, 'crossover': False}
        
        prices = np.array(prices)
        def ema(data, period):
            alpha = 2 / (period + 1)
            result = [data[0]]
            for price in data[1:]:
                result.append(alpha * price + (1 - alpha) * result[-1])
            return np.array(result)
        
        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd = ema12 - ema26
        signal = ema(macd, 9)
        hist = macd[-1] - signal[-1]
        prev_hist = macd[-2] - signal[-2] if len(macd) > 1 else hist
        
        crossover = (hist > 0 and prev_hist < 0) or (hist < 0 and prev_hist > 0)
        trend = 'BULLISH' if hist > 0 else 'BEARISH'
        
        return {'trend': trend, 'histogram': hist, 'crossover': crossover}
    
    def calculate_ema_stack(self, prices):
        """EMA 7/21/50 stack analizi"""
        if len(prices) < 50:
            return {'aligned': False, 'direction': 'NEUTRAL'}
        
        def ema(data, period):
            alpha = 2 / (period + 1)
            result = [data[0]]
            for price in data[1:]:
                result.append(alpha * price + (1 - alpha) * result[-1])
            return result[-1]
        
        ema7 = ema(prices, 7)
        ema21 = ema(prices, 21)
        ema50 = ema(prices, 50)
        current = prices[-1]
        
        # Bullish stack: price > ema7 > ema21 > ema50
        if current > ema7 > ema21 > ema50:
            return {'aligned': True, 'direction': 'BULLISH', 'strength': 'STRONG'}
        elif current > ema7 > ema21:
            return {'aligned': True, 'direction': 'BULLISH', 'strength': 'MEDIUM'}
        # Bearish stack
        elif current < ema7 < ema21 < ema50:
            return {'aligned': True, 'direction': 'BEARISH', 'strength': 'STRONG'}
        elif current < ema7 < ema21:
            return {'aligned': True, 'direction': 'BEARISH', 'strength': 'MEDIUM'}
        
        return {'aligned': False, 'direction': 'NEUTRAL', 'strength': 'WEAK'}
    
    def detect_pump_dump(self, prices, volumes):
        """Gelişmiş pump/dump tespiti"""
        if len(prices) < 20 or len(volumes) < 20:
            return {'is_pump': False, 'is_dump': False, 'risk': 0}
        
        # Son 24 mum
        recent_high = max(prices[-24:])
        recent_low = min(prices[-24:])
        current = prices[-1]
        
        # Drawdown hesapla
        drawdown = (recent_high - current) / recent_high * 100 if recent_high > 0 else 0
        
        # Volume spike
        avg_vol = np.mean(volumes[:-5])
        recent_max_vol = max(volumes[-5:])
        vol_spike = recent_max_vol / avg_vol if avg_vol > 0 else 1
        
        # Fiyat değişimi
        price_change = (prices[-1] - prices[-5]) / prices[-5] * 100 if prices[-5] > 0 else 0
        
        result = {
            'is_pump': False,
            'is_dump': False,
            'drawdown': drawdown,
            'vol_spike': vol_spike,
            'risk': 0
        }
        
        # Pump tespiti: Yüksek volume + hızlı artış
        if vol_spike > 3 and price_change > 15:
            result['is_pump'] = True
            result['risk'] = 80
        elif vol_spike > 2 and price_change > 10:
            result['is_pump'] = True
            result['risk'] = 60
        
        # Post-pump dump tespiti: Yüksek zirveden düşüş
        if drawdown > 15 and vol_spike > 1.5:
            result['is_dump'] = True
            result['risk'] = max(result['risk'], 70)
        elif drawdown > 10:
            result['is_dump'] = True
            result['risk'] = max(result['risk'], 50)
        
        return result
    
    def analyze_timeframe(self, ohlcv_data):
        """Tek timeframe için analiz"""
        if not ohlcv_data or len(ohlcv_data) < 10:
            return None
        
        prices = [c['close'] for c in ohlcv_data]
        volumes = [c['volume'] for c in ohlcv_data]
        
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        ema_stack = self.calculate_ema_stack(prices)
        pump_dump = self.detect_pump_dump(prices, volumes)
        
        # Bu timeframe için skor hesapla - DENGELI
        score = 50
        signals = []
        
        # RSI - daha dengeli
        if rsi < 25:
            score += 15
            signals.append(f"RSI {rsi:.0f} AŞIRI SATIM - fırsat!")
        elif rsi < 35:
            score += 8
            signals.append(f"RSI {rsi:.0f} alım bölgesi")
        elif rsi > 75:
            score -= 12
            signals.append(f"RSI {rsi:.0f} AŞIRI ALIM")
        elif rsi > 65:
            score -= 5
        
        # MACD - daha az ağırlık
        if macd['trend'] == 'BULLISH':
            score += 10
            if macd['crossover']:
                score += 8
                signals.append("MACD bullish crossover!")
        else:
            score -= 8  # Eskisi -15'ti, çok fazlaydı
            if macd['crossover']:
                score -= 5
                signals.append("MACD bearish")
        
        # EMA Stack - daha dengeli
        if ema_stack['aligned']:
            if ema_stack['direction'] == 'BULLISH':
                score += 12 if ema_stack['strength'] == 'STRONG' else 6
                signals.append(f"EMA BULLISH ({ema_stack['strength']})")
            else:
                score -= 10 if ema_stack['strength'] == 'STRONG' else 5
                signals.append(f"EMA BEARISH")
        
        # Pump/Dump riski
        if pump_dump['risk'] > 50:
            score -= pump_dump['risk'] // 2
            if pump_dump['is_pump']:
                signals.append(f"⚠️ PUMP tespit! Risk: {pump_dump['risk']}")
            if pump_dump['is_dump']:
                signals.append(f"⚠️ DUMP! Düşüş: %{pump_dump['drawdown']:.1f}")
        
        return {
            'score': max(0, min(100, score)),
            'rsi': rsi,
            'macd': macd,
            'ema_stack': ema_stack,
            'pump_dump': pump_dump,
            'signals': signals
        }
    
    def analyze_multi_timeframe(self, multi_tf_data):
        """
        Multi-timeframe analiz
        multi_tf_data: {'15m': [...], '1h': [...], '4h': [...], '1d': [...]}
        """
        results = {}
        weighted_score = 0
        all_signals = []
        
        for tf, ohlcv in multi_tf_data.items():
            analysis = self.analyze_timeframe(ohlcv)
            if analysis:
                results[tf] = analysis
                weight = self.tf_weights.get(tf, 0.25)
                weighted_score += analysis['score'] * weight
                
                # En önemli sinyalleri ekle
                for sig in analysis['signals'][:2]:
                    all_signals.append(f"[{tf}] {sig}")
        
        # Timeframe uyumu kontrolü
        tf_directions = []
        for tf, r in results.items():
            if r.get('ema_stack', {}).get('aligned'):
                tf_directions.append(r['ema_stack']['direction'])
        
        # Tüm timeframe'ler aynı yönde mi?
        alignment = 'NONE'
        if tf_directions:
            if all(d == 'BULLISH' for d in tf_directions):
                alignment = 'BULLISH'
                weighted_score += 10
            elif all(d == 'BEARISH' for d in tf_directions):
                alignment = 'BEARISH'
                weighted_score -= 10
        
        # Pump/dump riski kontrolü
        max_risk = 0
        for tf, r in results.items():
            if r.get('pump_dump', {}).get('risk', 0) > max_risk:
                max_risk = r['pump_dump']['risk']
        
        if max_risk > 60:
            weighted_score -= 15
        
        # Market sentiment bonus/ceza ekle
        market_sentiment = None
        if self.market_data:
            try:
                market_sentiment = self.market_data.get_market_sentiment_score()
                sentiment_adjustment = (market_sentiment['score'] - 50) / 5  # -10 ile +10 arası
                weighted_score += sentiment_adjustment
                
                # Fear & Greed sinyalleri ekle
                for sig in market_sentiment.get('signals', [])[:2]:
                    all_signals.append(sig)
            except Exception as e:
                logger.warning(f"Market sentiment error: {e}")
        
        final_score = max(0, min(100, weighted_score))
        
        # Sinyal üret
        if final_score >= self.thresholds['STRONG_BUY'] and alignment == 'BULLISH':
            signal = 'STRONG_BUY'
            prediction = '🟢🟢 GÜÇLÜ AL'
        elif final_score >= self.thresholds['BUY']:
            signal = 'BUY'
            prediction = '🟢 AL'
        elif final_score >= self.thresholds['WATCH']:
            signal = 'WATCH'
            prediction = '🟡 İZLE'
        elif final_score >= self.thresholds['NEUTRAL']:
            signal = 'NEUTRAL'
            prediction = '⚪ NÖTR'
        elif final_score >= self.thresholds['AVOID']:
            signal = 'AVOID'
            prediction = '🔴 UZAK DUR'
        else:
            signal = 'SELL'
            prediction = '🔴🔴 SAT'
        
        return {
            'score': final_score,
            'signal': signal,
            'prediction': prediction,
            'alignment': alignment,
            'pump_risk': max_risk,
            'timeframes': results,
            'signals': all_signals[:6],
            'confidence': 'HIGH' if alignment != 'NONE' and max_risk < 30 else 'MEDIUM' if len(results) >= 2 else 'LOW',
            'market_sentiment': market_sentiment
        }


composite_engine = CompositeSignalEngine()
