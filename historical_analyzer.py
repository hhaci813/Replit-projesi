"""
TARİHSEL PATTERN ANALİZCİSİ - GELİŞMİŞ VERSİYON
Yükselen kriptoları geçmiş verilerle karşılaştır
+ Fibonacci seviyeleri
+ Destek/Direnç analizi
+ BTC korelasyonu
+ Trend kanalı
+ Risk/ödül oranı
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class HistoricalPatternAnalyzer:
    def __init__(self):
        self.cache_file = "historical_events.json"
        self.events = self.load_events()
        self.btc_cache = {'data': None, 'timestamp': None}
    
    def calculate_fibonacci_levels(self, high: float, low: float) -> Dict:
        """Fibonacci düzeltme seviyeleri hesapla"""
        diff = high - low
        return {
            '0.0': high,
            '0.236': high - (diff * 0.236),
            '0.382': high - (diff * 0.382),
            '0.5': high - (diff * 0.5),
            '0.618': high - (diff * 0.618),
            '0.786': high - (diff * 0.786),
            '1.0': low,
            'ext_1.272': high + (diff * 0.272),
            'ext_1.618': high + (diff * 0.618)
        }
    
    def find_support_resistance(self, closes: List[float], window: int = 10) -> Dict:
        """Destek ve direnç seviyelerini bul"""
        if len(closes) < window * 2:
            return {'supports': [], 'resistances': [], 'current_zone': 'UNKNOWN'}
        
        supports = []
        resistances = []
        
        for i in range(window, len(closes) - window):
            is_support = all(closes[i] <= closes[i-j] and closes[i] <= closes[i+j] for j in range(1, min(window, len(closes)-i)))
            is_resistance = all(closes[i] >= closes[i-j] and closes[i] >= closes[i+j] for j in range(1, min(window, len(closes)-i)))
            
            if is_support:
                supports.append(closes[i])
            if is_resistance:
                resistances.append(closes[i])
        
        supports = sorted(set([round(s, 4) for s in supports]))[-3:] if supports else []
        resistances = sorted(set([round(r, 4) for r in resistances]))[:3] if resistances else []
        
        current = closes[-1]
        if resistances and current > resistances[-1] * 0.98:
            zone = 'RESISTANCE'
        elif supports and current < supports[0] * 1.02:
            zone = 'SUPPORT'
        else:
            zone = 'MIDDLE'
        
        return {
            'supports': supports,
            'resistances': resistances,
            'current_zone': zone
        }
    
    def calculate_btc_correlation(self, coin_closes: List[float], btc_closes: List[float]) -> Dict:
        """BTC ile korelasyon hesapla"""
        if len(coin_closes) < 10 or len(btc_closes) < 10:
            return {'correlation': 0, 'strength': 'UNKNOWN', 'divergence': False}
        
        min_len = min(len(coin_closes), len(btc_closes))
        coin_data = coin_closes[-min_len:]
        btc_data = btc_closes[-min_len:]
        
        coin_returns = [(coin_data[i] - coin_data[i-1]) / coin_data[i-1] for i in range(1, len(coin_data))]
        btc_returns = [(btc_data[i] - btc_data[i-1]) / btc_data[i-1] for i in range(1, len(btc_data))]
        
        if len(coin_returns) < 5:
            return {'correlation': 0, 'strength': 'UNKNOWN', 'divergence': False}
        
        try:
            correlation = np.corrcoef(coin_returns, btc_returns)[0, 1]
        except:
            correlation = 0
        
        if correlation > 0.7:
            strength = 'STRONG_POSITIVE'
        elif correlation > 0.4:
            strength = 'MODERATE_POSITIVE'
        elif correlation > -0.4:
            strength = 'WEAK'
        elif correlation > -0.7:
            strength = 'MODERATE_NEGATIVE'
        else:
            strength = 'STRONG_NEGATIVE'
        
        recent_coin_change = (coin_closes[-1] - coin_closes[-7]) / coin_closes[-7] * 100 if len(coin_closes) >= 7 else 0
        recent_btc_change = (btc_closes[-1] - btc_closes[-7]) / btc_closes[-7] * 100 if len(btc_closes) >= 7 else 0
        
        divergence = (recent_coin_change > 10 and recent_btc_change < 5) or (recent_coin_change < -10 and recent_btc_change > -5)
        
        return {
            'correlation': round(correlation, 2),
            'strength': strength,
            'divergence': divergence,
            'coin_7d': round(recent_coin_change, 1),
            'btc_7d': round(recent_btc_change, 1)
        }
    
    def calculate_trend_channel(self, closes: List[float]) -> Dict:
        """Trend kanalı hesapla"""
        if len(closes) < 20:
            return {'trend': 'UNKNOWN', 'strength': 0, 'channel_position': 50}
        
        ma7 = sum(closes[-7:]) / 7
        ma20 = sum(closes[-20:]) / 20
        ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else ma20
        
        current = closes[-1]
        
        if ma7 > ma20 > ma50:
            trend = 'STRONG_UP'
            strength = 80
        elif ma7 > ma20:
            trend = 'UP'
            strength = 60
        elif ma7 < ma20 < ma50:
            trend = 'STRONG_DOWN'
            strength = 20
        elif ma7 < ma20:
            trend = 'DOWN'
            strength = 40
        else:
            trend = 'SIDEWAYS'
            strength = 50
        
        high_20 = max(closes[-20:])
        low_20 = min(closes[-20:])
        channel_position = ((current - low_20) / (high_20 - low_20) * 100) if high_20 != low_20 else 50
        
        return {
            'trend': trend,
            'strength': strength,
            'channel_position': round(channel_position, 1),
            'ma7': round(ma7, 4),
            'ma20': round(ma20, 4),
            'ma50': round(ma50, 4)
        }
    
    def calculate_risk_reward(self, current_price: float, supports: List[float], resistances: List[float], fib_levels: Dict) -> Dict:
        """Risk/Ödül oranı hesapla"""
        if resistances:
            target = resistances[0] if resistances[0] > current_price else fib_levels.get('ext_1.272', current_price * 1.15)
        else:
            target = fib_levels.get('ext_1.272', current_price * 1.15)
        
        if supports:
            stop = supports[-1] if supports[-1] < current_price else fib_levels.get('0.618', current_price * 0.92)
        else:
            stop = fib_levels.get('0.618', current_price * 0.92)
        
        potential_gain = ((target - current_price) / current_price) * 100
        potential_loss = ((current_price - stop) / current_price) * 100
        
        if potential_loss > 0:
            ratio = potential_gain / potential_loss
        else:
            ratio = 0
        
        if ratio >= 3:
            rating = 'EXCELLENT'
        elif ratio >= 2:
            rating = 'GOOD'
        elif ratio >= 1:
            rating = 'FAIR'
        else:
            rating = 'POOR'
        
        return {
            'target': round(target, 4),
            'stop': round(stop, 4),
            'potential_gain_pct': round(potential_gain, 1),
            'potential_loss_pct': round(potential_loss, 1),
            'ratio': round(ratio, 2),
            'rating': rating
        }
    
    def get_btc_data(self) -> Optional[List[float]]:
        """BTC fiyat verisini al (cache ile)"""
        if self.btc_cache['data'] and self.btc_cache['timestamp']:
            if (datetime.now() - self.btc_cache['timestamp']).seconds < 3600:
                return self.btc_cache['data']
        
        data = self.get_historical_data('BTC', 90)
        if data and 'close' in data:
            self.btc_cache = {'data': data['close'], 'timestamp': datetime.now()}
            return data['close']
        return None
        
    def load_events(self) -> Dict:
        """Kayıtlı event'leri yükle"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"events": [], "last_update": None}
    
    def save_events(self):
        """Event'leri kaydet"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.events, f, indent=2, default=str)
    
    def get_historical_data(self, symbol: str, days: int = 90) -> Optional[Dict]:
        """Geçmiş fiyat verisi al"""
        try:
            end_time = int(datetime.now().timestamp())
            start_time = int((datetime.now() - timedelta(days=days)).timestamp())
            
            resp = requests.get(
                "https://graph-api.btcturk.com/v1/klines/history",
                params={
                    "symbol": f"{symbol}TRY",
                    "resolution": "D",
                    "from": start_time,
                    "to": end_time
                },
                timeout=15
            )
            
            data = resp.json()
            if 'c' in data and len(data['c']) > 10:
                return {
                    'timestamps': data.get('t', []),
                    'open': [float(x) for x in data.get('o', [])],
                    'high': [float(x) for x in data.get('h', [])],
                    'low': [float(x) for x in data.get('l', [])],
                    'close': [float(x) for x in data.get('c', [])],
                    'volume': [float(x) for x in data.get('v', [])]
                }
        except Exception as e:
            logger.error(f"Historical data error: {e}")
        return None
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI hesapla"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period if losses else 0.001
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def find_surge_events(self, data: Dict, min_surge: float = 10) -> List[Dict]:
        """Geçmişteki yükseliş olaylarını bul"""
        events = []
        closes = data['close']
        volumes = data['volume']
        timestamps = data['timestamps']
        
        for i in range(3, len(closes) - 3):
            prev_3 = closes[i-3:i]
            if not prev_3:
                continue
            
            base_price = sum(prev_3) / len(prev_3)
            current_price = closes[i]
            surge_pct = ((current_price - base_price) / base_price) * 100
            
            if surge_pct >= min_surge:
                rsi_before = self.calculate_rsi(closes[:i])
                
                avg_vol = sum(volumes[max(0,i-7):i]) / 7 if i >= 7 else sum(volumes[:i]) / max(1, i)
                vol_spike = volumes[i] / avg_vol if avg_vol > 0 else 1
                
                if i + 3 < len(closes):
                    next_3_max = max(closes[i+1:i+4])
                    next_3_min = min(closes[i+1:i+4])
                    max_gain = ((next_3_max - current_price) / current_price) * 100
                    max_loss = ((next_3_min - current_price) / current_price) * 100
                else:
                    max_gain = 0
                    max_loss = 0
                
                if i + 7 < len(closes):
                    week_later = closes[i+7]
                    week_change = ((week_later - current_price) / current_price) * 100
                else:
                    week_change = None
                
                if surge_pct > 30:
                    pattern = "PARABOLIC"
                elif vol_spike > 2 and surge_pct > 15:
                    pattern = "VOLUME_BREAKOUT"
                elif rsi_before < 30:
                    pattern = "OVERSOLD_BOUNCE"
                elif surge_pct > 15:
                    pattern = "STRONG_SURGE"
                else:
                    pattern = "MODERATE_SURGE"
                
                events.append({
                    'timestamp': timestamps[i] if i < len(timestamps) else None,
                    'surge_pct': round(surge_pct, 1),
                    'rsi_before': round(rsi_before, 1),
                    'vol_spike': round(vol_spike, 2),
                    'pattern': pattern,
                    'outcome': {
                        'max_gain_3d': round(max_gain, 1),
                        'max_loss_3d': round(max_loss, 1),
                        'week_change': round(week_change, 1) if week_change else None
                    }
                })
        
        return events
    
    def analyze_current_surge(self, symbol: str, current_change: float) -> Dict:
        """Mevcut yükselişi geçmişle karşılaştır"""
        data = self.get_historical_data(symbol, 90)
        
        if not data or len(data['close']) < 20:
            return {
                'symbol': symbol,
                'analysis': "Yetersiz veri",
                'recommendation': "BEKLE",
                'confidence': 0,
                'similar_cases': 0
            }
        
        closes = data['close']
        volumes = data['volume']
        
        current_rsi = self.calculate_rsi(closes)
        avg_vol = sum(volumes[-7:]) / 7 if len(volumes) >= 7 else sum(volumes) / len(volumes)
        current_vol_spike = volumes[-1] / avg_vol if avg_vol > 0 else 1
        
        if current_change > 30:
            current_pattern = "PARABOLIC"
        elif current_vol_spike > 2 and current_change > 15:
            current_pattern = "VOLUME_BREAKOUT"
        elif current_rsi < 35:
            current_pattern = "OVERSOLD_BOUNCE"
        elif current_change > 15:
            current_pattern = "STRONG_SURGE"
        else:
            current_pattern = "MODERATE_SURGE"
        
        past_events = self.find_surge_events(data, min_surge=current_change * 0.7)
        
        similar_events = [e for e in past_events 
                         if abs(e['surge_pct'] - current_change) < current_change * 0.5
                         and e['pattern'] == current_pattern]
        
        if not similar_events:
            similar_events = past_events[:5]
        
        if similar_events:
            avg_max_gain = sum(e['outcome']['max_gain_3d'] for e in similar_events) / len(similar_events)
            avg_max_loss = sum(e['outcome']['max_loss_3d'] for e in similar_events) / len(similar_events)
            
            week_changes = [e['outcome']['week_change'] for e in similar_events if e['outcome']['week_change'] is not None]
            avg_week_change = sum(week_changes) / len(week_changes) if week_changes else 0
            
            positive_outcomes = sum(1 for e in similar_events if e['outcome']['max_gain_3d'] > abs(e['outcome']['max_loss_3d']))
            win_rate = (positive_outcomes / len(similar_events)) * 100
        else:
            avg_max_gain = 0
            avg_max_loss = 0
            avg_week_change = 0
            win_rate = 50
        
        if current_pattern == "PARABOLIC":
            analysis = f"⚠️ PARABOLİK YÜKSELİŞ!\nGeçmişte {len(similar_events)} benzer durumda:\n"
            analysis += f"• 3 gün içinde ort. %{avg_max_loss:.1f} düşüş\n"
            analysis += f"• Kar satışı riski: YÜKSEK"
            recommendation = "SATMA ZAMANI"
            confidence = 75
        elif current_pattern == "VOLUME_BREAKOUT":
            analysis = f"🚀 HACİM KIRILIMI!\nGeçmişte {len(similar_events)} benzer durumda:\n"
            analysis += f"• Başarı oranı: %{win_rate:.0f}\n"
            analysis += f"• Ort. 3 gün sonuç: %{avg_max_gain:.1f} kar potansiyeli"
            recommendation = "GÜÇLÜ AL" if win_rate > 60 else "DİKKATLİ AL"
            confidence = int(win_rate)
        elif current_pattern == "OVERSOLD_BOUNCE":
            analysis = f"📈 AŞIRI SATIM DÖNÜŞÜ!\nGeçmişte {len(similar_events)} benzer durumda:\n"
            analysis += f"• Başarı oranı: %{win_rate:.0f}\n"
            analysis += f"• 1 hafta sonra ort.: %{avg_week_change:.1f}"
            recommendation = "AL" if win_rate > 55 else "İZLE"
            confidence = int(win_rate)
        elif current_pattern == "STRONG_SURGE":
            analysis = f"💪 GÜÇLÜ YÜKSELİŞ\nGeçmişte {len(similar_events)} benzer durumda:\n"
            analysis += f"• Devam etme: %{win_rate:.0f}\n"
            analysis += f"• 3 gün max kayıp: %{abs(avg_max_loss):.1f}"
            recommendation = "BEKLE" if current_rsi > 70 else "AL"
            confidence = int(win_rate * 0.8)
        else:
            analysis = f"📊 ORTA DÜZEY YÜKSELİŞ\nGeçmişte {len(similar_events)} benzer durumda:\n"
            analysis += f"• Başarı: %{win_rate:.0f} | Risk: %{abs(avg_max_loss):.1f}"
            recommendation = "İZLE"
            confidence = 50
        
        return {
            'symbol': symbol,
            'current_change': current_change,
            'pattern': current_pattern,
            'rsi': round(current_rsi, 1),
            'vol_spike': round(current_vol_spike, 2),
            'analysis': analysis,
            'recommendation': recommendation,
            'confidence': confidence,
            'similar_cases': len(similar_events),
            'historical_stats': {
                'avg_max_gain_3d': round(avg_max_gain, 1),
                'avg_max_loss_3d': round(avg_max_loss, 1),
                'avg_week_change': round(avg_week_change, 1),
                'win_rate': round(win_rate, 0)
            }
        }
    
    def advanced_coin_analysis(self, symbol: str, price: float, change: float) -> Dict:
        """Tek coin için gelişmiş derin analiz"""
        data = self.get_historical_data(symbol, 90)
        btc_data = self.get_btc_data()
        
        result = {
            'symbol': symbol,
            'price': price,
            'change': change,
            'has_data': False
        }
        
        if not data or len(data['close']) < 20:
            return result
        
        closes = data['close']
        highs = data['high']
        lows = data['low']
        
        result['has_data'] = True
        
        high_90d = max(highs) if highs else price
        low_90d = min(lows) if lows else price
        result['fib'] = self.calculate_fibonacci_levels(high_90d, low_90d)
        
        result['sr'] = self.find_support_resistance(closes)
        
        result['trend'] = self.calculate_trend_channel(closes)
        
        result['rsi'] = self.calculate_rsi(closes)
        
        if btc_data:
            result['btc_corr'] = self.calculate_btc_correlation(closes, btc_data)
        else:
            result['btc_corr'] = {'correlation': 0, 'strength': 'UNKNOWN', 'divergence': False}
        
        result['risk_reward'] = self.calculate_risk_reward(
            price, 
            result['sr']['supports'], 
            result['sr']['resistances'],
            result['fib']
        )
        
        pattern_analysis = self.analyze_current_surge(symbol, change)
        result['pattern'] = pattern_analysis
        
        return result
    
    def deep_analysis_rising(self, rising_list: List[Dict]) -> str:
        """Yükselen coinler için MAX DERİN ANALİZ raporu - Türkçe açıklamalı"""
        msg = """🔬 <b>DERİN ANALİZ - MAX SEVİYE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>En detaylı teknik analiz + açıklamalar</i>

