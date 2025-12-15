"""
⚡ HYBRİD SCALPING SİSTEMİ - 5/15/30 DAKİKA
Sinyal tarama: 15 dk | Pozisyon kontrolü: 5 dk | Max tutma: 30 dk
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import time
import os
import json

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

SCALP_DATA_FILE = "scalp_positions.json"

class ScalpingSystem:
    """
    Hybrid Scalping Sistemi
    - Sinyal tarama: Her 15 dakikada
    - Pozisyon kontrolü: Her 5 dakikada
    - Max tutma süresi: 30 dakika
    """
    
    def __init__(self):
        self.active_scalps = []
        self.completed_scalps = []
        self.last_scan_time = None
        self.last_check_time = None
        self.load_positions()
    
    def save_positions(self):
        """Pozisyonları dosyaya kaydet"""
        try:
            data = {
                'active': self.active_scalps,
                'completed': self.completed_scalps[-50:],
                'last_scan': self.last_scan_time.isoformat() if self.last_scan_time else None
            }
            with open(SCALP_DATA_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Pozisyon kaydetme hatası: {e}")
    
    def load_positions(self):
        """Pozisyonları dosyadan yükle"""
        try:
            if os.path.exists(SCALP_DATA_FILE):
                with open(SCALP_DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.active_scalps = data.get('active', [])
                    self.completed_scalps = data.get('completed', [])
                    if data.get('last_scan'):
                        self.last_scan_time = datetime.fromisoformat(data['last_scan'])
        except Exception as e:
            logger.error(f"Pozisyon yükleme hatası: {e}")
    
    def get_btcturk_data(self) -> List[Dict]:
        """BTCTurk verilerini al"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=15)
            return resp.json().get('data', [])
        except Exception as e:
            logger.error(f"BTCTurk API error: {e}")
            return []
    
    def calculate_short_rsi(self, prices: List[float], period: int = 7) -> float:
        """Kısa periyot RSI (7 periyot - scalping için)"""
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
        return round(100 - (100 / (1 + rs)), 1)
    
    def calculate_momentum(self, prices: List[float]) -> Dict:
        """Anlık momentum hesapla"""
        if len(prices) < 5:
            return {'score': 0, 'direction': 'FLAT', 'strength': 'WEAK'}
        
        change_1 = (prices[-1] - prices[-2]) / prices[-2] * 100 if prices[-2] > 0 else 0
        change_3 = (prices[-1] - prices[-4]) / prices[-4] * 100 if len(prices) >= 4 and prices[-4] > 0 else 0
        change_5 = (prices[-1] - prices[-6]) / prices[-6] * 100 if len(prices) >= 6 and prices[-6] > 0 else 0
        
        score = (change_1 * 3) + (change_3 * 2) + change_5
        
        if score > 5:
            direction = 'STRONG_UP'
            strength = 'STRONG'
        elif score > 2:
            direction = 'UP'
            strength = 'MODERATE'
        elif score > 0.5:
            direction = 'SLIGHT_UP'
            strength = 'WEAK'
        elif score < -5:
            direction = 'STRONG_DOWN'
            strength = 'STRONG'
        elif score < -2:
            direction = 'DOWN'
            strength = 'MODERATE'
        elif score < -0.5:
            direction = 'SLIGHT_DOWN'
            strength = 'WEAK'
        else:
            direction = 'FLAT'
            strength = 'NONE'
        
        return {
            'score': round(score, 2),
            'direction': direction,
            'strength': strength,
            'change_1': round(change_1, 2),
            'change_3': round(change_3, 2),
            'change_5': round(change_5, 2)
        }
    
    def get_short_term_prices(self, symbol: str) -> List[float]:
        """YFinance'dan kısa vadeli fiyat verisi al"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}-USD")
            hist = ticker.history(period="5d", interval="1h")
            if len(hist) > 0:
                return hist['Close'].tolist()
        except:
            pass
        return []
    
    def analyze_scalp_opportunity(self, ticker: Dict) -> Optional[Dict]:
        """
        Scalping fırsatı analizi - GELİŞTİRİLMİŞ
        """
        pair = ticker.get('pairNormalized', '')
        if '_TRY' not in pair:
            return None
        
        symbol = pair.split('_')[0]
        price = float(ticker.get('last', 0))
        daily_change = float(ticker.get('dailyPercent', 0))
        volume = float(ticker.get('volume', 0))
        high = float(ticker.get('high', 0))
        low = float(ticker.get('low', 0))
        bid = float(ticker.get('bid', 0))
        ask = float(ticker.get('ask', 0))
        
        if price <= 0:
            return None
        
        spread = ((ask - bid) / price * 100) if price > 0 else 0
        if spread > 1:
            return None
        
        if high > 0 and low > 0 and high != low:
            channel_position = ((price - low) / (high - low)) * 100
        else:
            channel_position = 50
        
        scalp_score = 0
        signals = []
        warnings = []
        
        prices = self.get_short_term_prices(symbol)
        
        short_rsi = 50
        momentum_data = {'score': 0, 'direction': 'FLAT'}
        
        if prices and len(prices) >= 10:
            short_rsi = self.calculate_short_rsi(prices, period=7)
            momentum_data = self.calculate_momentum(prices)
            
            if momentum_data['direction'] in ['STRONG_UP', 'UP']:
                scalp_score += 25
                signals.append(f"🚀 Momentum: {momentum_data['direction']}")
            elif momentum_data['direction'] in ['STRONG_DOWN', 'DOWN']:
                scalp_score -= 20
                warnings.append("📉 Negatif momentum")
            
            if 30 < short_rsi < 60:
                scalp_score += 20
                signals.append(f"✅ RSI: {short_rsi:.0f}")
            elif short_rsi > 70:
                scalp_score -= 25
                warnings.append(f"🔴 RSI aşırı alım: {short_rsi:.0f}")
                return None
            elif short_rsi < 30:
                scalp_score += 15
                signals.append(f"🟢 RSI düşük: {short_rsi:.0f}")
        
        if 1 < daily_change < 6:
            scalp_score += 20
            signals.append(f"📈 +{daily_change:.1f}%")
        elif daily_change >= 8:
            warnings.append("⚠️ Çok yükselmiş")
            scalp_score -= 20
            return None
        elif daily_change < 0:
            warnings.append("📉 Düşüşte")
            scalp_score -= 15
        
        if 25 < channel_position < 65:
            scalp_score += 20
            signals.append("🎯 Kanal OK")
        elif channel_position > 85:
            warnings.append("🔴 Zirve!")
            scalp_score -= 30
            return None
        elif channel_position < 20:
            scalp_score += 10
            signals.append("🟢 Dip")
        
        if volume > 500000:
            scalp_score += 10
            signals.append("💰 Hacim OK")
        elif volume < 100000:
            warnings.append("⚠️ Düşük hacim")
            scalp_score -= 15
        
        if spread < 0.2:
            scalp_score += 10
        elif spread > 0.5:
            scalp_score -= 10
        
        if scalp_score < 50:
            return None
        
        if daily_change > 4:
            target_pct = 2.5
            stop_pct = 1.5
        elif daily_change > 2:
            target_pct = 3.5
            stop_pct = 2
        else:
            target_pct = 4.5
            stop_pct = 2.5
        
        target_price = price * (1 + target_pct / 100)
        stop_price = price * (1 - stop_pct / 100)
        
        if scalp_score >= 70:
            action = "HIZLI_AL"
            urgency = "🔥🔥🔥"
            confidence = "YÜKSEK"
        elif scalp_score >= 55:
            action = "AL"
            urgency = "🔥🔥"
            confidence = "ORTA"
        else:
            action = "TAKIP_ET"
            urgency = "🔥"
            confidence = "DÜŞÜK"
        
        return {
            'symbol': symbol,
            'price': price,
            'daily_change': daily_change,
            'volume': volume,
            'channel_position': round(channel_position, 1),
            'spread': round(spread, 3),
            'rsi': short_rsi,
            'momentum': momentum_data['direction'],
            'scalp_score': scalp_score,
            'action': action,
            'urgency': urgency,
            'confidence': confidence,
            'target_price': round(target_price, 6),
            'stop_price': round(stop_price, 6),
            'target_pct': target_pct,
            'stop_pct': stop_pct,
            'signals': signals,
            'warnings': warnings,
            'entry_time': datetime.now().strftime("%H:%M:%S"),
            'max_hold_time': 30
        }
    
    def scan_scalp_opportunities(self) -> List[Dict]:
        """Tüm coinleri tara ve scalp fırsatlarını bul"""
        tickers = self.get_btcturk_data()
        opportunities = []
        
        for ticker in tickers:
            opp = self.analyze_scalp_opportunity(ticker)
            if opp and opp['action'] in ['HIZLI_AL', 'AL']:
                opportunities.append(opp)
        
        opportunities.sort(key=lambda x: x['scalp_score'], reverse=True)
        
        self.last_scan_time = datetime.now()
        
        return opportunities[:5]
    
    def add_to_active(self, opportunity: Dict):
        """Fırsatı aktif pozisyonlara ekle"""
        if not any(s['symbol'] == opportunity['symbol'] for s in self.active_scalps):
            opportunity['entry_price'] = opportunity['price']
            self.active_scalps.append(opportunity)
            self.save_positions()
    
    def check_active_positions(self) -> Dict:
        """
        5 DAKİKADA BİR - Aktif pozisyonları kontrol et
        Hedef/Stop/Timeout kontrolü
        """
        if not self.active_scalps:
            return {'checked': 0, 'completed': [], 'active': []}
        
        tickers = self.get_btcturk_data()
        ticker_map = {}
        for t in tickers:
            pair = t.get('pairNormalized', '')
            if '_TRY' in pair:
                symbol = pair.split('_')[0]
                ticker_map[symbol] = {
                    'price': float(t.get('last', 0)),
                    'change': float(t.get('dailyPercent', 0))
                }
        
        completed = []
        still_active = []
        alerts = []
        
        now = datetime.now()
        
        for scalp in self.active_scalps:
            symbol = scalp['symbol']
            current_data = ticker_map.get(symbol, {})
            current_price = current_data.get('price', 0)
            
            if current_price == 0:
                still_active.append(scalp)
                continue
            
            entry_price = scalp.get('entry_price', scalp['price'])
            change_pct = ((current_price - entry_price) / entry_price) * 100
            
            try:
                entry_time = datetime.strptime(scalp['entry_time'], "%H:%M:%S")
                entry_datetime = datetime.combine(now.date(), entry_time.time())
                minutes_held = (now - entry_datetime).total_seconds() / 60
            except:
                minutes_held = 0
            
            result = None
            exit_reason = ""
            
            if current_price >= scalp['target_price']:
                result = 'WIN'
                exit_reason = f"🎯 HEDEF! +{change_pct:.2f}%"
            elif current_price <= scalp['stop_price']:
                result = 'LOSS'
                exit_reason = f"🛑 STOP! {change_pct:.2f}%"
            elif minutes_held >= scalp.get('max_hold_time', 30):
                result = 'TIMEOUT'
                exit_reason = f"⏰ 30 dk doldu: {change_pct:.2f}%"
            
            if result:
                scalp['result'] = result
                scalp['exit_price'] = current_price
                scalp['profit_pct'] = round(change_pct, 2)
                scalp['exit_time'] = now.strftime("%H:%M:%S")
                scalp['exit_reason'] = exit_reason
                scalp['minutes_held'] = round(minutes_held, 1)
                completed.append(scalp)
                self.completed_scalps.append(scalp)
                alerts.append(f"{symbol}: {exit_reason}")
            else:
                scalp['current_price'] = current_price
                scalp['current_change'] = round(change_pct, 2)
                scalp['minutes_held'] = round(minutes_held, 1)
                still_active.append(scalp)
                
                if minutes_held >= 20 and change_pct < 0:
                    alerts.append(f"⚠️ {symbol}: {minutes_held:.0f} dk, {change_pct:.1f}% - Çıkış düşün")
        
        self.active_scalps = still_active
        self.last_check_time = now
        self.save_positions()
        
        if alerts:
            self.send_position_alert(alerts, completed, still_active)
        
        return {
            'checked': len(self.active_scalps) + len(completed),
            'completed': completed,
            'active': still_active,
            'alerts': alerts
        }
    
    def send_position_alert(self, alerts: List[str], completed: List[Dict], active: List[Dict]):
        """Pozisyon güncellemesi gönder"""
        now = datetime.now()
        
        msg = f"""📊 <b>SCALP POZİSYON GÜNCELLEMESİ</b>
