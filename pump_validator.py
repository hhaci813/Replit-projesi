"""
🔍 PUMP DOĞRULAMA SİSTEMİ - MAX VERSİYON
Sahte pump vs Gerçek pump ayrımı yapar
Mum dikmiş coinlerin derin analizini yapar
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import time

logger = logging.getLogger(__name__)

class PumpValidator:
    """
    Pump Doğrulama Sistemi
    Bir coin mum diktiğinde gerçek mi sahte mi analiz eder
    """
    
    def __init__(self):
        self.pump_history = {}
        self.fake_pump_patterns = []
    
    def get_btcturk_data(self) -> List[Dict]:
        """BTCTurk verilerini al"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=15)
            return resp.json().get('data', [])
        except:
            return []
    
    def get_ohlcv_data(self, symbol: str, days: int = 30) -> Dict:
        """OHLCV verilerini al"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}-USD")
            hist = ticker.history(period=f"{days}d")
            if len(hist) > 0:
                return {
                    'opens': hist['Open'].tolist(),
                    'highs': hist['High'].tolist(),
                    'lows': hist['Low'].tolist(),
                    'closes': hist['Close'].tolist(),
                    'volumes': hist['Volume'].tolist()
                }
        except:
            pass
        return {'opens': [], 'highs': [], 'lows': [], 'closes': [], 'volumes': []}
    
    def analyze_candle_structure(self, opens: List[float], highs: List[float], 
                                   lows: List[float], closes: List[float]) -> Dict:
        """
        Mum yapısı analizi
        - Uzun üst gölge = satış baskısı, tuzak olabilir
        - Uzun alt gölge = alım baskısı, destek var
        - Doji = kararsızlık
        """
        if len(closes) < 2:
            return {'signal': 'UNKNOWN', 'reliability': 0}
        
        last_open = opens[-1]
        last_high = highs[-1]
        last_low = lows[-1]
        last_close = closes[-1]
        
        body = abs(last_close - last_open)
        total_range = last_high - last_low if last_high > last_low else 0.0001
        
        upper_shadow = last_high - max(last_open, last_close)
        lower_shadow = min(last_open, last_close) - last_low
        
        upper_shadow_ratio = upper_shadow / total_range
        lower_shadow_ratio = lower_shadow / total_range
        body_ratio = body / total_range
        
        signals = []
        warning_score = 0
        
        if upper_shadow_ratio > 0.6:
            signals.append("🔴 UZUN ÜST GÖLGE - Yukarıda güçlü satış baskısı!")
            warning_score += 30
        
        if upper_shadow_ratio > 0.4 and body_ratio < 0.2:
            signals.append("🔴 SHOOTING STAR - Zirve tuzağı olabilir!")
            warning_score += 25
        
        if lower_shadow_ratio > 0.6:
            signals.append("🟢 UZUN ALT GÖLGE - Aşağıda güçlü alım desteği")
            warning_score -= 15
        
        if body_ratio < 0.1:
            signals.append("🟡 DOJI - Piyasa kararsız, trend dönebilir")
            warning_score += 10
        
        if last_close < last_open and upper_shadow_ratio > 0.3:
            signals.append("🔴 BEARISH ENGULFING benzeri - Düşüş sinyali")
            warning_score += 20
        
        prev_changes = []
        for i in range(1, min(6, len(closes))):
            change = (closes[-i] - closes[-i-1]) / closes[-i-1] * 100 if len(closes) > i else 0
            prev_changes.append(change)
        
        if len(prev_changes) >= 3:
            consecutive_up = sum(1 for c in prev_changes[:3] if c > 3)
            if consecutive_up >= 3:
                signals.append("⚠️ 3+ GÜN ARKA ARKAYA YÜKSELIŞ - Düzeltme riski!")
                warning_score += 20
        
        if warning_score >= 50:
            result = "TUZAK_RISKI_YUKSEK"
            reliability = 80
        elif warning_score >= 30:
            result = "DIKKATLI_OL"
            reliability = 60
        elif warning_score <= -10:
            result = "GERCEK_YUKSELIS"
            reliability = 70
        else:
            result = "BELIRSIZ"
            reliability = 40
        
        return {
            'signal': result,
            'reliability': reliability,
            'warning_score': warning_score,
            'upper_shadow_ratio': round(upper_shadow_ratio * 100, 1),
            'lower_shadow_ratio': round(lower_shadow_ratio * 100, 1),
            'body_ratio': round(body_ratio * 100, 1),
            'signals': signals
        }
    
    def analyze_volume_quality(self, volumes: List[float], closes: List[float]) -> Dict:
        """
        Hacim kalitesi analizi
        - Ani hacim patlaması = manipülasyon olabilir
        - Kademeli hacim artışı = sağlıklı
        - Hacim azalırken fiyat artışı = sahte pump
        """
        if len(volumes) < 10:
            return {'quality': 'UNKNOWN', 'score': 50}
        
        avg_volume_7d = np.mean(volumes[-7:])
        avg_volume_30d = np.mean(volumes[-30:]) if len(volumes) >= 30 else avg_volume_7d
        current_volume = volumes[-1]
        
        volume_spike_ratio = current_volume / avg_volume_30d if avg_volume_30d > 0 else 1
        
        signals = []
        quality_score = 50
        
        if volume_spike_ratio > 10:
            signals.append("🔴 ANI HACİM PATLAMASI (10x+) - Manipülasyon şüphesi!")
            quality_score -= 40
        elif volume_spike_ratio > 5:
            signals.append("🟡 YÜKSEK HACİM ARTIŞI (5x) - Dikkatli ol")
            quality_score -= 20
        elif volume_spike_ratio > 2:
            signals.append("🟢 NORMAL HACİM ARTIŞI - Sağlıklı görünüyor")
            quality_score += 10
        
        if len(volumes) >= 5:
            recent_volumes = volumes[-5:]
            volume_trend = (recent_volumes[-1] - recent_volumes[0]) / recent_volumes[0] * 100 if recent_volumes[0] > 0 else 0
            
            price_change = (closes[-1] - closes[-5]) / closes[-5] * 100 if len(closes) >= 5 and closes[-5] > 0 else 0
            
            if price_change > 10 and volume_trend < -20:
                signals.append("🔴 FİYAT ARTIYOR AMA HACİM DÜŞÜYOR - SAHTE PUMP!")
                quality_score -= 35
            elif price_change > 5 and volume_trend > 50:
                signals.append("🟢 Fiyat ve hacim birlikte artıyor - Sağlıklı")
                quality_score += 15
        
        volume_volatility = np.std(volumes[-7:]) / avg_volume_7d if avg_volume_7d > 0 else 0
        if volume_volatility > 2:
            signals.append("🟡 HACİM ÇOK DALGALI - Dengesiz piyasa")
            quality_score -= 10
        
        if quality_score >= 60:
            quality = "SAGLIKLI"
        elif quality_score >= 40:
            quality = "ORTA"
        elif quality_score >= 20:
            quality = "SUPHELI"
        else:
            quality = "MANIPULASYON_RISKI"
        
        return {
            'quality': quality,
            'score': quality_score,
            'volume_spike_ratio': round(volume_spike_ratio, 2),
            'current_volume': current_volume,
            'avg_volume_30d': avg_volume_30d,
            'signals': signals
        }
    
    def analyze_historical_pumps(self, symbol: str, closes: List[float], volumes: List[float]) -> Dict:
        """
        Tarihsel pump analizi
        Bu coin daha önce pump yaptığında ne olmuş?
        """
        if len(closes) < 30:
            return {'pattern': 'YETERSIZ_VERI', 'fake_pump_count': 0}
        
        pump_events = []
        
        for i in range(7, len(closes)):
            daily_change = (closes[i] - closes[i-1]) / closes[i-1] * 100 if closes[i-1] > 0 else 0
            
            if daily_change > 15:
                next_3_days = closes[i+1:i+4] if i+4 <= len(closes) else closes[i+1:]
                
                if len(next_3_days) >= 2:
                    after_pump_change = (next_3_days[-1] - closes[i]) / closes[i] * 100 if closes[i] > 0 else 0
                    
                    pump_events.append({
                        'date_index': i,
                        'pump_percent': round(daily_change, 1),
                        'after_3_days': round(after_pump_change, 1),
                        'was_fake': after_pump_change < -10
                    })
        
        fake_pump_count = sum(1 for p in pump_events if p['was_fake'])
        total_pumps = len(pump_events)
        
        if total_pumps == 0:
            pattern = "ILK_PUMP"
            reliability = 30
            warning = "⚠️ Bu coin daha önce pump yapmamış - Dikkatli ol"
        elif fake_pump_count / total_pumps > 0.6:
            pattern = "SAHTE_PUMP_GECMISI"
            reliability = 20
            warning = f"🔴 Bu coin {total_pumps} pump'ın {fake_pump_count}'i sahte çıkmış! UZAK DUR!"
        elif fake_pump_count / total_pumps > 0.3:
            pattern = "KARISIK_GECMIS"
            reliability = 50
            warning = f"🟡 Karma geçmiş: {fake_pump_count}/{total_pumps} sahte pump"
        else:
            pattern = "GUVENILIR_GECMIS"
            reliability = 75
            warning = f"🟢 Güvenilir: Çoğu pump gerçek çıkmış ({total_pumps - fake_pump_count}/{total_pumps})"
        
        return {
            'pattern': pattern,
            'reliability': reliability,
            'total_pumps': total_pumps,
            'fake_pump_count': fake_pump_count,
            'real_pump_count': total_pumps - fake_pump_count,
            'warning': warning,
            'pump_events': pump_events[-5:]
        }
    
    def analyze_market_cap_risk(self, symbol: str, volume: float, price: float) -> Dict:
        """
        Market cap ve likidite riski analizi
        Düşük market cap = kolay manipülasyon
        """
        try:
            resp = requests.get(
                f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}",
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                market_cap = data.get('market_data', {}).get('market_cap', {}).get('usd', 0)
                total_volume = data.get('market_data', {}).get('total_volume', {}).get('usd', 0)
                
                if market_cap > 0:
                    volume_to_mcap = total_volume / market_cap * 100
                else:
                    volume_to_mcap = 0
                
                signals = []
                risk_score = 50
                
                if market_cap < 10_000_000:
                    signals.append("🔴 ÇOK DÜŞÜK MARKET CAP (<$10M) - Kolay manipüle edilir!")
                    risk_score += 40
                elif market_cap < 50_000_000:
                    signals.append("🟡 DÜŞÜK MARKET CAP (<$50M) - Manipülasyon riski var")
                    risk_score += 25
                elif market_cap < 500_000_000:
                    signals.append("🟢 ORTA MARKET CAP - Normal risk")
                    risk_score += 0
                else:
                    signals.append("🟢 YÜKSEK MARKET CAP - Manipülasyon zor")
                    risk_score -= 20
                
                if volume_to_mcap > 50:
                    signals.append("🔴 HACİM/MCAP ÇOK YÜKSEK - Anormal aktivite!")
                    risk_score += 30
                elif volume_to_mcap > 20:
                    signals.append("🟡 HACİM/MCAP YÜKSEK - Dikkat")
                    risk_score += 15
                
                return {
                    'market_cap': market_cap,
                    'market_cap_formatted': f"${market_cap/1_000_000:.1f}M" if market_cap > 0 else "Bilinmiyor",
                    'volume_to_mcap': round(volume_to_mcap, 1),
                    'risk_score': risk_score,
                    'signals': signals
                }
        except Exception as e:
            logger.debug(f"CoinGecko error: {e}")
        
        estimated_mcap = volume * 20
        
        signals = []
        if estimated_mcap < 50_000_000:
            signals.append("🟡 Tahmini düşük market cap - Dikkatli ol")
            risk_score = 60
        else:
            signals.append("⚪ Market cap verisi alınamadı")
            risk_score = 50
        
        return {
            'market_cap': estimated_mcap,
            'market_cap_formatted': f"~${estimated_mcap/1_000_000:.1f}M (tahmini)",
            'volume_to_mcap': 0,
            'risk_score': risk_score,
            'signals': signals
        }
    
    def detect_whale_activity(self, volumes: List[float], closes: List[float]) -> Dict:
        """
        Balina aktivitesi tespiti
        Büyük oyuncuların hareketlerini analiz eder
        """
        if len(volumes) < 14:
            return {'whale_detected': False, 'signal': 'YETERSIZ_VERI'}
        
        avg_volume = np.mean(volumes[-14:])
        std_volume = np.std(volumes[-14:])
        
        signals = []
        whale_score = 0
        
        for i in range(-3, 0):
            if volumes[i] > avg_volume + (3 * std_volume):
                signals.append(f"🐋 {-i} gün önce BALINA HAREKETİ tespit edildi!")
                whale_score += 30
        
        if len(volumes) >= 5:
            recent_avg = np.mean(volumes[-3:])
            prev_avg = np.mean(volumes[-7:-3])
            
            if recent_avg > prev_avg * 3:
                signals.append("🐋 Son 3 günde hacim 3x arttı - Büyük oyuncu girişi olabilir")
                whale_score += 25
        
        price_change = (closes[-1] - closes[-7]) / closes[-7] * 100 if closes[-7] > 0 else 0
        if price_change < -5 and volumes[-1] > avg_volume * 2:
            signals.append("🔴 BALINA SATIŞI! Yüksek hacimde düşüş")
            whale_score -= 40
        elif price_change > 10 and volumes[-1] > avg_volume * 2:
            signals.append("🟢 BALINA ALIMI! Yüksek hacimde yükseliş")
            whale_score += 20
        
        if whale_score > 30:
            whale_type = "ALIM_AKTIVITESI"
            warning = "🐋 Büyük oyuncular alım yapıyor olabilir"
        elif whale_score < -20:
            whale_type = "SATIS_AKTIVITESI"
            warning = "🔴 Büyük oyuncular satış yapıyor!"
        elif whale_score != 0:
            whale_type = "AKTIF"
            warning = "🟡 Balina aktivitesi var - Dikkatli ol"
        else:
            whale_type = "NORMAL"
            warning = "⚪ Normal piyasa aktivitesi"
        
        return {
            'whale_detected': whale_score != 0,
            'whale_type': whale_type,
            'whale_score': whale_score,
            'warning': warning,
            'signals': signals
        }
    
    def calculate_pump_reliability_score(self, symbol: str) -> Dict:
        """
        Pump güvenilirlik skoru hesapla
        Tüm analizleri birleştirerek final skor ver
        """
        ohlcv = self.get_ohlcv_data(symbol, 60)
        
        if not ohlcv['closes']:
            return {
                'symbol': symbol,
                'reliability_score': 0,
                'verdict': 'VERI_YOK',
                'recommendation': 'Analiz yapılamadı - Veri yok'
            }
        
        candle = self.analyze_candle_structure(
            ohlcv['opens'], ohlcv['highs'], ohlcv['lows'], ohlcv['closes']
        )
        
        volume = self.analyze_volume_quality(ohlcv['volumes'], ohlcv['closes'])
        
        historical = self.analyze_historical_pumps(symbol, ohlcv['closes'], ohlcv['volumes'])
        
        current_volume = ohlcv['volumes'][-1] if ohlcv['volumes'] else 0
        current_price = ohlcv['closes'][-1] if ohlcv['closes'] else 0
        market_cap = self.analyze_market_cap_risk(symbol, current_volume, current_price)
        
        whale = self.detect_whale_activity(ohlcv['volumes'], ohlcv['closes'])
        
        final_score = 50
        
        if candle['signal'] == 'TUZAK_RISKI_YUKSEK':
            final_score -= 25
        elif candle['signal'] == 'DIKKATLI_OL':
            final_score -= 10
        elif candle['signal'] == 'GERCEK_YUKSELIS':
            final_score += 15
        
        if volume['quality'] == 'MANIPULASYON_RISKI':
            final_score -= 30
        elif volume['quality'] == 'SUPHELI':
            final_score -= 15
        elif volume['quality'] == 'SAGLIKLI':
            final_score += 15
        
        if historical['pattern'] == 'SAHTE_PUMP_GECMISI':
            final_score -= 35
        elif historical['pattern'] == 'KARISIK_GECMIS':
            final_score -= 10
        elif historical['pattern'] == 'GUVENILIR_GECMIS':
            final_score += 20
        
        if market_cap['risk_score'] > 70:
            final_score -= 20
        elif market_cap['risk_score'] < 40:
            final_score += 10
        
        if whale['whale_type'] == 'SATIS_AKTIVITESI':
            final_score -= 25
        elif whale['whale_type'] == 'ALIM_AKTIVITESI':
            final_score += 15
        
        final_score = max(0, min(100, final_score))
        
        if final_score >= 70:
            verdict = "GERCEK_PUMP"
            recommendation = "🟢 Güvenilir görünüyor - Alım düşünülebilir"
            action = "AL"
        elif final_score >= 50:
            verdict = "BELIRSIZ"
            recommendation = "🟡 Belirsiz - Daha fazla onay bekle"
            action = "BEKLE"
        elif final_score >= 30:
            verdict = "SUPHELI_PUMP"
            recommendation = "🟠 Şüpheli pump - Dikkatli ol"
            action = "DIKKATLI_OL"
        else:
            verdict = "SAHTE_PUMP"
            recommendation = "🔴 SAHTE PUMP! UZAK DUR!"
            action = "UZAK_DUR"
        
        all_warnings = []
        all_warnings.extend(candle.get('signals', []))
        all_warnings.extend(volume.get('signals', []))
        all_warnings.append(historical.get('warning', ''))
        all_warnings.extend(market_cap.get('signals', []))
        all_warnings.extend(whale.get('signals', []))
        all_warnings = [w for w in all_warnings if w]
        
        return {
            'symbol': symbol,
            'reliability_score': final_score,
            'verdict': verdict,
            'action': action,
            'recommendation': recommendation,
            'analysis': {
                'candle': candle,
                'volume': volume,
                'historical': historical,
                'market_cap': market_cap,
                'whale': whale
            },
            'warnings': all_warnings[:10],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    
    def format_pump_analysis_message(self, analysis: Dict) -> str:
        """Telegram için pump analiz mesajı oluştur"""
        symbol = analysis['symbol']
        score = analysis['reliability_score']
        verdict = analysis['verdict']
        action = analysis['action']
        
        if score >= 70:
            score_emoji = "🟢"
        elif score >= 50:
            score_emoji = "🟡"
        elif score >= 30:
            score_emoji = "🟠"
        else:
            score_emoji = "🔴"
        
        msg = f"""🔍 <b>PUMP DOĞRULAMA - {symbol}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━

