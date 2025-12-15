"""
GELİŞMİŞ TEKNİK ANALİZ MODÜLÜ - MAX VERSİYON
Ichimoku, Stochastic RSI, ADX, ATR, OBV, Williams %R, VWAP
"""

import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AdvancedTechnical:
    """Gelişmiş teknik analiz göstergeleri"""
    
    def __init__(self):
        pass
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """EMA hesapla"""
        if len(prices) < period:
            return prices
        
        alpha = 2 / (period + 1)
        ema = [prices[0]]
        for price in prices[1:]:
            ema.append(alpha * price + (1 - alpha) * ema[-1])
        return ema
    
    def calculate_sma(self, prices: List[float], period: int) -> List[float]:
        """SMA hesapla"""
        if len(prices) < period:
            return [sum(prices) / len(prices)] * len(prices)
        
        sma = []
        for i in range(len(prices)):
            if i < period - 1:
                sma.append(sum(prices[:i+1]) / (i + 1))
            else:
                sma.append(sum(prices[i-period+1:i+1]) / period)
        return sma
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI hesapla"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def calculate_stochastic_rsi(self, prices: List[float], rsi_period: int = 14, stoch_period: int = 14) -> Dict:
        """
        Stochastic RSI - RSI'nin stokastik versiyonu
        %K ve %D değerleri döndürür
        
        Yorumlama:
        - 80 üzeri: Aşırı alım
        - 20 altı: Aşırı satım
        - %K, %D'yi yukarı keserse: AL sinyali
        - %K, %D'yi aşağı keserse: SAT sinyali
        """
        if len(prices) < rsi_period + stoch_period:
            return {'k': 50, 'd': 50, 'signal': 'BEKLE', 'aciklama': 'Yetersiz veri'}
        
        rsi_values = []
        for i in range(rsi_period, len(prices) + 1):
            rsi = self.calculate_rsi(prices[:i], rsi_period)
            rsi_values.append(rsi)
        
        if len(rsi_values) < stoch_period:
            return {'k': 50, 'd': 50, 'signal': 'BEKLE', 'aciklama': 'Yetersiz veri'}
        
        recent_rsi = rsi_values[-stoch_period:]
        min_rsi = min(recent_rsi)
        max_rsi = max(recent_rsi)
        
        if max_rsi == min_rsi:
            k = 50
        else:
            k = ((rsi_values[-1] - min_rsi) / (max_rsi - min_rsi)) * 100
        
        d = sum(rsi_values[-3:]) / 3 if len(rsi_values) >= 3 else k
        d = ((d - min_rsi) / (max_rsi - min_rsi)) * 100 if max_rsi != min_rsi else 50
        
        if k > 80:
            signal = 'AŞIRI ALIM'
            aciklama = '🔴 Düzeltme gelebilir, dikkatli ol'
        elif k < 20:
            signal = 'AŞIRI SATIM'
            aciklama = '🟢 Alım fırsatı olabilir'
        elif k > d and k < 50:
            signal = 'AL SİNYALİ'
            aciklama = '🟢 Yukarı momentum başlıyor'
        elif k < d and k > 50:
            signal = 'SAT SİNYALİ'
            aciklama = '🔴 Aşağı momentum başlıyor'
        else:
            signal = 'NÖTR'
            aciklama = '⚪ Net sinyal yok'
        
        return {
            'k': round(k, 1),
            'd': round(d, 1),
            'signal': signal,
            'aciklama': aciklama
        }
    
    def calculate_ichimoku(self, highs: List[float], lows: List[float], closes: List[float]) -> Dict:
        """
        Ichimoku Cloud - Japon bulut sistemi
        
        Bileşenler:
        - Tenkan-sen (Dönüş çizgisi): 9 periyot
        - Kijun-sen (Taban çizgisi): 26 periyot
        - Senkou Span A: (Tenkan + Kijun) / 2, 26 ileri
        - Senkou Span B: 52 periyot orta, 26 ileri
        - Chikou Span: Kapanış, 26 geri
        
        Yorumlama:
        - Fiyat bulutun üstünde: Yükseliş trendi
        - Fiyat bulutun altında: Düşüş trendi
        - Tenkan > Kijun: Boğa sinyali
        - Tenkan < Kijun: Ayı sinyali
        """
        if len(closes) < 52:
            return {
                'tenkan': 0, 'kijun': 0, 'senkou_a': 0, 'senkou_b': 0,
                'trend': 'UNKNOWN', 'signal': 'BEKLE',
                'aciklama': 'Yetersiz veri (min 52 gün gerekli)'
            }
        
        def donchian_mid(h, l, period):
            return (max(h[-period:]) + min(l[-period:])) / 2
        
        tenkan = donchian_mid(highs, lows, 9)
        kijun = donchian_mid(highs, lows, 26)
        senkou_a = (tenkan + kijun) / 2
        senkou_b = donchian_mid(highs, lows, 52)
        
        current_price = closes[-1]
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        
        if current_price > cloud_top:
            trend = 'YUKARI'
            trend_aciklama = '🟢 Fiyat bulutun üstünde - Güçlü yükseliş'
        elif current_price < cloud_bottom:
            trend = 'AŞAĞI'
            trend_aciklama = '🔴 Fiyat bulutun altında - Düşüş trendi'
        else:
            trend = 'BULUT İÇİNDE'
            trend_aciklama = '🟡 Fiyat bulut içinde - Kararsız'
        
        if tenkan > kijun:
            signal = 'AL'
            signal_aciklama = '🟢 Tenkan > Kijun - Boğa sinyali'
        elif tenkan < kijun:
            signal = 'SAT'
            signal_aciklama = '🔴 Tenkan < Kijun - Ayı sinyali'
        else:
            signal = 'BEKLE'
            signal_aciklama = '⚪ Tenkan = Kijun - Nötr'
        
        if trend == 'YUKARI' and signal == 'AL':
            genel = 'GÜÇLÜ AL'
            genel_aciklama = '🟢🟢 Trend ve sinyal uyumlu - Güçlü alım'
        elif trend == 'AŞAĞI' and signal == 'SAT':
            genel = 'GÜÇLÜ SAT'
            genel_aciklama = '🔴🔴 Trend ve sinyal uyumlu - Satış'
        else:
            genel = 'BEKLE'
            genel_aciklama = '🟡 Trend ve sinyal uyumsuz - Bekle'
        
        return {
            'tenkan': round(tenkan, 4),
            'kijun': round(kijun, 4),
            'senkou_a': round(senkou_a, 4),
            'senkou_b': round(senkou_b, 4),
            'cloud_top': round(cloud_top, 4),
            'cloud_bottom': round(cloud_bottom, 4),
            'trend': trend,
            'trend_aciklama': trend_aciklama,
            'signal': signal,
            'signal_aciklama': signal_aciklama,
            'genel': genel,
            'genel_aciklama': genel_aciklama
        }
    
    def calculate_adx(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Dict:
        """
        ADX - Average Directional Index
        Trend gücünü ölçer (yön değil, güç!)
        
        Yorumlama:
        - 0-25: Zayıf trend veya yatay
        - 25-50: Güçlü trend
        - 50-75: Çok güçlü trend
        - 75-100: Aşırı güçlü trend
        
        +DI > -DI: Yükseliş trendi
        -DI > +DI: Düşüş trendi
        """
        if len(closes) < period + 1:
            return {
                'adx': 0, 'plus_di': 0, 'minus_di': 0,
                'trend_strength': 'UNKNOWN', 'trend_direction': 'UNKNOWN',
                'aciklama': 'Yetersiz veri'
            }
        
        tr_list = []
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(closes)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
            
            if high_diff > low_diff and high_diff > 0:
                plus_dm.append(high_diff)
            else:
                plus_dm.append(0)
            
            if low_diff > high_diff and low_diff > 0:
                minus_dm.append(low_diff)
            else:
                minus_dm.append(0)
        
        if len(tr_list) < period:
            return {
                'adx': 0, 'plus_di': 0, 'minus_di': 0,
                'trend_strength': 'UNKNOWN', 'trend_direction': 'UNKNOWN',
                'aciklama': 'Yetersiz veri'
            }
        
        atr = sum(tr_list[-period:]) / period
        plus_dm_avg = sum(plus_dm[-period:]) / period
        minus_dm_avg = sum(minus_dm[-period:]) / period
        
        if atr == 0:
            plus_di = 0
            minus_di = 0
        else:
            plus_di = (plus_dm_avg / atr) * 100
            minus_di = (minus_dm_avg / atr) * 100
        
        if plus_di + minus_di == 0:
            dx = 0
        else:
            dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100
        
        adx = dx
        
        if adx < 25:
            trend_strength = 'ZAYIF'
            strength_aciklama = '⚪ Trend zayıf veya yatay piyasa'
        elif adx < 50:
            trend_strength = 'GÜÇLÜ'
            strength_aciklama = '🟢 Güçlü trend var'
        elif adx < 75:
            trend_strength = 'ÇOK GÜÇLÜ'
            strength_aciklama = '🟢🟢 Çok güçlü trend - Trendi takip et'
        else:
            trend_strength = 'AŞIRI GÜÇLÜ'
            strength_aciklama = '🔥 Aşırı güçlü trend - Dikkat, dönüş yakın olabilir'
        
        if plus_di > minus_di:
            trend_direction = 'YUKARI'
            direction_aciklama = '📈 Yükseliş trendi baskın'
        else:
            trend_direction = 'AŞAĞI'
            direction_aciklama = '📉 Düşüş trendi baskın'
        
        return {
            'adx': round(adx, 1),
            'plus_di': round(plus_di, 1),
            'minus_di': round(minus_di, 1),
            'trend_strength': trend_strength,
            'strength_aciklama': strength_aciklama,
            'trend_direction': trend_direction,
            'direction_aciklama': direction_aciklama
        }
    
    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Dict:
        """
        ATR - Average True Range
        Volatilite (oynaklık) ölçer
        
        Yorumlama:
        - Yüksek ATR: Yüksek volatilite, geniş stop-loss gerekir
        - Düşük ATR: Düşük volatilite, dar stop-loss yeterli
        - Stop-loss için: 2x ATR kullan
        """
        if len(closes) < period + 1:
            return {
                'atr': 0, 'atr_percent': 0, 'volatility': 'UNKNOWN',
                'suggested_stop': 0, 'aciklama': 'Yetersiz veri'
            }
        
        tr_list = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
        
        atr = sum(tr_list[-period:]) / period
        current_price = closes[-1]
        atr_percent = (atr / current_price) * 100 if current_price > 0 else 0
        
        suggested_stop = current_price - (2 * atr)
        
        if atr_percent < 2:
            volatility = 'DÜŞÜK'
            aciklama = '🟢 Düşük volatilite - Sakin piyasa'
        elif atr_percent < 5:
            volatility = 'NORMAL'
            aciklama = '🟡 Normal volatilite'
        elif atr_percent < 10:
            volatility = 'YÜKSEK'
            aciklama = '🟠 Yüksek volatilite - Dikkatli ol'
        else:
            volatility = 'ÇOK YÜKSEK'
            aciklama = '🔴 Çok yüksek volatilite - Riskli!'
        
        return {
            'atr': round(atr, 4),
            'atr_percent': round(atr_percent, 2),
            'volatility': volatility,
            'suggested_stop': round(suggested_stop, 4),
            'aciklama': aciklama
        }
    
    def calculate_obv(self, closes: List[float], volumes: List[float]) -> Dict:
        """
        OBV - On Balance Volume
        Hacim ve fiyat ilişkisini ölçer
        
        Yorumlama:
        - OBV yükseliyor + Fiyat yükseliyor: Güçlü yükseliş
        - OBV düşüyor + Fiyat düşüyor: Güçlü düşüş
        - OBV yükseliyor + Fiyat düşüyor: Yakında yukarı dönüş (diverjanş)
        - OBV düşüyor + Fiyat yükseliyor: Yakında aşağı dönüş (diverjanş)
        """
        if len(closes) < 10 or len(volumes) < 10:
            return {
                'obv': 0, 'obv_trend': 'UNKNOWN', 'divergence': False,
                'aciklama': 'Yetersiz veri'
            }
        
        obv = [0]
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif closes[i] < closes[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        
        obv_change = (obv[-1] - obv[-7]) / abs(obv[-7]) * 100 if obv[-7] != 0 else 0
        price_change = (closes[-1] - closes[-7]) / closes[-7] * 100 if closes[-7] != 0 else 0
        
        if obv_change > 5:
            obv_trend = 'YUKARI'
        elif obv_change < -5:
            obv_trend = 'AŞAĞI'
        else:
            obv_trend = 'YATAY'
        
        divergence = False
        if obv_change > 10 and price_change < -5:
            divergence = True
            aciklama = '🟢 POZİTİF DİVERJANS! Hacim yükseliyor, fiyat düşüyor - Yukarı dönüş beklenir'
        elif obv_change < -10 and price_change > 5:
            divergence = True
            aciklama = '🔴 NEGATİF DİVERJANS! Hacim düşüyor, fiyat yükseliyor - Aşağı dönüş beklenir'
        elif obv_trend == 'YUKARI' and price_change > 0:
            aciklama = '🟢 Hacim ve fiyat uyumlu yükseliyor - Güçlü trend'
        elif obv_trend == 'AŞAĞI' and price_change < 0:
            aciklama = '🔴 Hacim ve fiyat uyumlu düşüyor - Güçlü düşüş'
        else:
            aciklama = '⚪ Net sinyal yok'
        
        return {
            'obv': round(obv[-1], 0),
            'obv_change_7d': round(obv_change, 1),
            'obv_trend': obv_trend,
            'divergence': divergence,
            'aciklama': aciklama
        }
    
    def calculate_williams_r(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Dict:
        """
        Williams %R
        RSI benzeri momentum göstergesi
        
        Yorumlama:
        - -20 üzeri: Aşırı alım (satış düşün)
        - -80 altı: Aşırı satım (alım düşün)
        - -50 orta nokta
        """
        if len(closes) < period:
            return {'williams_r': -50, 'signal': 'BEKLE', 'aciklama': 'Yetersiz veri'}
        
        highest_high = max(highs[-period:])
        lowest_low = min(lows[-period:])
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            williams_r = -50
        else:
            williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        
        if williams_r > -20:
            signal = 'AŞIRI ALIM'
            aciklama = '🔴 Aşırı alım bölgesi - Düzeltme gelebilir'
        elif williams_r < -80:
            signal = 'AŞIRI SATIM'
            aciklama = '🟢 Aşırı satım bölgesi - Alım fırsatı'
        elif williams_r > -50:
            signal = 'YUKARI EĞİLİMLİ'
            aciklama = '📈 Orta üstü - Yükseliş devam edebilir'
        else:
            signal = 'AŞAĞI EĞİLİMLİ'
            aciklama = '📉 Orta altı - Düşüş devam edebilir'
        
        return {
            'williams_r': round(williams_r, 1),
            'signal': signal,
            'aciklama': aciklama
        }
    
    def full_technical_analysis(self, highs: List[float], lows: List[float], 
                                  closes: List[float], volumes: List[float]) -> Dict:
        """Tam teknik analiz - Tüm göstergeler"""
        
        result = {
            'has_data': False,
            'rsi': 50,
            'stoch_rsi': {},
            'ichimoku': {},
            'adx': {},
            'atr': {},
            'obv': {},
            'williams_r': {},
            'overall_score': 50,
            'overall_signal': 'BEKLE',
            'overall_aciklama': ''
        }
        
        if len(closes) < 52:
            result['overall_aciklama'] = 'Yetersiz veri (min 52 gün gerekli)'
            return result
        
        result['has_data'] = True
        
        result['rsi'] = self.calculate_rsi(closes)
        result['stoch_rsi'] = self.calculate_stochastic_rsi(closes)
        result['ichimoku'] = self.calculate_ichimoku(highs, lows, closes)
        result['adx'] = self.calculate_adx(highs, lows, closes)
        result['atr'] = self.calculate_atr(highs, lows, closes)
        result['obv'] = self.calculate_obv(closes, volumes)
        result['williams_r'] = self.calculate_williams_r(highs, lows, closes)
        
        score = 50
        signals = []
        
        if result['rsi'] < 30:
            score += 15
            signals.append('RSI aşırı satım')
        elif result['rsi'] > 70:
            score -= 15
            signals.append('RSI aşırı alım')
        
        if result['stoch_rsi'].get('signal') == 'AŞIRI SATIM':
            score += 10
        elif result['stoch_rsi'].get('signal') == 'AŞIRI ALIM':
            score -= 10
        
        ichimoku = result['ichimoku']
        if ichimoku.get('genel') == 'GÜÇLÜ AL':
            score += 20
            signals.append('Ichimoku AL')
        elif ichimoku.get('genel') == 'GÜÇLÜ SAT':
            score -= 20
            signals.append('Ichimoku SAT')
        
        adx = result['adx']
        if adx.get('adx', 0) > 25:
            if adx.get('trend_direction') == 'YUKARI':
                score += 15
                signals.append('ADX güçlü yükseliş')
            else:
                score -= 15
                signals.append('ADX güçlü düşüş')
        
        if result['obv'].get('divergence'):
            if 'POZİTİF' in result['obv'].get('aciklama', ''):
                score += 15
                signals.append('OBV pozitif diverjanş')
            else:
                score -= 15
                signals.append('OBV negatif diverjanş')
        
        williams = result['williams_r']
        if williams.get('signal') == 'AŞIRI SATIM':
            score += 10
        elif williams.get('signal') == 'AŞIRI ALIM':
            score -= 10
        
        score = max(0, min(100, score))
        result['overall_score'] = score
        
        if score >= 75:
            result['overall_signal'] = 'GÜÇLÜ AL'
            result['overall_aciklama'] = '🟢🟢 Çoğu gösterge alım sinyali veriyor'
        elif score >= 60:
            result['overall_signal'] = 'AL'
            result['overall_aciklama'] = '🟢 Genel görünüm olumlu'
        elif score >= 40:
            result['overall_signal'] = 'BEKLE'
            result['overall_aciklama'] = '🟡 Karışık sinyaller - Bekle'
        elif score >= 25:
            result['overall_signal'] = 'SAT'
            result['overall_aciklama'] = '🔴 Genel görünüm olumsuz'
        else:
            result['overall_signal'] = 'GÜÇLÜ SAT'
            result['overall_aciklama'] = '🔴🔴 Çoğu gösterge satış sinyali veriyor'
        
        result['active_signals'] = signals
        
        return result


advanced_tech = AdvancedTechnical()