🕐 {now.strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        if completed:
            msg += "<b>✅ TAMAMLANAN:</b>\n"
            for c in completed:
                emoji = "🟢" if c['result'] == 'WIN' else "🔴"
                msg += f"{emoji} {c['symbol']}: {c['profit_pct']:+.2f}% ({c['result']})\n"
            msg += "\n"
        
        if active:
            msg += "<b>📈 AKTİF POZİSYONLAR:</b>\n"
            for a in active:
                change = a.get('current_change', 0)
                emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                msg += f"{emoji} {a['symbol']}: {change:+.2f}% | {a.get('minutes_held', 0):.0f} dk\n"
            msg += "\n"
        
        if alerts:
            msg += "<b>⚠️ UYARILAR:</b>\n"
            for alert in alerts:
                msg += f"• {alert}\n"
        
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'},
                timeout=10
            )
        except:
            pass
    
    def format_scalp_message(self, opportunities: List[Dict]) -> str:
        """Telegram için scalp mesajı oluştur"""
        now = datetime.now()
        
        next_scan = (now + timedelta(minutes=15)).strftime('%H:%M')
        next_check = (now + timedelta(minutes=5)).strftime('%H:%M')
        
        msg = f"""⚡ <b>HYBRİD SCALPING SİNYALLERİ</b>
🕐 {now.strftime('%H:%M:%S')}
📊 Sonraki tarama: {next_scan} | Kontrol: {next_check}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        if self.active_scalps:
            msg += f"📊 <b>AKTİF:</b> {len(self.active_scalps)} pozisyon\n\n"
        
        if not opportunities:
            msg += """❌ <b>ŞU AN UYGUN FIRSAT YOK</b>

