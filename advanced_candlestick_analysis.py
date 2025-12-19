"""
🕯️ İLERİ MUM ANALZ SİSTEMİ
Her mum hakkında detaylı bilgi - body, wick, shade, pattern kombinasyonları
"""

from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class CandleInfo:
    open: float
    high: float
    low: float
    close: float
    volume: float
    
class AdvancedCandlestickAnalyzer:
    """Mumlar hakkında her bilgiye sahip sistem"""
    
    def analyze_single_candle(self, candle: CandleInfo) -> Dict:
        """1 mumun tüm özelliklerini analiz et"""
        
        # Temel ölçüler
        body_height = abs(candle.close - candle.open)
        total_range = candle.high - candle.low
        upper_wick = candle.high - max(candle.open, candle.close)
        lower_wick = min(candle.open, candle.close) - candle.low
        
        # Oranlar
        body_ratio = body_height / total_range if total_range > 0 else 0
        wick_ratio = (upper_wick + lower_wick) / total_range if total_range > 0 else 0
        
        # Mum tipi
        is_bullish = candle.close > candle.open
        is_doji = body_height < (total_range * 0.1)
        is_marubozu = body_height > (total_range * 0.8) and (upper_wick + lower_wick) < (total_range * 0.2)
        
        # Wick karakteristikleri
        upper_wick_ratio = upper_wick / total_range if total_range > 0 else 0
        lower_wick_ratio = lower_wick / total_range if total_range > 0 else 0
        
        candle_type = self._classify_candle(candle, body_ratio, is_doji, is_marubozu)
        strength = self._calculate_candle_strength(is_bullish, body_ratio, upper_wick_ratio, lower_wick_ratio)
        
        return {
            'type': candle_type,
            'is_bullish': is_bullish,
            'body_height': round(body_height, 8),
            'total_range': round(total_range, 8),
            'body_ratio': round(body_ratio * 100, 1),  # % body of total
            'wick_ratio': round(wick_ratio * 100, 1),  # % wick of total
            'upper_wick': round(upper_wick, 8),
            'lower_wick': round(lower_wick, 8),
            'upper_wick_ratio': round(upper_wick_ratio * 100, 1),
            'lower_wick_ratio': round(lower_wick_ratio * 100, 1),
            'strength': strength,  # 0-10 (0=zayıf, 10=güçlü)
            'open': candle.open,
            'close': candle.close,
            'high': candle.high,
            'low': candle.low,
            'volume': candle.volume,
        }
    
    def _classify_candle(self, candle: CandleInfo, body_ratio: float, is_doji: bool, is_marubozu: bool) -> str:
        """Mum tipini belirle"""
        is_bullish = candle.close > candle.open
        
        if is_doji:
            return "DOJI"
        if is_marubozu:
            return "BULLISH_MARUBOZU" if is_bullish else "BEARISH_MARUBOZU"
        if body_ratio > 0.7:
            return "STRONG_BULLISH" if is_bullish else "STRONG_BEARISH"
        if body_ratio < 0.3:
            return "SMALL_BODY"
        return "NORMAL"
    
    def _calculate_candle_strength(self, is_bullish: bool, body_ratio: float, 
                                  upper_wick_ratio: float, lower_wick_ratio: float) -> int:
        """Mum gücünü 0-10 ölçeğinde hesapla"""
        strength = 0
        
        # Gövde gücü
        strength += body_ratio * 6
        
        # Bullish/Bearish yönü
        if is_bullish:
            strength += lower_wick_ratio * 2  # Alt wick = rejection
        else:
            strength += upper_wick_ratio * 2  # Üst wick = rejection
        
        # Max 10
        return min(int(strength), 10)
    
    def analyze_candle_sequence(self, candles: List[CandleInfo]) -> Dict:
        """Ardışık mumları analiz et - formasyonlar, momentumlar"""
        if len(candles) < 2:
            return {'error': 'Min 2 mum gerekli'}
        
        analyzed = [self.analyze_single_candle(c) for c in candles]
        
        # Mum kombinasyonları
        formations = self._find_formations(analyzed)
        
        # Trend momentumu
        momentum = self._calculate_momentum(analyzed)
        
        # Volume trend
        volume_trend = self._analyze_volume_trend(analyzed)
        
        return {
            'total_candles': len(analyzed),
            'candles': analyzed,
            'formations': formations,
            'momentum': momentum,
            'volume_trend': volume_trend,
            'bullish_count': sum(1 for c in analyzed if c['is_bullish']),
            'bearish_count': sum(1 for c in analyzed if not c['is_bullish']),
        }
    
    def _find_formations(self, candles: List[Dict]) -> List[Dict]:
        """Mum kombinasyon formasyonlarını tespit et"""
        formations = []
        
        # 3 White Soldiers (3 bullish güçlü mumlar)
        if len(candles) >= 3:
            last_3 = candles[-3:]
            if all(c['is_bullish'] for c in last_3) and all(c['strength'] >= 6 for c in last_3):
                formations.append({
                    'name': '3 White Soldiers',
                    'reliability': '72%',
                    'signal': 'STRONG_BUY',
                    'description': 'Güçlü yükseliş (3 güçlü bullish mum)'
                })
        
        # Morning Star (bearish-doji/small-bullish)
        if len(candles) >= 3:
            if candles[-3]['is_bullish'] == False and candles[-1]['is_bullish'] and candles[-2]['strength'] <= 3:
                formations.append({
                    'name': 'Morning Star',
                    'reliability': '72%',
                    'signal': 'BUY',
                    'description': 'Düşüşten dönüş (bullish reversal)'
                })
        
        # Engulfing Pattern
        if len(candles) >= 2:
            prev, curr = candles[-2], candles[-1]
            if prev['is_bullish'] != curr['is_bullish']:
                if curr['body_height'] > prev['body_height'] * 1.2:
                    pattern_name = 'Bullish Engulfing' if curr['is_bullish'] else 'Bearish Engulfing'
                    formations.append({
                        'name': pattern_name,
                        'reliability': '62%',
                        'signal': 'BUY' if curr['is_bullish'] else 'SELL',
                        'description': f'{pattern_name} (ters yönde güçlü mum)'
                    })
        
        return formations
    
    def _calculate_momentum(self, candles: List[Dict]) -> Dict:
        """Mum momentumunu hesapla"""
        if len(candles) < 3:
            return {'momentum': 0, 'trend': 'UNKNOWN'}
        
        # Son 3 mumun yönü
        last_3_bullish = sum(1 for c in candles[-3:] if c['is_bullish'])
        
        # Güç
        avg_strength = np.mean([c['strength'] for c in candles[-3:]])
        
        if last_3_bullish >= 2:
            trend = 'BULLISH'
        elif last_3_bullish <= 1:
            trend = 'BEARISH'
        else:
            trend = 'NEUTRAL'
        
        momentum_value = (last_3_bullish - 1.5) * 10  # -10 to +10
        
        return {
            'trend': trend,
            'momentum': round(momentum_value, 1),
            'strength_avg': round(avg_strength, 1),
            'confidence': self._get_momentum_confidence(trend, avg_strength)
        }
    
    def _analyze_volume_trend(self, candles: List[Dict]) -> Dict:
        """Volume trendini analiz et"""
        volumes = [c['volume'] for c in candles]
        
        if len(volumes) < 2:
            return {'trend': 'UNKNOWN'}
        
        avg_volume = np.mean(volumes)
        last_volume = volumes[-1]
        
        volume_change = ((last_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0
        
        return {
            'avg_volume': round(avg_volume, 0),
            'last_volume': round(last_volume, 0),
            'volume_change_percent': round(volume_change, 1),
            'trend': 'INCREASING' if volume_change > 10 else 'DECREASING' if volume_change < -10 else 'STABLE'
        }
    
    def _get_momentum_confidence(self, trend: str, strength: float) -> str:
        """Momentum güvenilirliği"""
        if strength >= 7:
            return 'VERY_HIGH'
        elif strength >= 5:
            return 'HIGH'
        elif strength >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_detailed_message(self, candles: List[CandleInfo]) -> str:
        """Detaylı analiz mesajı"""
        analysis = self.analyze_candle_sequence(candles)
        
        msg = "🕯️ İLERİ MUM ANALZ\n"
        msg += "="*50 + "\n\n"
        
        # Son 5 mumun özeti
        msg += f"📊 SON {min(5, len(candles))} MUM:\n"
        for i, candle in enumerate(analysis['candles'][-5:]):
            emoji = "🟢" if candle['is_bullish'] else "🔴"
            msg += f"{emoji} {candle['type']:20} | Güç: {candle['strength']}/10 | Body: {candle['body_ratio']:.0f}%\n"
        
        # Momentum
        msg += f"\n⚡ MOMENTUM:\n"
        mom = analysis['momentum']
        msg += f"   Trend: {mom['trend']} ({mom['momentum']:+.0f})\n"
        msg += f"   Güven: {mom['confidence']}\n"
        
        # Volume
        msg += f"\n📈 VOLUME:\n"
        vol = analysis['volume_trend']
        msg += f"   Trend: {vol['trend']}\n"
        msg += f"   Değişim: {vol['volume_change_percent']:+.1f}%\n"
        
        # Formasyonlar
        if analysis['formations']:
            msg += f"\n🎯 FORMASYONLAR:\n"
            for form in analysis['formations']:
                msg += f"   {form['name']} ({form['reliability']})\n"
                msg += f"   Signal: {form['signal']}\n"
        
        return msg
