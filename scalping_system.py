"""
⚡ 15 DAKİKA SCALPING SİSTEMİ - KISA VADELİ AL-SAT
Hızlı giriş-çıkış, anlık momentum, %2-5 kar hedefi
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import time
import os

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

class ScalpingSystem:
    """
    15 Dakikalık Scalping Sistemi
    - Anlık momentum tespiti
    - Hızlı kar al-çık
    - Sıkı stop loss
    """
    
    def __init__(self):
        self.active_scalps = []
        self.completed_scalps = []
        self.last_scan_time = None
    
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
    
    def detect_volume_spike(self, volume: float, avg_volume: float) -> Dict:
        """Anlık hacim spike tespiti"""
        if avg_volume == 0:
            return {'spike': False, 'ratio': 0}
        
        ratio = volume / avg_volume
        
        if ratio > 3:
            spike_type = 'EXTREME'
            signal = '🔥 AŞIRI HACİM!'
        elif ratio > 2:
            spike_type = 'HIGH'
            signal = '📊 Yüksek hacim'
        elif ratio > 1.5:
            spike_type = 'MODERATE'
            signal = '📈 Hacim artışı'
        else:
            spike_type = 'NORMAL'
            signal = None
        
        return {
            'spike': ratio > 1.5,
            'ratio': round(ratio, 2),
            'type': spike_type,
            'signal': signal
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
        Scalping fırsatı analizi
        Kriterler:
        - Momentum yukarı
        - Hacim spike var
        - RSI 35-65 arası (aşırı alım/satım değil)
        - Kanal pozisyonu uygun
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
                scalp_score += 20
                signals.append(f"🚀 Momentum: {momentum_data['direction']}")
            elif momentum_data['direction'] in ['STRONG_DOWN', 'DOWN']:
                scalp_score -= 15
                warnings.append("📉 Negatif momentum")
            
            if 35 < short_rsi < 65:
                scalp_score += 15
                signals.append(f"✅ RSI: {short_rsi:.0f}")
            elif short_rsi > 75:
                scalp_score -= 20
                warnings.append(f"🔴 RSI aşırı alım: {short_rsi:.0f}")
            elif short_rsi < 25:
                scalp_score += 10
                signals.append(f"🟢 RSI düşük: {short_rsi:.0f}")
        
        if 1 < daily_change < 8:
            scalp_score += 20
            signals.append(f"📈 +{daily_change:.1f}%")
        elif daily_change >= 8:
            warnings.append("⚠️ Çok yükselmiş")
            scalp_score -= 15
        elif daily_change < 0:
            warnings.append("📉 Düşüşte")
            scalp_score -= 10
        
        if 30 < channel_position < 70:
            scalp_score += 15
            signals.append("🎯 Kanal OK")
        elif channel_position > 90:
            warnings.append("🔴 Zirve!")
            scalp_score -= 25
        elif channel_position < 20:
            scalp_score += 10
            signals.append("🟢 Dip")
        
        if volume > 500000:
            scalp_score += 10
            signals.append("💰 Hacim OK")
        elif volume < 100000:
            warnings.append("⚠️ Düşük hacim")
            scalp_score -= 10
        
        if spread < 0.3:
            scalp_score += 5
        elif spread > 0.5:
            scalp_score -= 5
        
        if scalp_score < 40:
            return None
        
        if daily_change > 5:
            target_pct = 2
            stop_pct = 1.5
        elif daily_change > 3:
            target_pct = 3
            stop_pct = 2
        else:
            target_pct = 4
            stop_pct = 2.5
        
        target_price = price * (1 + target_pct / 100)
        stop_price = price * (1 - stop_pct / 100)
        
        if scalp_score >= 60:
            action = "HIZLI_AL"
            urgency = "🔥🔥🔥"
        elif scalp_score >= 45:
            action = "AL"
            urgency = "🔥🔥"
        else:
            action = "TAKIP_ET"
            urgency = "🔥"
        
        return {
            'symbol': symbol,
            'price': price,
            'daily_change': daily_change,
            'volume': volume,
            'channel_position': round(channel_position, 1),
            'spread': round(spread, 3),
            'scalp_score': scalp_score,
            'action': action,
            'urgency': urgency,
            'target_price': round(target_price, 6),
            'stop_price': round(stop_price, 6),
            'target_pct': target_pct,
            'stop_pct': stop_pct,
            'signals': signals,
            'warnings': warnings,
            'timestamp': datetime.now().strftime("%H:%M:%S")
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
    
    def format_scalp_message(self, opportunities: List[Dict]) -> str:
        """Telegram için scalp mesajı oluştur"""
        now = datetime.now()
        
        msg = f"""⚡ <b>15 DAKİKA SCALPING SİNYALLERİ</b>