Bekleme kriterleri:
• %1-6 arası yükseliş
• Kanal ortasında (25-65%)
• RSI 30-60 arası
• Yeterli hacim + Dar spread

⏳ 15 dakika sonra tekrar taranacak..."""
            return msg
        
        for i, opp in enumerate(opportunities, 1):
            score_bar = "🟢" * min(opp['scalp_score'] // 15, 5)
            
            msg += f"""{opp['urgency']} <b>#{i} {opp['symbol']}</b> [{opp['confidence']}]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>Fiyat:</b> ₺{opp['price']:,.6f}
📈 <b>Değişim:</b> +{opp['daily_change']:.1f}%
📊 <b>Skor:</b> {opp['scalp_score']}/100 {score_bar}

🎯 <b>HEDEF:</b> ₺{opp['target_price']:,.6f} (+{opp['target_pct']}%)
🛑 <b>STOP:</b> ₺{opp['stop_price']:,.6f} (-{opp['stop_pct']}%)

"""
            
            if opp['signals']:
                msg += "✅ " + " | ".join(opp['signals'][:3]) + "\n"
            
            if opp['warnings']:
                msg += "⚠️ " + " | ".join(opp['warnings'][:2]) + "\n"
            
            msg += f"📍 Kanal: %{opp['channel_position']} | RSI: {opp['rsi']:.0f}\n\n"
        
        msg += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>HYBRİD KURALLAR:</b>
• Sinyal tarama: Her 15 dk
• Pozisyon kontrolü: Her 5 dk
• Max tutma: 30 dk
• Hedef/Stop'a gel = HEMEN çık"""
        
        return msg
    
    def send_scalp_alert(self, opportunities: List[Dict] = None):
        """Scalp sinyallerini Telegram'a gönder"""
        if opportunities is None:
            opportunities = self.scan_scalp_opportunities()
        
        msg = self.format_scalp_message(opportunities)
        
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': msg,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            if resp.status_code == 200:
                logger.info(f"✅ Scalp sinyali gönderildi: {len(opportunities)} fırsat")
                
                for opp in opportunities:
                    if opp['action'] in ['HIZLI_AL', 'AL']:
                        self.add_to_active(opp)
                
                return True
            else:
                logger.error(f"Telegram error: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def run_scalp_scan(self):
        """15 DAKİKADA BİR - Scalp taraması çalıştır"""
        logger.info("⚡ Hybrid Scalping taraması başlıyor...")
        opportunities = self.scan_scalp_opportunities()
        logger.info(f"📊 {len(opportunities)} scalp fırsatı bulundu")
        self.send_scalp_alert(opportunities)
        return opportunities
    
    def run_position_check(self):
        """5 DAKİKADA BİR - Pozisyon kontrolü"""
        logger.info("📊 Pozisyon kontrolü...")
        result = self.check_active_positions()
        logger.info(f"✅ {result['checked']} pozisyon kontrol edildi, {len(result['completed'])} tamamlandı")
        return result
    
    def get_scalp_stats(self) -> Dict:
        """Scalping istatistikleri"""
        if not self.completed_scalps:
            return {
                'total': 0,
                'wins': 0,
                'losses': 0,
                'timeouts': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'total_profit': 0,
                'active_count': len(self.active_scalps)
            }
        
        wins = sum(1 for s in self.completed_scalps if s.get('result') == 'WIN')
        losses = sum(1 for s in self.completed_scalps if s.get('result') == 'LOSS')
        timeouts = sum(1 for s in self.completed_scalps if s.get('result') == 'TIMEOUT')
        
        total_profit = sum(s.get('profit_pct', 0) for s in self.completed_scalps)
        avg_profit = total_profit / len(self.completed_scalps)
        
        win_rate = (wins / len(self.completed_scalps)) * 100 if self.completed_scalps else 0
        
        return {
            'total': len(self.completed_scalps),
            'wins': wins,
            'losses': losses,
            'timeouts': timeouts,
            'win_rate': round(win_rate, 1),
            'avg_profit': round(avg_profit, 2),
            'total_profit': round(total_profit, 2),
            'active_count': len(self.active_scalps)
        }
    
    def format_stats_message(self) -> str:
        """İstatistik mesajı"""
        stats = self.get_scalp_stats()
        
        if stats['total'] == 0:
            return """📊 <b>SCALPING İSTATİSTİKLERİ</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Henüz tamamlanmış işlem yok.
Sistem sinyal üretiyor, bekleyin..."""
        
        win_emoji = "🟢" if stats['win_rate'] >= 50 else "🔴"
        profit_emoji = "📈" if stats['total_profit'] > 0 else "📉"
        
        msg = f"""📊 <b>SCALPING İSTATİSTİKLERİ</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>TOPLAM:</b> {stats['total']} işlem
{win_emoji} <b>BAŞARI:</b> %{stats['win_rate']}

✅ Kazanan: {stats['wins']}
❌ Kaybeden: {stats['losses']}
⏰ Timeout: {stats['timeouts']}

{profit_emoji} <b>TOPLAM KAR:</b> %{stats['total_profit']}
📊 <b>ORT. KAR:</b> %{stats['avg_profit']}

📌 <b>AKTİF:</b> {stats['active_count']} pozisyon"""
        
        return msg


scalping_system = ScalpingSystem()
