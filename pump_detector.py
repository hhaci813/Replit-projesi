"""🚀 Pump Detection - Volume spike algılama"""
import numpy as np

class PumpDetector:
    def __init__(self, volume_threshold=1.5, price_threshold=0.02):
        self.volume_threshold = volume_threshold  # 1.5x normal volume
        self.price_threshold = price_threshold  # 2% fiyat artışı
    
    def detect_pump(self, current_volume, avg_volume, price_change_pct):
        """Pump candidate'ı tespit et"""
        volume_spike = current_volume / avg_volume if avg_volume > 0 else 0
        
        is_volume_spike = volume_spike >= self.volume_threshold
        is_price_rise = price_change_pct >= self.price_threshold
        
        if is_volume_spike and is_price_rise:
            return {
                'detected': True,
                'risk_level': 'HIGH' if volume_spike > 3 else 'MEDIUM',
                'volume_spike': volume_spike,
                'price_change': price_change_pct
            }
        
        return {'detected': False}
    
    def analyze_volume_pattern(self, volumes):
        """Volume pattern analizi"""
        if len(volumes) < 3:
            return None
        
        recent_vol = np.array(volumes[-5:])
        older_vol = np.array(volumes[:-5])
        
        recent_avg = recent_vol.mean()
        older_avg = older_vol.mean() if len(older_vol) > 0 else recent_avg
        
        spike_ratio = recent_avg / older_avg if older_avg > 0 else 1
        
        return {
            'recent_average': recent_avg,
            'historical_average': older_avg,
            'spike_ratio': spike_ratio,
            'is_unusual': spike_ratio > self.volume_threshold
        }

class TrendDetector:
    """Trend detection - RSI, MACD, Moving Averages"""
    
    @staticmethod
    def detect_trend(prices):
        """Güçlü trend tespiti"""
        if len(prices) < 20:
            return 'INSUFFICIENT_DATA'
        
        prices = np.array(prices)
        ma20 = prices[-20:].mean()
        ma50 = prices[-50:].mean() if len(prices) >= 50 else prices.mean()
        
        # Trend
        if prices[-1] > ma20 > ma50:
            return 'STRONG_UP'
        elif prices[-1] < ma20 < ma50:
            return 'STRONG_DOWN'
        elif prices[-1] > ma20:
            return 'UP'
        elif prices[-1] < ma20:
            return 'DOWN'
        else:
            return 'SIDEWAYS'
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """RSI hesaplama"""
        if len(prices) < period:
            return 50
        
        prices = np.array(prices)
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        
        rs = up / down if down != 0 else 0
        rsi = 100 - 100 / (1 + rs)
        
        return rsi

if __name__ == "__main__":
    detector = PumpDetector()
    result = detector.detect_pump(1000, 500, 0.03)
    print(f"Pump Detection: {result}")
