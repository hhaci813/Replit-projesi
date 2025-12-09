"""
TARİHSEL PATTERN ANALİZCİSİ
Yükselen kriptoları geçmiş verilerle karşılaştır
"Bu coin daha önce böyle yükseldi, sonra X oldu" analizi
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class HistoricalPatternAnalyzer:
    def __init__(self):
        self.cache_file = "historical_events.json"
        self.events = self.load_events()
        
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
    
    def deep_analysis_rising(self, rising_list: List[Dict]) -> str:
        """Yükselen coinler için derin analiz raporu"""
        msg = """🔬 <b>DERİN TARİHSEL ANALİZ</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Geçmiş 90 günlük verilerle karşılaştırma</i>

"""
        
        for coin in rising_list[:5]:
            symbol = coin.get('symbol', '')
            change = coin.get('change', 0)
            price = coin.get('price', 0)
            
            analysis = self.analyze_current_surge(symbol, change)
            
            rec_emoji = {
                "GÜÇLÜ AL": "🟢",
                "AL": "🟢",
                "DİKKATLİ AL": "🟡",
                "İZLE": "🔵",
                "BEKLE": "🟡",
                "SATMA ZAMANI": "🔴"
            }.get(analysis['recommendation'], "⚪")
            
            msg += f"""<b>{symbol}</b> +{change:.1f}%
💰 ₺{price:,.4f}
📊 RSI: {analysis['rsi']} | Hacim: {analysis['vol_spike']}x
🔍 Pattern: {analysis['pattern']}

{analysis['analysis']}

{rec_emoji} <b>TAVSİYE: {analysis['recommendation']}</b>
📈 Güven: %{analysis['confidence']}

"""
            if analysis['similar_cases'] > 0:
                stats = analysis['historical_stats']
                msg += f"""<i>📜 {analysis['similar_cases']} benzer vaka analizi:
   • Başarı oranı: %{stats['win_rate']:.0f}
   • 3g max kar: %{stats['avg_max_gain_3d']:.1f}
   • 3g max kayıp: %{stats['avg_max_loss_3d']:.1f}
   • 1 hafta sonra: %{stats['avg_week_change']:.1f}</i>

"""
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        msg += """💡 <b>PATTERN AÇIKLAMALARI:</b>
• <b>PARABOLIC:</b> Çok hızlı yükseliş, düşme riski yüksek
• <b>VOLUME_BREAKOUT:</b> Hacimle kırılım, devam potansiyeli
• <b>OVERSOLD_BOUNCE:</b> Dipten dönüş, iyi fırsat olabilir
• <b>STRONG_SURGE:</b> Güçlü hareket, momentum takibi

⚠️ Geçmiş performans gelecek sonuçları garanti etmez!
"""
        return msg

historical_analyzer = HistoricalPatternAnalyzer()