🕐 {now.strftime('%H:%M:%S')} | Sonraki: {(now + timedelta(minutes=15)).strftime('%H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        if not opportunities:
            msg += """❌ <b>ŞU AN UYGUN FIRSAT YOK</b>

Bekleme kriterleri:
• %1-8 arası yükseliş
• Kanal ortasında (30-70%)
• Yeterli hacim
• Dar spread

⏳ 15 dakika sonra tekrar taranacak..."""
            return msg
        
        for i, opp in enumerate(opportunities, 1):
            score_bar = "🟢" * min(opp['scalp_score'] // 15, 5)
            
            msg += f"""{opp['urgency']} <b>#{i} {opp['symbol']}</b>
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
            
            msg += f"📍 Kanal: %{opp['channel_position']} | Spread: %{opp['spread']}\n\n"
        
        msg += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>SCALPING KURALLARI:</b>
• Max 15 dk tut
• Hedef veya stop'a gelince HEMEN çık
• Günde max 5 işlem
• Sermayenin %5'ini riske at"""
        
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
                return True
            else:
                logger.error(f"Telegram error: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def run_scalp_scan(self):
        """Scalp taraması çalıştır ve sinyal gönder"""
        logger.info("⚡ Scalping taraması başlıyor...")
        opportunities = self.scan_scalp_opportunities()
        logger.info(f"📊 {len(opportunities)} scalp fırsatı bulundu")
        self.send_scalp_alert(opportunities)
        return opportunities
    
    def check_active_scalps(self) -> List[Dict]:
        """Aktif scalp pozisyonlarını kontrol et"""
        tickers = self.get_btcturk_data()
        ticker_map = {}
        for t in tickers:
            pair = t.get('pairNormalized', '')
            if '_TRY' in pair:
                symbol = pair.split('_')[0]
                ticker_map[symbol] = float(t.get('last', 0))
        
        completed = []
        still_active = []
        
        for scalp in self.active_scalps:
            symbol = scalp['symbol']
            current_price = ticker_map.get(symbol, 0)
            
            if current_price == 0:
                still_active.append(scalp)
                continue
            
            entry_price = scalp['entry_price']
            change_pct = ((current_price - entry_price) / entry_price) * 100
            
            result = None
            if current_price >= scalp['target_price']:
                result = 'WIN'
                scalp['exit_price'] = current_price
                scalp['profit_pct'] = round(change_pct, 2)
                scalp['exit_time'] = datetime.now().strftime("%H:%M:%S")
            elif current_price <= scalp['stop_price']:
                result = 'LOSS'
                scalp['exit_price'] = current_price
                scalp['profit_pct'] = round(change_pct, 2)
                scalp['exit_time'] = datetime.now().strftime("%H:%M:%S")
            
            entry_time = datetime.strptime(scalp['entry_time'], "%H:%M:%S")
            if datetime.now().time() > (datetime.combine(datetime.today(), entry_time.time()) + timedelta(minutes=15)).time():
                result = 'TIMEOUT'
                scalp['exit_price'] = current_price
                scalp['profit_pct'] = round(change_pct, 2)
                scalp['exit_time'] = datetime.now().strftime("%H:%M:%S")
            
            if result:
                scalp['result'] = result
                completed.append(scalp)
                self.completed_scalps.append(scalp)
            else:
                scalp['current_price'] = current_price
                scalp['current_change'] = round(change_pct, 2)
                still_active.append(scalp)
        
        self.active_scalps = still_active
        return completed
    
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
                'total_profit': 0
            }
        
        wins = sum(1 for s in self.completed_scalps if s['result'] == 'WIN')
        losses = sum(1 for s in self.completed_scalps if s['result'] == 'LOSS')
        timeouts = sum(1 for s in self.completed_scalps if s['result'] == 'TIMEOUT')
        
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
            'total_profit': round(total_profit, 2)
        }


scalping_system = ScalpingSystem()