"""
        
        for coin in rising_list[:5]:
            symbol = coin.get('symbol', '')
            change = coin.get('change', 0)
            price = coin.get('price', 0)
            
            analysis = self.advanced_coin_analysis(symbol, price, change)
            
            if not analysis['has_data']:
                msg += f"<b>{symbol}</b> - Yetersiz veri\n\n"
                continue
            
            pattern = analysis['pattern']
            trend = analysis['trend']
            sr = analysis['sr']
            rr = analysis['risk_reward']
            btc = analysis['btc_corr']
            fib = analysis['fib']
            rsi = analysis['rsi']
            
            trend_tr = {
                "STRONG_UP": "🚀 ÇOK GÜÇLÜ YÜKSELİŞ (Tüm ortalamalar yukarı)",
                "UP": "📈 YÜKSELİŞ TRENDİ (Kısa vade yukarı)",
                "SIDEWAYS": "➡️ YATAY SEYİR (Kararsız piyasa)",
                "DOWN": "📉 DÜŞÜŞ TRENDİ (Kısa vade aşağı)",
                "STRONG_DOWN": "💥 SERT DÜŞÜŞ (Tüm ortalamalar aşağı)"
            }.get(trend['trend'], "❓ Belirsiz")
            
            pattern_tr = {
                "PARABOLIC": "🔥 PARABOLİK (Aşırı hızlı, düzeltme beklenir)",
                "VOLUME_BREAKOUT": "💎 HACİM KIRILIMI (Güçlü alıcı var)",
                "OVERSOLD_BOUNCE": "🔄 DİP DÖNÜŞÜ (Aşırı satımdan toparlanma)",
                "STRONG_SURGE": "💪 GÜÇLÜ ÇIKIŞ (%15+ sağlam yükseliş)",
                "MODERATE_SURGE": "📊 ORTA YÜKSELİŞ (%5-15 normal hareket)"
            }.get(pattern['pattern'], "📊 Normal hareket")
            
            btc_corr_tr = {
                "STRONG_POSITIVE": "🔗 BTC ile ÇOK BAĞLI (BTC düşerse bu da düşer)",
                "MODERATE_POSITIVE": "🔗 BTC ile BAĞLI (Genelde BTC'yi takip eder)",
                "WEAK": "⚡ BAĞIMSIZ (BTC'den etkilenmez)",
                "MODERATE_NEGATIVE": "↔️ TERS HAREKET (BTC yükselirken düşebilir)",
                "STRONG_NEGATIVE": "🔄 TAM TERS (BTC ile zıt hareket)"
            }.get(btc['strength'], "❓ Bilinmiyor")
            
            rr_tr = {
                "EXCELLENT": "🌟 MÜKEMMEL (3x+ kazanç/risk oranı - İDEAL GİRİŞ)",
                "GOOD": "✅ İYİ (2-3x oran - Güvenli giriş)",
                "FAIR": "🟡 ORTA (1-2x oran - Dikkatli ol)",
                "POOR": "🔴 KÖTÜ (1x altı - RİSKLİ, girme)"
            }.get(rr['rating'], "❓ Hesaplanamadı")
            
            if rr['ratio'] == 0:
                rr_explain = "⚠️ Hesaplanamadı (destek/direnç bulunamadı)"
            elif rr['ratio'] < 1:
                rr_explain = f"⛔ {rr['ratio']:.1f}x = Riskli! Kaybetme ihtimalin kazanmadan yüksek"
            elif rr['ratio'] < 2:
                rr_explain = f"🟡 {rr['ratio']:.1f}x = Orta. Her ₺1 risk için ₺{rr['ratio']:.1f} potansiyel"
            elif rr['ratio'] < 3:
                rr_explain = f"✅ {rr['ratio']:.1f}x = İyi! Her ₺1 risk için ₺{rr['ratio']:.1f} potansiyel"
            else:
                rr_explain = f"🌟 {rr['ratio']:.1f}x = Harika! Her ₺1 risk için ₺{rr['ratio']:.1f} potansiyel"
            
            if trend['channel_position'] >= 80:
                kanal_aciklama = "⚠️ ZİRVEYE YAKIN! Kar al veya bekle"
            elif trend['channel_position'] >= 60:
                kanal_aciklama = "📈 Üst bölgede, yükseliş güçlü"
            elif trend['channel_position'] >= 40:
                kanal_aciklama = "➡️ Ortada, her yöne gidebilir"
            elif trend['channel_position'] >= 20:
                kanal_aciklama = "📉 Alt bölgede, dip yakın olabilir"
            else:
                kanal_aciklama = "🟢 DİPTE! Alım fırsatı olabilir"
            
            if rsi >= 70:
                rsi_aciklama = "🔴 AŞIRI ALIM - Düzeltme gelebilir"
            elif rsi >= 60:
                rsi_aciklama = "🟡 Yüksek - Dikkatli ol"
            elif rsi >= 40:
                rsi_aciklama = "🟢 Normal bölge"
            elif rsi >= 30:
                rsi_aciklama = "🟡 Düşük - Fırsat olabilir"
            else:
                rsi_aciklama = "🟢 AŞIRI SATIM - Alım fırsatı!"
            
            zone_text = {
                "RESISTANCE": "⚠️ DİRENÇ BÖLGESİ (Satış baskısı olabilir)",
                "SUPPORT": "🟢 DESTEK BÖLGESİ (Alıcılar burada)",
                "MIDDLE": "🔵 ORTA BÖLGE (Net sinyal yok)"
            }.get(sr['current_zone'], "")
            
            rec_emoji = {
                "GÜÇLÜ AL": "🟢🟢",
                "AL": "🟢",
                "DİKKATLİ AL": "🟡",
                "İZLE": "🔵",
                "BEKLE": "⏸️",
                "SATMA ZAMANI": "🔴"
            }.get(pattern['recommendation'], "⚪")
            
            msg += f"""<b>━━━ {symbol} ━━━</b>
