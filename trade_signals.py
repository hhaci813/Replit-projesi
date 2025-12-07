"""
OTOMATİK TRADE SİNYALLERİ
Giriş/çıkış noktaları ve sinyal üretimi
"""

import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

class TradeSignals:
    def __init__(self):
        self.signals_history = []
        self.active_signals = []
        
    def get_price_data(self, symbol: str, days: int = 30) -> Dict:
        """Fiyat verisi al"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            for t in resp.json().get('data', []):
                if t.get('pairNormalized') == f"{symbol}_TRY":
                    return {
                        'price': float(t.get('last', 0)),
                        'high': float(t.get('high', 0)),
                        'low': float(t.get('low', 0)),
                        'change': float(t.get('dailyPercent', 0)),
                        'volume': float(t.get('volume', 0))
                    }
            return None
        except:
            return None
    
    def get_historical_data(self, symbol: str, days: int = 30) -> List[float]:
        """Geçmiş fiyatları al"""
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
            if 'c' in data:
                return [float(x) for x in data['c']]
            return []
        except:
            return []
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI hesapla"""
        if len(prices) < period + 1:
            return 50
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """MACD hesapla"""
        if len(prices) < 26:
            return {'signal': 'NEUTRAL', 'histogram': 0}
        
        def ema(data, period):
            alpha = 2 / (period + 1)
            result = [data[0]]
            for price in data[1:]:
                result.append(alpha * price + (1 - alpha) * result[-1])
            return np.array(result)
        
        prices = np.array(prices)
        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd_line = ema12 - ema26
        signal_line = ema(macd_line, 9)
        histogram = macd_line[-1] - signal_line[-1]
        
        return {
            'signal': 'BULLISH' if histogram > 0 else 'BEARISH',
            'histogram': histogram,
            'macd': macd_line[-1],
            'signal_line': signal_line[-1]
        }
    
    def generate_signal(self, symbol: str) -> Optional[Dict]:
        """Trade sinyali üret"""
        try:
            current = self.get_price_data(symbol)
            if not current:
                return None
            
            prices = self.get_historical_data(symbol, 30)
            if len(prices) < 20:
                return None
            
            rsi = self.calculate_rsi(prices)
            macd = self.calculate_macd(prices)
            
            price = current['price']
            change = current['change']
            volume = current['volume']
            
            score = 50
            signals = []
            
            if rsi < 30:
                score += 25
                signals.append(f"RSI {rsi:.1f} - Aşırı satım")
            elif rsi > 70:
                score -= 25
                signals.append(f"RSI {rsi:.1f} - Aşırı alım")
            elif rsi < 40:
                score += 10
                signals.append(f"RSI {rsi:.1f} - Düşük")
            elif rsi > 60:
                score -= 10
                signals.append(f"RSI {rsi:.1f} - Yüksek")
            
            if macd['signal'] == 'BULLISH':
                score += 20
                signals.append("MACD Bullish")
            else:
                score -= 20
                signals.append("MACD Bearish")
            
            if -5 < change < 0:
                score += 15
                signals.append("Dip fırsatı")
            elif change > 5:
                score += 10
                signals.append("Momentum güçlü")
            
            ma7 = np.mean(prices[-7:])
            ma20 = np.mean(prices[-20:])
            
            if price > ma7 > ma20:
                score += 15
                signals.append("Golden cross")
            elif price < ma7 < ma20:
                score -= 15
                signals.append("Death cross")
            
            if score >= 75:
                action = 'STRONG_BUY'
                emoji = '🔥'
            elif score >= 60:
                action = 'BUY'
                emoji = '🟢'
            elif score <= 25:
                action = 'STRONG_SELL'
                emoji = '🔴'
            elif score <= 40:
                action = 'SELL'
                emoji = '🟠'
            else:
                action = 'HOLD'
                emoji = '⚪'
            
            entry = price
            if action in ['STRONG_BUY', 'BUY']:
                target1 = price * 1.10
                target2 = price * 1.20
                target3 = price * 1.30
                stop_loss = price * 0.95
            elif action in ['STRONG_SELL', 'SELL']:
                target1 = price * 0.95
                target2 = price * 0.90
                target3 = price * 0.85
                stop_loss = price * 1.05
            else:
                target1 = target2 = target3 = price
                stop_loss = price * 0.95
            
            risk_reward = abs(target1 - entry) / abs(entry - stop_loss) if stop_loss != entry else 0
            
            signal = {
                'symbol': symbol,
                'price': price,
                'action': action,
                'emoji': emoji,
                'score': score,
                'signals': signals,
                'entry': entry,
                'target1': target1,
                'target2': target2,
                'target3': target3,
                'stop_loss': stop_loss,
                'risk_reward': round(risk_reward, 2),
                'rsi': round(rsi, 1),
                'macd': macd['signal'],
                'timestamp': datetime.now().isoformat()
            }
            
            self.signals_history.append(signal)
            
            return signal
        except Exception as e:
            return None
    
    def scan_all_cryptos(self, limit: int = 20) -> List[Dict]:
        """Tüm kriptoları tara ve sinyaller üret"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=15)
            tickers = resp.json().get('data', [])
            
            signals = []
            seen = set()
            
            for t in tickers:
                pair = t.get('pairNormalized', '')
                if '_TRY' in pair:
                    symbol = pair.split('_')[0]
                    if symbol in seen:
                        continue
                    seen.add(symbol)
                    
                    signal = self.generate_signal(symbol)
                    if signal and signal['action'] in ['STRONG_BUY', 'BUY', 'STRONG_SELL', 'SELL']:
                        signals.append(signal)
                    
                    if len(signals) >= limit:
                        break
            
            return sorted(signals, key=lambda x: x['score'], reverse=True)
        except:
            return []
    
    def generate_report(self) -> str:
        """Telegram için sinyal raporu"""
        signals = self.scan_all_cryptos(10)
        
        msg = "📡 <b>TRADE SİNYALLERİ</b>\n\n"
        
        buy_signals = [s for s in signals if s['action'] in ['STRONG_BUY', 'BUY']]
        sell_signals = [s for s in signals if s['action'] in ['STRONG_SELL', 'SELL']]
        
        if buy_signals:
            msg += "🟢 <b>AL SİNYALLERİ:</b>\n"
            for s in buy_signals[:5]:
                msg += f"""
{s['emoji']} <b>{s['symbol']}</b> - {s['action']}
💰 Fiyat: ₺{s['price']:,.2f}
🎯 Hedef 1: ₺{s['target1']:,.2f} (+10%)
🎯 Hedef 2: ₺{s['target2']:,.2f} (+20%)
🛑 Stop: ₺{s['stop_loss']:,.2f}
📊 R/R: 1:{s['risk_reward']}
📈 RSI: {s['rsi']} | MACD: {s['macd']}