{score_emoji} <b>GÜVENİLİRLİK: {score}/100</b>
📊 <b>SONUÇ: {verdict}</b>
🎯 <b>AKSİYON: {action}</b>

{analysis['recommendation']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>📋 DETAYLI ANALİZ:</b>

"""
        
        candle = analysis['analysis']['candle']
        msg += f"🕯 <b>Mum Yapısı:</b> {candle['signal']}\n"
        msg += f"   Üst Gölge: %{candle['upper_shadow_ratio']} | Alt Gölge: %{candle['lower_shadow_ratio']}\n\n"
        
        volume = analysis['analysis']['volume']
        msg += f"📊 <b>Hacim Kalitesi:</b> {volume['quality']}\n"
        msg += f"   Hacim Spike: {volume['volume_spike_ratio']}x\n\n"
        
        historical = analysis['analysis']['historical']
        msg += f"📜 <b>Geçmiş:</b> {historical['pattern']}\n"
        msg += f"   Sahte/Toplam: {historical['fake_pump_count']}/{historical['total_pumps']}\n\n"
        
        market_cap = analysis['analysis']['market_cap']
        msg += f"💰 <b>Market Cap:</b> {market_cap['market_cap_formatted']}\n\n"
        
        whale = analysis['analysis']['whale']
        msg += f"🐋 <b>Balina:</b> {whale['whale_type']}\n\n"
        
        if analysis['warnings']:
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += "<b>⚠️ UYARILAR:</b>\n\n"
            for warning in analysis['warnings'][:5]:
                msg += f"• {warning}\n"
        
        msg += f"\n⏰ {analysis['timestamp']}"
        
        return msg
    
    def should_send_signal(self, symbol: str) -> Dict:
        """
        Sinyal gönderilmeli mi?
        Pump validator + diğer filtreler
        """
        analysis = self.calculate_pump_reliability_score(symbol)
        
        if analysis['reliability_score'] < 50:
            return {
                'should_send': False,
                'reason': f"Güvenilirlik düşük: {analysis['reliability_score']}/100",
                'analysis': analysis
            }
        
        if analysis['verdict'] in ['SAHTE_PUMP', 'SUPHELI_PUMP']:
            return {
                'should_send': False,
                'reason': f"Pump şüpheli: {analysis['verdict']}",
                'analysis': analysis
            }
        
        return {
            'should_send': True,
            'reason': f"Güvenilir pump: {analysis['reliability_score']}/100",
            'analysis': analysis
        }


pump_validator = PumpValidator()
