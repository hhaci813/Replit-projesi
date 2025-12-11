"""
Otomatik Grafik Analiz Sistemi
- BTCTurk'teki tüm coinleri tarar
- Yükselenleri ve yükselecekleri tespit eder
- Detaylı teknik analiz yapar (RSI, MACD, BB, Trend)
- Telegram'a otomatik rapor gönderir
"""

import os
import requests
import yfinance as yf
import numpy as np
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

class AutoChartAnalyzer:
    def __init__(self):
        self.last_analysis = None
        self.price_cache = {}
    
    def get_btcturk_all(self):
        """BTCTurk'ten tüm TRY çiftlerini al"""
        try:
            resp = requests.get('https://api.btcturk.com/api/v2/ticker', timeout=15)
            data = resp.json().get('data', [])
            
            coins = []
            for t in data:
                pair = t.get('pair', '')
                if pair.endswith('TRY') and not pair.startswith('USDT') and not pair.startswith('USDC'):
                    symbol = pair.replace('TRY', '')
                    coins.append({
                        'symbol': symbol,
                        'price': float(t.get('last', 0)),
                        'change': float(t.get('dailyPercent', 0)),
                        'volume': float(t.get('volume', 0)),
                        'high': float(t.get('high', 0)),
                        'low': float(t.get('low', 0))
                    })
            return coins
        except Exception as e:
            logger.error(f"BTCTurk error: {e}")
            return []
    
    def get_price_history(self, symbol, days=30):
        """YFinance'ten geçmiş fiyat al"""
        try:
            ticker = yf.Ticker(f"{symbol}-USD")
            hist = ticker.history(period=f"{days}d")
            return hist['Close'].tolist() if len(hist) > 0 else []
        except:
            return []
    
    def calculate_rsi(self, prices, period=14):
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
        return round(100 - (100 / (1 + rs)), 1)
    
    def calculate_macd(self, prices):
        if len(prices) < 26:
            return {'trend': 'NEUTRAL', 'histogram': 0, 'signal': 'HOLD'}
        prices = np.array(prices)
        def ema(data, period):
            alpha = 2 / (period + 1)
            result = [data[0]]
            for price in data[1:]:
                result.append(alpha * price + (1 - alpha) * result[-1])
            return np.array(result)
        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd = ema12 - ema26
        signal = ema(macd, 9)
        hist = macd[-1] - signal[-1]
        prev_hist = macd[-2] - signal[-2] if len(macd) > 1 else hist
        
        trend = 'BULLISH' if hist > 0 else 'BEARISH'
        if hist > 0 and prev_hist < 0:
            sig = 'BUY'
        elif hist < 0 and prev_hist > 0:
            sig = 'SELL'
        else:
            sig = 'HOLD'
        
        return {'trend': trend, 'histogram': round(hist, 4), 'signal': sig}
    
    def calculate_bollinger(self, prices, period=20):
        if len(prices) < period:
            return None
        recent = prices[-period:]
        middle = np.mean(recent)
        std = np.std(recent)
        upper = middle + (std * 2)
        lower = middle - (std * 2)
        current = prices[-1]
        position = ((current - lower) / (upper - lower) * 100) if (upper - lower) > 0 else 50
        
        if position < 20:
            signal = 'OVERSOLD'
        elif position > 80:
            signal = 'OVERBOUGHT'
        else:
            signal = 'NEUTRAL'
        
        return {'position': round(position, 1), 'signal': signal}
    
    def get_trend(self, prices):
        if len(prices) < 7:
            return 'YATAY'
        ma3 = np.mean(prices[-3:])
        ma7 = np.mean(prices[-7:])
        ma14 = np.mean(prices[-14:]) if len(prices) >= 14 else ma7
        
        if ma3 > ma7 > ma14:
            return 'GÜÇLÜ YÜKSELİŞ'
        elif ma3 > ma7:
            return 'YÜKSELİŞ'
        elif ma3 < ma7 < ma14:
            return 'GÜÇLÜ DÜŞÜŞ'
        elif ma3 < ma7:
            return 'DÜŞÜŞ'
        return 'YATAY'
    
    def analyze_coin(self, coin_data):
        """Tek coin için detaylı grafik analizi"""
        symbol = coin_data['symbol']
        
        prices = self.get_price_history(symbol)
        
        if len(prices) < 7:
            return None
        
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        bb = self.calculate_bollinger(prices)
        trend = self.get_trend(prices)
        
        score = 50
        signals = []
        
        if rsi < 30:
            score += 30
            signals.append(f"RSI {rsi} AŞIRI SATIM")
        elif rsi < 40:
            score += 15
            signals.append(f"RSI {rsi} alım bölgesi")
        elif rsi > 70:
            score -= 25
            signals.append(f"RSI {rsi} AŞIRI ALIM")
        elif rsi > 60:
            score -= 10
            signals.append(f"RSI {rsi} satım bölgesi")
        
        if macd['trend'] == 'BULLISH':
            score += 15
            if macd['signal'] == 'BUY':
                score += 10
                signals.append("MACD AL sinyali!")
        else:
            score -= 15
            if macd['signal'] == 'SELL':
                score -= 10
                signals.append("MACD SAT sinyali")
        
        if bb:
            if bb['signal'] == 'OVERSOLD':
                score += 20
                signals.append(f"BB dip ({bb['position']:.0f}%)")
            elif bb['signal'] == 'OVERBOUGHT':
                score -= 15
                signals.append(f"BB zirve ({bb['position']:.0f}%)")
        
        if 'GÜÇLÜ YÜKSELİŞ' in trend:
            score += 15
        elif 'YÜKSELİŞ' in trend:
            score += 10
        elif 'GÜÇLÜ DÜŞÜŞ' in trend:
            score -= 15
        elif 'DÜŞÜŞ' in trend:
            score -= 10
        
        change = coin_data['change']
        if change > 10:
            score += 10
        elif change > 5:
            score += 5
        elif change < -10:
            score -= 5
        
        if score >= 80:
            prediction = "🟢🟢 GÜÇLÜ YÜKSELECEK"
            action = "GÜÇLÜ AL"
        elif score >= 65:
            prediction = "🟢 YÜKSELECEK"
            action = "AL"
        elif score >= 50:
            prediction = "🟡 YATAY"
            action = "İZLE"
        elif score >= 35:
            prediction = "🔴 DÜŞECEK"
            action = "UZAK DUR"
        else:
            prediction = "🔴🔴 GÜÇLÜ DÜŞECEK"
            action = "SAT"
        
        return {
            'symbol': symbol,
            'price': coin_data['price'],
            'change': change,
            'volume': coin_data['volume'],
            'rsi': rsi,
            'macd': macd,
            'bb': bb,
            'trend': trend,
            'score': min(100, max(0, score)),
            'signals': signals,
            'prediction': prediction,
            'action': action
        }
    
    def run_full_analysis(self):
        """Tüm coinleri analiz et ve rapor gönder"""
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz).strftime('%d.%m.%Y %H:%M')
        
        logger.info("📊 Otomatik grafik analizi başlıyor...")
        
        coins = self.get_btcturk_all()
        if not coins:
            logger.error("Coin verisi alınamadı")
            return
        
        gainers = sorted(coins, key=lambda x: x['change'], reverse=True)[:15]
        
        high_volume = sorted(coins, key=lambda x: x['volume'] * x['price'], reverse=True)[:20]
        
        to_analyze = list({c['symbol'] for c in gainers + high_volume})[:25]
        
        results = []
        for symbol in to_analyze:
            coin_data = next((c for c in coins if c['symbol'] == symbol), None)
            if coin_data:
                analysis = self.analyze_coin(coin_data)
                if analysis:
                    results.append(analysis)
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        rising = [r for r in results if r['score'] >= 65]
        will_rise = [r for r in results if r['score'] >= 50 and r['change'] < 3]
        
        msg = f'''📊 <b>OTOMATİK GRAFİK ANALİZİ</b>
⏰ {now}

<b>🟢 YÜKSELENLER + YÜKSELECEKLER:</b>
'''
        
        for r in results[:8]:
            if r['score'] >= 65:
                emoji = "🟢"
            elif r['score'] >= 50:
                emoji = "🟡"
            else:
                emoji = "🔴"
            
            msg += f"\n{emoji} <b>{r['symbol']}</b> ₺{r['price']:,.2f} ({r['change']:+.1f}%)\n"
            msg += f"RSI:{r['rsi']:.0f} MACD:{r['macd']['trend'][:4]} Trend:{r['trend'][:6]}\n"
            msg += f"📊 Skor:{r['score']:.0f} → {r['prediction']}\n"
            
            if r['signals']:
                msg += f"💡 {r['signals'][0]}\n"
        
        msg += f"\n<b>📈 ÖZET:</b>\n"
        msg += f"✅ Yükseliş sinyali: {len([r for r in results if r['score'] >= 65])} coin\n"
        msg += f"🟡 İzlenmeli: {len([r for r in results if 50 <= r['score'] < 65])} coin\n"
        msg += f"❌ Uzak dur: {len([r for r in results if r['score'] < 50])} coin\n"
        
        if results:
            best = results[0]
            msg += f"\n🏆 <b>EN İYİ:</b> {best['symbol']} ({best['score']:.0f}/100)"
        
        msg += "\n\n🤖 Quantum Grafik Analiz"
        
        self.send_telegram(msg)
        logger.info(f"✅ Grafik analizi tamamlandı: {len(results)} coin")
        
        self.last_analysis = datetime.now()
        return results
    
    def send_telegram(self, message):
        """Telegram'a mesaj gönder"""
        if not BOT_TOKEN or not CHAT_ID:
            return False
        try:
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
            resp = requests.post(url, json={
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }, timeout=15)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False


auto_chart_analyzer = AutoChartAnalyzer()


if __name__ == "__main__":
    analyzer = AutoChartAnalyzer()
    analyzer.run_full_analysis()