💰 Fiyat: ₺{price:,.4f} | Değişim: <b>+{change:.1f}%</b>

📊 <b>TREND ANALİZİ:</b>
{trend_tr}
   
📍 <b>KANAL POZİSYONU: %{trend['channel_position']:.0f}</b>
{kanal_aciklama}
<i>(Son 20 günün en düşüğü %0, en yükseği %100)</i>

🎯 <b>HAREKET TİPİ:</b>
{pattern_tr}

📈 <b>RSI: {rsi:.0f}</b>
{rsi_aciklama}

🔗 <b>BTC KORELASYONU: {btc['correlation']:.2f}</b>
{btc_corr_tr}
{"⚡ <b>DİVERJANS VAR!</b> BTC'den bağımsız hareket ediyor!" if btc['divergence'] else ""}

📐 <b>FİBONACCİ SEVİYELERİ:</b>
<i>(Fiyatın döneceği olası noktalar)</i>
   • %38.2 düzeltme: ₺{fib['0.382']:,.4f}
   • %61.8 düzeltme: ₺{fib['0.618']:,.4f}
   • %127.2 hedef: ₺{fib['ext_1.272']:,.4f}

📍 <b>BÖLGE:</b> {zone_text}

💎 <b>RİSK/ÖDÜL ANALİZİ:</b>
{rr_tr}
{rr_explain}

   🎯 HEDEF: ₺{rr['target']:,.4f} (+%{rr['potential_gain_pct']:.1f} potansiyel kar)
   🛑 STOP: ₺{rr['stop']:,.4f} (-%{rr['potential_loss_pct']:.1f} max kayıp)

