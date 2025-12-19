"""
💎 İLERİ FİYAT HAREKETI ANALZ
Support/Resistance seviyeleri, Order blocks, Fair value gaps
"""

from typing import List, Dict, Tuple
import numpy as np

class PriceActionAnalyzer:
    """Advanced price action - Support/Resistance ve tuzakları"""
    
    def find_support_resistance_levels(self, prices: List[float], sensitivity: int = 10) -> Dict:
        """Önemli destek ve direnç seviyelerini bul"""
        
        if len(prices) < sensitivity:
            return {'error': 'Yeterli veri yok'}
        
        # Local minima (support)
        supports = []
        for i in range(sensitivity // 2, len(prices) - sensitivity // 2):
            window = prices[i - sensitivity // 2:i + sensitivity // 2]
            if prices[i] == min(window):
                supports.append((i, prices[i]))
        
        # Local maxima (resistance)
        resistances = []
        for i in range(sensitivity // 2, len(prices) - sensitivity // 2):
            window = prices[i - sensitivity // 2:i + sensitivity // 2]
            if prices[i] == max(window):
                resistances.append((i, prices[i]))
        
        # Merge nearby levels
        supports = self._merge_levels(supports, threshold=0.02)
        resistances = self._merge_levels(resistances, threshold=0.02)
        
        # Strength calculation
        support_levels = [{'price': p, 'strength': self._calculate_level_strength(prices, p)} 
                         for _, p in supports]
        resistance_levels = [{'price': p, 'strength': self._calculate_level_strength(prices, p)} 
                            for _, p in resistances]
        
        # Sort
        support_levels.sort(key=lambda x: x['price'])
        resistance_levels.sort(key=lambda x: x['price'], reverse=True)
        
        return {
            'supports': support_levels[:5],  # Top 5
            'resistances': resistance_levels[:5],
            'current_price': prices[-1],
            'pivots': self._calculate_pivot_points(prices)
        }
    
    def _merge_levels(self, levels: List[Tuple], threshold: float = 0.02) -> List[Tuple]:
        """Yakın seviyeleri birleştir"""
        if not levels:
            return []
        
        merged = []
        sorted_levels = sorted(levels, key=lambda x: x[1])
        
        current_group = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if abs((level[1] - current_group[-1][1]) / current_group[-1][1]) < threshold:
                current_group.append(level)
            else:
                avg_idx = sum(l[0] for l in current_group) // len(current_group)
                avg_price = sum(l[1] for l in current_group) / len(current_group)
                merged.append((avg_idx, avg_price))
                current_group = [level]
        
        if current_group:
            avg_idx = sum(l[0] for l in current_group) // len(current_group)
            avg_price = sum(l[1] for l in current_group) / len(current_group)
            merged.append((avg_idx, avg_price))
        
        return merged
    
    def _calculate_level_strength(self, prices: List[float], level: float, window: int = 20) -> str:
        """Destek/direnç gücünü hesapla"""
        touches = 0
        bounces = 0
        
        for i in range(1, min(len(prices) - 1, window)):
            if abs(prices[i] - level) / level < 0.01:  # 1% tolerance
                touches += 1
                # Eğer seviyelenmiş ve geri geçtiyse - bounce
                if (prices[i-1] < level < prices[i+1]) or (prices[i-1] > level > prices[i+1]):
                    bounces += 1
        
        if touches >= 3:
            return "VERY_STRONG"
        elif touches == 2:
            return "STRONG"
        elif touches == 1 and bounces > 0:
            return "MODERATE"
        else:
            return "WEAK"
    
    def _calculate_pivot_points(self, prices: List[float]) -> Dict:
        """Pivot noktaları hesapla"""
        if len(prices) < 1:
            return {}
        
        high = max(prices)
        low = min(prices)
        close = prices[-1]
        
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        
        return {
            'pivot': round(pivot, 2),
            'r1': round(r1, 2),
            'r2': round(r2, 2),
            's1': round(s1, 2),
            's2': round(s2, 2)
        }
    
    def detect_order_blocks(self, opens: List[float], closes: List[float], 
                           highs: List[float], lows: List[float]) -> List[Dict]:
        """Order block'ları tespit et (bullish/bearish accumulation zones)"""
        
        order_blocks = []
        
        for i in range(1, len(closes) - 1):
            # Bullish Order Block: Strong bullish candle, sonra consolidation
            if closes[i] > opens[i]:  # Bullish candle
                strength = (closes[i] - opens[i]) / (highs[i] - lows[i])
                
                # Check next candle for pullback
                if i + 1 < len(closes):
                    if lows[i+1] < closes[i] and closes[i+1] < closes[i]:
                        order_blocks.append({
                            'type': 'BULLISH_OB',
                            'level': closes[i],
                            'range_low': lows[i],
                            'range_high': highs[i],
                            'strength': min(int(strength * 10), 10)
                        })
            
            # Bearish Order Block
            elif closes[i] < opens[i]:  # Bearish candle
                strength = (opens[i] - closes[i]) / (highs[i] - lows[i])
                
                if i + 1 < len(closes):
                    if highs[i+1] > closes[i] and closes[i+1] > closes[i]:
                        order_blocks.append({
                            'type': 'BEARISH_OB',
                            'level': closes[i],
                            'range_high': highs[i],
                            'range_low': lows[i],
                            'strength': min(int(strength * 10), 10)
                        })
        
        return order_blocks[:5]  # Top 5
    
    def detect_fair_value_gaps(self, highs: List[float], lows: List[float]) -> List[Dict]:
        """Fair Value Gaps (FVG) - açılmayan fiyat boşlukları"""
        
        gaps = []
        
        for i in range(1, len(lows)):
            # Bullish FVG: Gap up sonra pullback
            if lows[i] > highs[i-1]:
                gap_size = lows[i] - highs[i-1]
                gap_percent = (gap_size / highs[i-1]) * 100
                
                if gap_percent > 0.5:  # %0.5+ gap
                    gaps.append({
                        'type': 'BULLISH_FVG',
                        'gap_start': highs[i-1],
                        'gap_end': lows[i],
                        'size_percent': round(gap_percent, 2),
                        'level': (highs[i-1] + lows[i]) / 2
                    })
            
            # Bearish FVG: Gap down
            elif highs[i] < lows[i-1]:
                gap_size = lows[i-1] - highs[i]
                gap_percent = (gap_size / lows[i-1]) * 100
                
                if gap_percent > 0.5:
                    gaps.append({
                        'type': 'BEARISH_FVG',
                        'gap_start': lows[i-1],
                        'gap_end': highs[i],
                        'size_percent': round(gap_percent, 2),
                        'level': (lows[i-1] + highs[i]) / 2
                    })
        
        return gaps[:3]
    
    def get_price_action_summary(self, prices: Dict) -> str:
        """Price action özeti"""
        sr = self.find_support_resistance_levels(prices.get('closes', []))
        
        msg = "💎 ADVANCED PRICE ACTION\n"
        msg += "="*50 + "\n\n"
        
        # Support/Resistance
        if 'supports' in sr:
            msg += "📉 DESTEK SEVİYELERİ:\n"
            for i, sup in enumerate(sr['supports'][:3], 1):
                msg += f"   {i}. ₺{sup['price']:.2f} ({sup['strength']})\n"
        
        if 'resistances' in sr:
            msg += "\n📈 DİRENÇ SEVİYELERİ:\n"
            for i, res in enumerate(sr['resistances'][:3], 1):
                msg += f"   {i}. ₺{res['price']:.2f} ({res['strength']})\n"
        
        # Pivots
        if 'pivots' in sr:
            pivots = sr['pivots']
            msg += f"\n🎯 PIVOT NOKTALAR:\n"
            msg += f"   Pivot: ₺{pivots['pivot']}\n"
            msg += f"   R1: ₺{pivots['r1']} | S1: ₺{pivots['s1']}\n"
        
        return msg
