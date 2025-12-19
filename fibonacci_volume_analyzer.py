"""
🎯 FİBONACCİ + VOLUME PROFİLE ANALZ
Fibonacci seviyeleri, Volume at Price, VWAP
"""

from typing import List, Dict
import numpy as np

class FibonacciAnalyzer:
    """Fibonacci retracement ve extension seviyeleri"""
    
    def calculate_fibonacci_levels(self, high: float, low: float) -> Dict:
        """Fibonacci retracement ve extension seviyeleri"""
        
        diff = high - low
        
        # Retracement Levels
        levels = {
            '0.0%': high,
            '23.6%': high - (diff * 0.236),
            '38.2%': high - (diff * 0.382),
            '50.0%': high - (diff * 0.5),
            '61.8%': high - (diff * 0.618),
            '78.6%': high - (diff * 0.786),
            '100.0%': low,
        }
        
        # Extension Levels (downtrend'de)
        levels['127.2%'] = low - (diff * 0.272)
        levels['161.8%'] = low - (diff * 0.618)
        levels['261.8%'] = low - (diff * 1.618)
        
        return {
            'retracement_levels': {k: round(v, 2) for k, v in levels.items()},
            'high': high,
            'low': low,
            'range': diff,
            'key_levels': {
                '38.2%': round(high - (diff * 0.382), 2),
                '61.8%': round(high - (diff * 0.618), 2),
                '161.8% Extension': round(low - (diff * 0.618), 2)
            }
        }
    
    def analyze_fibonacci_touches(self, prices: List[float], fib_levels: Dict) -> Dict:
        """Fibonacci seviyelerine dokunuş analizi"""
        
        touches = {}
        
        for level_name, level_price in fib_levels.items():
            count = 0
            bounces = 0
            
            for i in range(1, len(prices) - 1):
                # %1 tolerance
                if abs(prices[i] - level_price) / level_price < 0.01:
                    count += 1
                    # Bounce kontrolü
                    if (prices[i-1] < level_price < prices[i+1]) or \
                       (prices[i-1] > level_price > prices[i+1]):
                        bounces += 1
            
            if count > 0:
                touches[level_name] = {
                    'touches': count,
                    'bounces': bounces,
                    'importance': 'STRONG' if count >= 2 else 'MODERATE'
                }
        
        return touches


class VolumeProfileAnalyzer:
    """Volume at Price - hangi fiyat seviyesinde çok işlem"""
    
    def calculate_volume_profile(self, prices: List[float], volumes: List[float], 
                                bins: int = 20) -> Dict:
        """Volume profile hesapla"""
        
        if len(prices) != len(volumes) or len(prices) < 2:
            return {'error': 'Veri hatası'}
        
        price_min = min(prices)
        price_max = max(prices)
        
        # Price bins
        bin_edges = np.linspace(price_min, price_max, bins + 1)
        bin_volume = np.zeros(bins)
        
        for price, volume in zip(prices, volumes):
            bin_idx = min(int((price - price_min) / (price_max - price_min) * bins), bins - 1)
            bin_volume[bin_idx] += volume
        
        # En yüksek volume alanları
        top_indices = np.argsort(bin_volume)[-5:][::-1]
        
        poc = bin_edges[top_indices[0]]  # Point of Control
        
        return {
            'point_of_control': round(poc, 2),  # En çok işlem yapılan fiyat
            'volume_distribution': {
                'high_volume_zones': [
                    {
                        'price_range': f"₺{bin_edges[i]:.2f} - ₺{bin_edges[i+1]:.2f}",
                        'volume': round(bin_volume[i], 0),
                        'strength': 'VERY_HIGH' if i == top_indices[0] else 'HIGH'
                    }
                    for i in top_indices if bin_volume[i] > 0
                ]
            },
            'analysis': self._interpret_volume_profile(bin_volume, poc, prices[-1])
        }
    
    def _interpret_volume_profile(self, bin_volume: np.ndarray, poc: float, current_price: float) -> Dict:
        """Volume profili yorumla"""
        
        if current_price > poc:
            trend = "BULLISH (Fiyat POC üstünde)"
            interpretation = "Alıcılar hakim - Yükseliş baskısı var"
        elif current_price < poc:
            trend = "BEARISH (Fiyat POC altında)"
            interpretation = "Satıcılar hakim - Düşüş baskısı var"
        else:
            trend = "NEUTRAL"
            interpretation = "Fiyat POC'de - Karar beklenti"
        
        return {
            'trend': trend,
            'interpretation': interpretation,
            'price_vs_poc': f"{'+' if current_price > poc else ''}{((current_price - poc) / poc * 100):.2f}%"
        }
    
    def calculate_vwap(self, highs: List[float], lows: List[float], 
                      closes: List[float], volumes: List[float]) -> Dict:
        """Volume Weighted Average Price"""
        
        if len(closes) != len(volumes):
            return {'error': 'Veri uzunluğu uyumsuz'}
        
        # Typical price = (H + L + C) / 3
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        
        # VWAP = Σ(TP × V) / Σ(V)
        tp_volume = [tp * v for tp, v in zip(typical_prices, volumes)]
        vwap = sum(tp_volume) / sum(volumes) if sum(volumes) > 0 else 0
        
        # Distance from VWAP
        current_price = closes[-1]
        distance_percent = ((current_price - vwap) / vwap * 100) if vwap > 0 else 0
        
        return {
            'vwap': round(vwap, 2),
            'current_price': current_price,
            'distance_percent': round(distance_percent, 2),
            'position': 'ABOVE_VWAP' if current_price > vwap else 'BELOW_VWAP',
            'strength': self._calculate_vwap_strength(current_price, vwap)
        }
    
    def _calculate_vwap_strength(self, current: float, vwap: float) -> str:
        """VWAP'ten ne kadar uzak - ne kadar güçlü"""
        distance = abs(current - vwap) / vwap * 100
        
        if distance > 5:
            return "VERY_STRONG"
        elif distance > 2:
            return "STRONG"
        elif distance > 1:
            return "MODERATE"
        else:
            return "WEAK"


def get_advanced_analysis_message(prices: Dict) -> str:
    """Fibonacci + Volume profili özeti"""
    
    msg = "🎯 FİBONACCİ + VOLUME PROFLE ANALZ\n"
    msg += "="*50 + "\n\n"
    
    # Fibonacci
    high = max(prices.get('highs', [0]))
    low = min(prices.get('lows', [0]))
    
    if high > low:
        fib = FibonacciAnalyzer()
        fib_levels = fib.calculate_fibonacci_levels(high, low)
        
        msg += "📊 FİBONACCİ SEVİYELERİ:\n"
        key_levels = fib_levels.get('key_levels', {})
        for level_name, level_price in list(key_levels.items())[:3]:
            msg += f"   {level_name}: ₺{level_price}\n"
    
    # Volume Profile
    vp = VolumeProfileAnalyzer()
    closes = prices.get('closes', [])
    volumes = prices.get('volumes', [])
    
    if closes and volumes:
        profile = vp.calculate_volume_profile(closes, volumes, bins=15)
        if 'point_of_control' in profile:
            msg += f"\n📈 VOLUME PROFİLE:\n"
            msg += f"   POC: ₺{profile['point_of_control']}\n"
            msg += f"   Yorum: {profile['analysis'].get('interpretation', '')}\n"
    
    return msg
