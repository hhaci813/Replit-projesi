"""
Otomatik Grafik Analiz Sistemi v2 - Pattern Detection Entegreli
- Mum formasyonu tespiti (Shooting Star, Hammer, Engulfing, Doji)
- Pump/Dump algılama
- Zirve/Dip mesafesi analizi
- Daha gerçekçi tahminler
"""

import os
import sys
import requests
import yfinance as yf
import numpy as np
from datetime import datetime
import pytz
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

try:
    from src.analysis.pattern_detector import PatternDetector, ohlcv_from_yfinance
    pattern_detector = PatternDetector()
except:
    pattern_detector = None
    logger.warning("Pattern detector yüklenemedi")

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
    
    def get_ohlcv_history(self, symbol, days=30):
        """YFinance'ten OHLCV verisi al"""
        try:
            ticker = yf.Ticker(f"{symbol}-USD")
            hist = ticker.history(period=f"{days}d")
            if len(hist) > 0:
                ohlcv = []
                for idx, row in hist.iterrows():
                    ohlcv.append({
                        'open': row['Open'],
                        'high': row['High'],
                        'low': row['Low'],
                        'close': row['Close'],
                        'volume': row.get('Volume', 0),
                        'date': idx
                    })
                return ohlcv
            return []
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
    
    def detect_pump_dump_simple(self, prices, high_24h, current):
        """Basit pump/dump tespiti"""
        if len(prices) < 5:
            return None
        
        recent_high = max(prices[-24:]) if len(prices) >= 24 else max(prices)
        drawdown = (recent_high - current) / recent_high * 100 if recent_high > 0 else 0
        
        avg_price = np.mean(prices[-7:])
        spike = (recent_high - avg_price) / avg_price * 100 if avg_price > 0 else 0
        
        result = {
            'is_post_pump': False,
            'drawdown': drawdown,
            'spike': spike,
            'signal': 'NEUTRAL'
        }
        
        if drawdown > 10 and spike > 15:
            result['is_post_pump'] = True
            result['signal'] = 'POST_PUMP_DUMP'
        elif drawdown > 15:
            result['is_post_pump'] = True  
            result['signal'] = 'DOWNTREND'
        
        return result
    
    def analyze_coin(self, coin_data):
        """Tek coin için detaylı grafik analizi - Pattern Detection dahil"""
        symbol = coin_data['symbol']
        
        ohlcv = self.get_ohlcv_history(symbol)
        
        if len(ohlcv) < 7:
            return None
        
        prices = [c['close'] for c in ohlcv]
        volumes = [c['volume'] for c in ohlcv]
        
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        bb = self.calculate_bollinger(prices)
        trend = self.get_trend(prices)
        
        pattern_result = None
        if pattern_detector:
            try:
                pattern_result = pattern_detector.analyze_full(ohlcv, volumes)
            except:
                pass
        
        pump_check = self.detect_pump_dump_simple(prices, coin_data['high'], coin_data['price'])
        
        score = 50
        signals = []
        
        if rsi < 30:
            score += 25
            signals.append(f"RSI {rsi:.0f} AŞIRI SATIM")
        elif rsi < 40:
            score += 10
            signals.append(f"RSI {rsi:.0f} alım bölgesi")
        elif rsi > 70:
            score -= 20
            signals.append(f"RSI {rsi:.0f} AŞIRI ALIM")
        elif rsi > 60:
            score -= 10
            signals.append(f"RSI {rsi:.0f} satım bölgesi")
        
        if macd['trend'] == 'BULLISH':
            score += 10
            if macd['signal'] == 'BUY':
                score += 10
                signals.append("MACD AL sinyali")
        else:
            score -= 10
            if macd['signal'] == 'SELL':
                score -= 10
                signals.append("MACD SAT sinyali")
        
        if bb:
            if bb['signal'] == 'OVERSOLD':
                score += 15
                signals.append(f"BB dip ({bb['position']:.0f}%)")
            elif bb['signal'] == 'OVERBOUGHT':
                score -= 15
                signals.append(f"BB zirve ({bb['position']:.0f}%)")
        
        if 'GÜÇLÜ YÜKSELİŞ' in trend:
            score += 10
        elif 'YÜKSELİŞ' in trend:
            score += 5
        elif 'GÜÇLÜ DÜŞÜŞ' in trend:
            score -= 15
            signals.append("📉 Güçlü düşüş trendi")
        elif 'DÜŞÜŞ' in trend:
            score -= 10
            signals.append("📉 Düşüş trendi")
        
        if pattern_result:
            pattern_score = pattern_result.get('pattern_score', 0)
            score += pattern_score // 2
            
            if pattern_result.get('signals'):
                signals.extend(pattern_result['signals'][:2])
            
            if pattern_result.get('candlestick_patterns'):
                for p in pattern_result['candlestick_patterns'][-2:]:
                    if p['signal'] == 'BEARISH' and p['strength'] == 'STRONG':
                        score -= 15
                        signals.append(f"🕯️ {p['type']}")
        
        if pump_check:
            if pump_check['signal'] == 'POST_PUMP_DUMP':
                score -= 30
                signals.append(f"⚠️ PUMP SONRASI %{pump_check['drawdown']:.1f} düşüş")
            elif pump_check['signal'] == 'DOWNTREND':
                score -= 20
                signals.append(f"⚠️ Zirveden %{pump_check['drawdown']:.1f} aşağıda")
        
        change = coin_data['change']
        if change > 20:
            score -= 10
            signals.append(f"⚠️ %{change:.0f} artış - dikkat")
        elif change > 10:
            pass
        elif change < -15:
            score -= 5
        
        score = min(100, max(0, score))
        
        if score >= 75:
            prediction = "🟢🟢 GÜÇLÜ YÜKSELECEK"
            action = "GÜÇLÜ AL"
        elif score >= 60:
            prediction = "🟢 YÜKSELECEK"
            action = "AL"
        elif score >= 45:
            prediction = "🟡 YATAY/BELİRSİZ"
            action = "İZLE"
        elif score >= 30:
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
            'score': score,
            'signals': signals,
            'prediction': prediction,
            'action': action,
            'pattern_result': pattern_result,
            'pump_check': pump_check
        }
    
    def run_full_analysis(self):
        """Tüm coinleri analiz et ve rapor gönder"""
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz).strftime('%d.%m.%Y %H:%M')
        
        logger.info("📊 Otomatik grafik analizi başlıyor (Pattern Detection aktif)...")
        
        coins = self.get_btcturk_all()
        if not coins:
            logger.error("Coin verisi alınamadı")
            return []
        
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
        
        bullish = [r for r in results if r['score'] >= 60]
        bearish = [r for r in results if r['score'] < 40]
        neutral = [r for r in results if 40 <= r['score'] < 60]
        
        msg = f'''📊 <b>GRAFİK ANALİZ RAPORU</b>
⏰ {now}
🔬 Pattern Detection + Pump/Dump Algılama

'''
        
        if bullish:
            msg += "<b>🟢 YÜKSELİŞ SİNYALİ:</b>\n"
            for r in bullish[:4]:
                msg += f"• <b>{r['symbol']}</b> ₺{r['price']:,.2f} ({r['change']:+.1f}%)\n"
                msg += f"  Skor:{r['score']:.0f} RSI:{r['rsi']:.0f} {r['prediction']}\n"
                if r['signals']:
                    msg += f"  💡 {r['signals'][0]}\n"
        
        if bearish:
            msg += "\n<b>🔴 DÜŞÜŞ SİNYALİ (UZAK DUR):</b>\n"
            for r in bearish[:4]:
                msg += f"• <b>{r['symbol']}</b> ₺{r['price']:,.2f} ({r['change']:+.1f}%)\n"
                msg += f"  Skor:{r['score']:.0f} {r['prediction']}\n"
                if r['signals']:
                    for sig in r['signals'][:2]:
                        if '⚠️' in sig or '📉' in sig or '🔴' in sig:
                            msg += f"  {sig}\n"
                            break
        
        if neutral:
            msg += "\n<b>🟡 BELİRSİZ (İZLE):</b>\n"
            for r in neutral[:3]:
                msg += f"• {r['symbol']} ₺{r['price']:,.2f} Skor:{r['score']:.0f}\n"
        
        msg += f"\n<b>📈 ÖZET:</b>\n"
        msg += f"🟢 Yükseliş: {len(bullish)} | 🟡 Belirsiz: {len(neutral)} | 🔴 Düşüş: {len(bearish)}\n"
        
        if results:
            best = max(results, key=lambda x: x['score'])
            worst = min(results, key=lambda x: x['score'])
            msg += f"\n🏆 En İyi: {best['symbol']} ({best['score']:.0f})"
            msg += f"\n⚠️ En Riskli: {worst['symbol']} ({worst['score']:.0f})"
        
        msg += "\n\n🤖 Quantum Pattern Analiz v2"
        
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