"""
        
        if sell_signals:
            msg += "\n🔴 <b>SAT SİNYALLERİ:</b>\n"
            for s in sell_signals[:3]:
                msg += f"""
{s['emoji']} <b>{s['symbol']}</b> - {s['action']}
💰 Fiyat: ₺{s['price']:,.2f}
📊 Skor: {s['score']}/100

"""
        
        if not buy_signals and not sell_signals:
            msg += "⚠️ Şu an güçlü sinyal yok\n"
        
        return msg
    
    def send_signal_alert(self, signal: Dict) -> bool:
        """Sinyal uyarısı gönder"""
        try:
            if signal['action'] not in ['STRONG_BUY', 'STRONG_SELL']:
                return False
            
            msg = f"""🚨 <b>YENİ SİNYAL!</b>

{signal['emoji']} <b>{signal['symbol']}</b>
📊 {signal['action']}
💰 Fiyat: ₺{signal['price']:,.2f}

🎯 Hedefler:
   1. ₺{signal['target1']:,.2f}
   2. ₺{signal['target2']:,.2f}
   3. ₺{signal['target3']:,.2f}

🛑 Stop Loss: ₺{signal['stop_loss']:,.2f}
📈 Risk/Reward: 1:{signal['risk_reward']}

⏰ {datetime.now().strftime('%H:%M')}
"""
            
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'},
                timeout=10
            )
            return resp.status_code == 200
        except:
            return False
