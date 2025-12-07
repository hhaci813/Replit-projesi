"""
GELİŞMİŞ TEKNİK GÖSTERGELER
Fibonacci, Volume Profile, Ichimoku Cloud
"""

import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AdvancedIndicators:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300
        
    def get_price_history(self, symbol: str, days: int = 30) -> List[Dict]:
        try:
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            resp = requests.get(
                "https://graph-api.btcturk.com/v1/klines/history",
                params={
                    "symbol": f"{symbol}TRY",
                    "resolution": "D",
                    "from": start_time // 1000,
                    "to": end_time // 1000
                },
                timeout=15
            )
            
            data = resp.json()
            if 'c' in data and len(data['c']) > 5:
                return {
                    'open': [float(x) for x in data.get('o', [])],
                    'high': [float(x) for x in data.get('h', [])],
                    'low': [float(x) for x in data.get('l', [])],
                    'close': [float(x) for x in data.get('c', [])],
                    'volume': [float(x) for x in data.get('v', [])]
                }
            return None
        except:
            return None
    
    def calculate_fibonacci(self, symbol: str) -> Dict:
        """Fibonacci seviyeleri hesapla"""
        try:
            data = self.get_price_history(symbol, 30)
            if not data:
                return None
            
            high = max(data['high'])
            low = min(data['low'])
            diff = high - low
            current = data['close'][-1]
            
            levels = {
                '0.0': high,
                '0.236': high - (diff * 0.236),
                '0.382': high - (diff * 0.382),
                '0.5': high - (diff * 0.5),
                '0.618': high - (diff * 0.618),
                '0.786': high - (diff * 0.786),
                '1.0': low
            }
            
            support = None
            resistance = None
            for level, price in sorted(levels.items(), key=lambda x: x[1], reverse=True):
                if price < current and support is None:
                    support = {'level': level, 'price': price}
                if price > current:
                    resistance = {'level': level, 'price': price}
            
            position = ((current - low) / diff * 100) if diff > 0 else 50
            
            trend = 'BULLISH' if position > 61.8 else ('BEARISH' if position < 38.2 else 'NEUTRAL')
            
            return {
                'symbol': symbol,
                'current_price': current,
                'levels': levels,
                'support': support,
                'resistance': resistance,
                'position': round(position, 1),
                'trend': trend,
                'high_30d': high,
                'low_30d': low
            }
        except Exception as e:
            return None
    
    def calculate_volume_profile(self, symbol: str) -> Dict:
        """Volume Profile analizi"""
        try:
            data = self.get_price_history(symbol, 30)
            if not data or len(data['close']) < 10:
                return None
            
            prices = data['close']
            volumes = data['volume']
            
            price_min = min(prices)
            price_max = max(prices)
            num_bins = 10
            bin_size = (price_max - price_min) / num_bins
            
            volume_bins = {}
            for i in range(num_bins):
                bin_low = price_min + (i * bin_size)
                bin_high = bin_low + bin_size
                bin_vol = 0
                for j, price in enumerate(prices):
                    if bin_low <= price < bin_high:
                        bin_vol += volumes[j]
                volume_bins[f"{bin_low:.2f}-{bin_high:.2f}"] = bin_vol
            
            poc_range = max(volume_bins, key=volume_bins.get)
            poc_price = (float(poc_range.split('-')[0]) + float(poc_range.split('-')[1])) / 2
            
            current = prices[-1]
            avg_volume = np.mean(volumes)
            recent_volume = np.mean(volumes[-5:])
            volume_trend = 'HIGH' if recent_volume > avg_volume * 1.5 else ('LOW' if recent_volume < avg_volume * 0.5 else 'NORMAL')
            
            position = 'ABOVE_POC' if current > poc_price else 'BELOW_POC'
            
            return {
                'symbol': symbol,
                'current_price': current,
                'poc_price': poc_price,
                'poc_range': poc_range,
                'position': position,
                'volume_bins': volume_bins,
                'avg_volume': avg_volume,
                'recent_volume': recent_volume,
                'volume_trend': volume_trend,
                'signal': 'BULLISH' if position == 'ABOVE_POC' and volume_trend == 'HIGH' else 
                         ('BEARISH' if position == 'BELOW_POC' and volume_trend == 'HIGH' else 'NEUTRAL')
            }
        except:
            return None
    
    def calculate_ichimoku(self, symbol: str) -> Dict:
        """Ichimoku Cloud hesapla"""
        try:
            data = self.get_price_history(symbol, 60)
            if not data or len(data['close']) < 52:
                return None
            
            high = np.array(data['high'])
            low = np.array(data['low'])
            close = np.array(data['close'])
            
            def period_high_low_mid(h, l, period):
                return (np.max(h[-period:]) + np.min(l[-period:])) / 2
            
            tenkan = period_high_low_mid(high, low, 9)
            kijun = period_high_low_mid(high, low, 26)
            senkou_a = (tenkan + kijun) / 2
            senkou_b = period_high_low_mid(high, low, 52)
            chikou = close[-1]
            
            current = close[-1]
            
            cloud_top = max(senkou_a, senkou_b)
            cloud_bottom = min(senkou_a, senkou_b)
            
            if current > cloud_top:
                position = 'ABOVE_CLOUD'
                trend = 'BULLISH'
            elif current < cloud_bottom:
                position = 'BELOW_CLOUD'
                trend = 'BEARISH'
            else:
                position = 'IN_CLOUD'
                trend = 'NEUTRAL'
            
            signals = []
            if tenkan > kijun:
                signals.append('TK Cross Bullish')
            else:
                signals.append('TK Cross Bearish')
            
            if current > tenkan:
                signals.append('Price > Tenkan')
            if current > kijun:
                signals.append('Price > Kijun')
            
            cloud_color = 'GREEN' if senkou_a > senkou_b else 'RED'
            
            bullish_signals = sum(1 for s in signals if 'Bullish' in s or '>' in s)
            strength = bullish_signals / len(signals) * 100 if signals else 50
            
            return {
                'symbol': symbol,
                'current_price': current,
                'tenkan_sen': round(tenkan, 2),
                'kijun_sen': round(kijun, 2),
                'senkou_a': round(senkou_a, 2),
                'senkou_b': round(senkou_b, 2),
                'chikou_span': round(chikou, 2),
                'cloud_top': round(cloud_top, 2),
                'cloud_bottom': round(cloud_bottom, 2),
                'cloud_color': cloud_color,
                'position': position,
                'trend': trend,
                'signals': signals,
                'strength': round(strength, 1)
            }
        except:
            return None
    
    def get_full_analysis(self, symbol: str) -> Dict:
        """Tüm gelişmiş göstergeleri al"""
        return {
            'fibonacci': self.calculate_fibonacci(symbol),
            'volume_profile': self.calculate_volume_profile(symbol),
            'ichimoku': self.calculate_ichimoku(symbol),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_report(self, symbol: str = 'BTC') -> str:
        """Telegram için rapor oluştur"""
        fib = self.calculate_fibonacci(symbol)
        vol = self.calculate_volume_profile(symbol)
        ich = self.calculate_ichimoku(symbol)
        
        msg = f"📊 <b>GELİŞMİŞ ANALİZ: {symbol} (TL)</b>\n\n"
        
        if fib:
            msg += f"""📐 <b>FİBONACCİ SEVİYELERİ</b>
💰 Fiyat: ₺{fib['current_price']:,.2f}
📈 30g Yüksek: ₺{fib['high_30d']:,.2f}
📉 30g Düşük: ₺{fib['low_30d']:,.2f}
🎯 Destek: ₺{fib['support']['price']:,.2f} ({fib['support']['level']})
🚀 Direnç: ₺{fib['resistance']['price']:,.2f} ({fib['resistance']['level']})
📊 Pozisyon: %{fib['position']}
🔮 Trend: {fib['trend']}

"""
        
        if vol:
            msg += f"""📊 <b>VOLUME PROFİLE</b>
💎 POC Fiyat: ₺{vol['poc_price']:,.2f}
📍 Pozisyon: {vol['position']}
📈 Hacim Trend: {vol['volume_trend']}
🔮 Sinyal: {vol['signal']}

"""
        
        if ich:
            msg += f"""☁️ <b>ICHIMOKU CLOUD</b>
🔴 Tenkan: ₺{ich['tenkan_sen']:,.2f}
🔵 Kijun: ₺{ich['kijun_sen']:,.2f}
☁️ Bulut: {ich['cloud_color']} (₺{ich['cloud_bottom']:,.2f} - ₺{ich['cloud_top']:,.2f})
📍 Pozisyon: {ich['position']}
🔮 Trend: {ich['trend']}
💪 Güç: %{ich['strength']}
"""
        
        return msg