{rec_emoji} <b>SONUÇ: {pattern['recommendation']}</b>
📊 Güven: %{pattern['confidence']} | Geçmişte {pattern['similar_cases']} benzer vaka

━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        msg += """📚 <b>TERİMLER SÖZLÜĞÜ:</b>

<b>🔹 TREND TİPLERİ:</b>
• <b>GÜÇLÜ YÜKSELİŞ:</b> Tüm ortalamalar (7-20-50 gün) yukarı bakıyor
• <b>YÜKSELİŞ:</b> Kısa vadeli ortalama yukarı
• <b>YATAY:</b> Kararsız, yön belli değil
• <b>DÜŞÜŞ:</b> Kısa vadeli ortalama aşağı

<b>🔹 HAREKET TİPLERİ:</b>
• <b>PARABOLİK:</b> %30+ ani çıkış, genelde düzeltme gelir
• <b>HACİM KIRILIMI:</b> Yüksek hacimle yükseliş, güçlü sinyal
• <b>DİP DÖNÜŞÜ:</b> Aşırı satımdan toparlanma
• <b>GÜÇLÜ ÇIKIŞ:</b> %15-30 sağlam yükseliş
• <b>ORTA YÜKSELİŞ:</b> %5-15 normal hareket

<b>🔹 RİSK/ÖDÜL ORANI:</b>
• <b>3x+:</b> Mükemmel! ₺1 risk = ₺3+ potansiyel
• <b>2-3x:</b> İyi giriş noktası
• <b>1-2x:</b> Orta, dikkatli ol
• <b>1x altı:</b> Riskli, bekleme tavsiyesi

<b>🔹 KANAL POZİSYONU:</b>
• <b>%80+:</b> Zirveye yakın, kar satışı gelebilir
• <b>%50:</b> Orta bölge
• <b>%20-:</b> Dip bölgesi, alım fırsatı

<b>🔹 BTC KORELASYONU:</b>
• <b>+0.7 üzeri:</b> BTC ile çok bağlı
• <b>+0.4 ile +0.7:</b> Kısmen bağlı
• <b>-0.4 ile +0.4:</b> Bağımsız hareket
• <b>-0.7 altı:</b> BTC ile ters hareket

⚠️ Bu veriler yatırım tavsiyesi değildir!
Geçmiş performans gelecek için garanti değildir.
"""
        return msg

historical_analyzer = HistoricalPatternAnalyzer()
