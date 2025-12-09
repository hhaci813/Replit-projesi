"""🚀 AKILLI YATIRIM ASİSTANI - MAX VERSİYON
Tüm özellikler entegre + ML Advanced + Alarm + Portföy + Whale + AI Haberci
"""
import os
import requests
import yfinance as yf
import numpy as np
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import threading
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

app = Flask(__name__)
CORS(app)

# ===================== MODÜL IMPORTS =====================
try:
    from price_alerts import PriceAlertSystem
    alert_system = PriceAlertSystem()
except:
    alert_system = None

try:
    from portfolio_tracker import PortfolioTracker
    portfolio = PortfolioTracker()
except:
    portfolio = None

try:
    from advanced_whale_tracker import AdvancedWhaleTracker
    whale_tracker = AdvancedWhaleTracker()
except:
    whale_tracker = None

try:
    from backtesting_engine import BacktestingEngine
    backtest = BacktestingEngine()
except:
    backtest = None

try:
    from ai_news_analyzer import AINewsAnalyzer
    news_analyzer = AINewsAnalyzer()
except:
    news_analyzer = None

try:
    from ml_advanced import MLAdvancedPredictor
    ml_predictor = MLAdvancedPredictor()
except:
    ml_predictor = None

try:
    from detailed_analyzer import DetailedAnalyzer
    detailed = DetailedAnalyzer()
except:
    detailed = None

try:
    from advanced_indicators import AdvancedIndicators
    indicators = AdvancedIndicators()
except:
    indicators = None

try:
    from market_sentiment import MarketSentiment
    market_sent = MarketSentiment()
except:
    market_sent = None

try:
    from social_sentiment import SocialSentiment
    social_sent = SocialSentiment()
except:
    social_sent = None

try:
    from chart_generator import ChartGenerator
    chart_gen = ChartGenerator()
except:
    chart_gen = None

try:
    from trade_signals import TradeSignals
    trade_sig = TradeSignals()
except:
    trade_sig = None

try:
    from watchlist import Watchlist
    watchlist = Watchlist()
except:
    watchlist = None

try:
    from risk_profile import RiskProfile
    risk_prof = RiskProfile()
except:
    risk_prof = None

try:
    from trade_history import TradeHistory
    trade_hist = TradeHistory()
except:
    trade_hist = None

try:
    from pro_analysis import ProAnalysis
    pro_analyzer = ProAnalysis()
except:
    pro_analyzer = None

try:
    from signal_tracker import SignalTracker, signal_tracker
except:
    signal_tracker = None

try:
    from sniper_system import SniperSystem, sniper
except:
    sniper = None

try:
    from historical_analyzer import HistoricalPatternAnalyzer, historical_analyzer
except:
    historical_analyzer = None

# ===================== TEKNIK ANALİZ =====================
def calculate_rsi(prices, period=14):
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

def calculate_macd(prices):
    if len(prices) < 26:
        return {'trend': 'NEUTRAL', 'histogram': 0}
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
    trend = 'BULLISH' if hist > 0 else 'BEARISH'
    return {'trend': trend, 'histogram': round(hist, 4)}

def calculate_bollinger(prices, period=20):
    if len(prices) < period:
        return None
    recent = prices[-period:]
    middle = np.mean(recent)
    std = np.std(recent)
    upper = middle + (std * 2)
    lower = middle - (std * 2)
    current = prices[-1]
    position = (current - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
    return {'upper': upper, 'middle': middle, 'lower': lower, 'position': position * 100}

# ===================== VERİ KAYNAKLARI =====================
def get_btcturk_data():
    try:
        resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=15)
        return resp.json().get('data', [])
    except:
        return []

def get_crypto_history(symbol, days=30):
    try:
        ticker = yf.Ticker(f"{symbol}-USD")
        hist = ticker.history(period=f"{days}d")
        return hist['Close'].tolist() if len(hist) > 0 else []
    except:
        return []

# ===================== DETAYLI ANALİZ =====================
def analyze_crypto_detailed(symbol):
    """Tek kripto için detaylı analiz (TL)"""
    try:
        tickers = get_btcturk_data()
        for t in tickers:
            if t.get('pairNormalized') == f"{symbol}_TRY":
                price = float(t.get('last', 0))
                high = float(t.get('high', 0))
                low = float(t.get('low', 0))
                change = float(t.get('dailyPercent', 0))
                volume = float(t.get('volume', 0))
                
                prices = get_crypto_history(symbol, 30)
                rsi = calculate_rsi(prices) if prices else 50
                macd = calculate_macd(prices) if prices else {'trend': 'NEUTRAL'}
                bb = calculate_bollinger(prices) if prices else None
                
                signals = []
                score = 50
                
                if rsi < 30:
                    signals.append(f"🟢 RSI {rsi} - Aşırı satım")
                    score += 20
                elif rsi > 70:
                    signals.append(f"🔴 RSI {rsi} - Aşırı alım")
                    score -= 20
                else:
                    signals.append(f"⚪ RSI {rsi}")
                
                if macd['trend'] == 'BULLISH':
                    signals.append("🟢 MACD Yükseliş")
                    score += 15
                else:
                    signals.append("🔴 MACD Düşüş")
                    score -= 15
                
                if bb:
                    if bb['position'] < 20:
                        signals.append("🟢 BB Alt bant")
                        score += 15
                    elif bb['position'] > 80:
                        signals.append("🔴 BB Üst bant")
                        score -= 15
                
                if score >= 70:
                    rec = "STRONG_BUY"
                elif score >= 55:
                    rec = "BUY"
                elif score <= 30:
                    rec = "STRONG_SELL"
                elif score <= 45:
                    rec = "SELL"
                else:
                    rec = "HOLD"
                
                target = price * 1.15 if rec in ['STRONG_BUY', 'BUY'] else price
                stop = price * 0.92
                
                return {
                    'symbol': symbol, 'price': price, 'change': change,
                    'high': high, 'low': low, 'volume': volume,
                    'rsi': rsi, 'macd': macd['trend'],
                    'bb_position': bb['position'] if bb else 50,
                    'signals': signals, 'score': score, 
                    'recommendation': rec, 'target': target, 'stop': stop
                }
        return None
    except Exception as e:
        return None

def analyze_rising_cryptos(tickers):
    """Yükselen kriptolar (TL) - Akıllı risk filtresi ile"""
    cryptos = []
    seen = set()
    for t in tickers:
        if isinstance(t, dict):
            pair = t.get('pairNormalized', '')
            if '_TRY' in pair:
                symbol = pair.split('_')[0]
                change = float(t.get('dailyPercent', 0))
                price = float(t.get('last', 0))
                volume = float(t.get('volume', 0))
                if price > 0 and change > 5:
                    momentum = 100 if change > 15 else (80 if change > 10 else 60)
                    if volume > 1000000: momentum += 10
                    
                    # YENİ: Yüksek değişim riski filtresi
                    if change > 30:
                        risk_level = "YUKSEK_RISK"
                        warning = "⚠️ ÇOK YÜKSEK - Kar satışı gelebilir!"
                        rec = "DIKKATLI_AL"
                    elif change > 20:
                        risk_level = "ORTA_RISK"
                        warning = "⚡ Hızlı yükseliş - Stop-loss şart!"
                        rec = "DIKKATLI_AL"
                    elif change > 15:
                        risk_level = "NORMAL"
                        warning = "📈 Momentum güçlü"
                        rec = 'STRONG_BUY' if momentum >= 80 else 'BUY'
                    else:
                        risk_level = "GUVENLI"
                        warning = "✅ Güvenli giriş bölgesi"
                        rec = 'STRONG_BUY' if momentum >= 80 else 'BUY'
                    
                    cryptos.append({
                        'symbol': symbol, 'change': change, 'price': price,
                        'momentum': momentum, 'rec': rec,
                        'risk_level': risk_level, 'warning': warning,
                        'target': price * (1 + min(change + 25, 100) / 100),
                        'stop': price * 0.92
                    })
    return sorted(cryptos, key=lambda x: x['change'], reverse=True)[:10]

def analyze_potential_risers(tickers):
    """Yükselecek kriptolar (TL)"""
    potentials = []
    seen = set()
    for t in tickers:
        if not isinstance(t, dict):
            continue
        pair = t.get('pairNormalized', '')
        if '_TRY' not in pair:
            continue
        
        symbol = pair.split('_')[0]
        price = float(t.get('last', 0))
        change = float(t.get('dailyPercent', 0))
        volume = float(t.get('volume', 0))
        high = float(t.get('high', 0))
        low = float(t.get('low', 0))
        
        if price <= 0 or change > 5:
            continue
        
        score = 0
        signals = []
        
        if -3 < change < 3 and volume > 100000:
            score += 25
            signals.append("📦 Birikim")
        
        if -10 < change < 0 and volume > 50000:
            score += 20
            signals.append("📉 Dip")
        
        if high > 0 and low > 0 and high != low:
            price_pos = (price - low) / (high - low)
            if price_pos < 0.3:
                score += 30
                signals.append("🎯 Breakout")
        
        if volume > 500000 and abs(change) < 5:
            score += 20
            signals.append("📊 Hacim")
        
        if change < -5:
            score += 15
            signals.append("📈 Oversold")
        
        if score >= 40 and signals:
            potential_gain = ((high - price) / price * 100) if high > price else 20
            potentials.append({
                'symbol': symbol, 'price': price, 'change': change,
                'volume': volume, 'score': score, 'signals': signals,
                'potential': round(min(potential_gain, 50), 1),
                'risk': 4 if volume > 100000 else 6,
                'target': price * 1.25,
                'stop': price * 0.92,
                'days_estimate': '3-7 gün'
            })
    
    return sorted(potentials, key=lambda x: x['score'], reverse=True)[:10]

def get_global_market_sentiment():
    try:
        indices = {'^GSPC': 'S&P 500', '^DJI': 'Dow Jones', '^IXIC': 'NASDAQ'}
        results = {}
        positive = 0
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='2d')
                if len(hist) >= 2:
                    change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                    results[name] = round(change, 2)
                    if change > 0:
                        positive += 1
            except:
                pass
        
        if positive >= 2:
            sentiment = 'RISK_ON'
            crypto_impact = 'BULLISH'
        elif positive == 0:
            sentiment = 'RISK_OFF'
            crypto_impact = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
            crypto_impact = 'NEUTRAL'
        
        return {'sentiment': sentiment, 'crypto_impact': crypto_impact, 'indices': results}
    except:
        return {'sentiment': 'UNKNOWN', 'crypto_impact': 'NEUTRAL', 'indices': {}}

def get_btc_technical_analysis():
    try:
        prices = get_crypto_history('BTC', 30)
        if len(prices) < 20:
            return None
        
        rsi = calculate_rsi(prices)
        macd = calculate_macd(prices)
        bb = calculate_bollinger(prices)
        
        score = 50
        signals = []
        
        if rsi < 30:
            score += 25
            signals.append(f"RSI {rsi} - Aşırı satım")
        elif rsi > 70:
            score -= 25
            signals.append(f"RSI {rsi} - Aşırı alım")
        else:
            signals.append(f"RSI {rsi} - Normal")
        
        if macd['trend'] == 'BULLISH':
            score += 20
            signals.append("MACD Yükseliş")
        else:
            score -= 20
            signals.append("MACD Düşüş")
        
        if prices[-1] > np.mean(prices[-7:]):
            score += 10
            signals.append("7g MA üzerinde")
        
        rec = 'STRONG_BUY' if score >= 75 else ('BUY' if score >= 55 else ('HOLD' if score >= 45 else 'SELL'))
        
        return {'rsi': rsi, 'macd': macd['trend'], 'score': score, 'signals': signals, 'recommendation': rec, 'price': round(prices[-1], 2)}
    except:
        return None

def get_stock_data():
    stocks_list = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'ADBE', 'CRM', 'AMD', 'NFLX']
    stocks = []
    for sym in stocks_list:
        try:
            hist = yf.Ticker(sym).history(period="30d")
            if len(hist) >= 5:
                current = hist['Close'].iloc[-1]
                prev_week = hist['Close'].iloc[-5]
                weekly = ((current - prev_week) / prev_week * 100) if prev_week > 0 else 0
                momentum = 90 if weekly > 10 else (70 if weekly > 5 else 50 if weekly > 2 else 30)
                rec = "STRONG_BUY" if momentum >= 80 else ("BUY" if momentum >= 50 else "HOLD")
                stocks.append({'symbol': sym, 'price': round(current,2), 'weekly': round(weekly,2), 'rec': rec, 'target': current * 1.15, 'stop': current * 0.95})
        except:
            pass
    return sorted(stocks, key=lambda x: x['weekly'], reverse=True)

# ===================== TELEGRAM =====================
def send_telegram(msg):
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'},
            timeout=10
        )
        return resp.status_code == 200
    except:
        return False

def send_telegram_to(chat_id, msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML'},
            timeout=10
        )
    except:
        pass

def get_usd_try_rate():
    """USD/TRY kurunu al"""
    try:
        resp = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        if resp.status_code == 200:
            return resp.json().get('rates', {}).get('TRY', 34.5)
    except:
        pass
    return 34.5

def run_full_analysis():
    logger.info("🔄 ULTRA Tam analiz başlıyor...")
    
    tickers = get_btcturk_data()
    rising = analyze_rising_cryptos(tickers)
    potential = analyze_potential_risers(tickers)
    stocks = get_stock_data()
    strong_stocks = [s for s in stocks if s['rec'] == 'STRONG_BUY'][:3]
    btc_analysis = get_btc_technical_analysis()
    global_sentiment = get_global_market_sentiment()
    
    # USD/TRY kuru
    usd_try = get_usd_try_rate()
    
    logger.info(f"📊 {len(tickers)} kripto analiz edildi | USD/TRY: {usd_try:.2f}")
    
    # Alarm kontrolü
    if alert_system:
        alert_system.check_alerts()
    
    # Backtest güncelleme
    if backtest:
        backtest.check_recommendations()
    
    now = datetime.now()
    
    # ==================== MESAJ 1: ANA RAPOR ====================
    msg1 = f"""🔔 <b>AKILLI YATIRIM RAPORU - ULTRA</b>
📅 {now.strftime('%d.%m.%Y %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # BTC TL fiyatını al
    btc_tl = None
    for t in tickers:
        if t.get('pairNormalized') == 'BTC_TRY':
            btc_tl = float(t.get('last', 0))
            break
    
    # PRO Analiz - Top 5 Coin (Açıklayıcı)
    if pro_analyzer:
        msg1 += "\n🔥 <b>PRO ANALİZ - EN İYİ 5</b>\n"
        msg1 += "<i>Skor 7+: AL | 5-7: TUT | 5-: SAT</i>\n\n"
        top_coins = ['BTC', 'ETH', 'SOL', 'XRP', 'AVAX']
        pro_results = []
        for coin in top_coins:
            try:
                analysis = pro_analyzer.full_pro_analysis(coin)
                if analysis:
                    pro_results.append(analysis)
                    price = analysis.get('price', 0)
                    pro_score = analysis['pro_score']
                    rsi_val = analysis['rsi']['value']
                    
                    # Aksiyon belirleme
                    if pro_score >= 8:
                        action = "🟢 GÜÇLÜ AL"
                        stop_pct = 5
                        target_pct = 15
                    elif pro_score >= 7:
                        action = "🟢 AL"
                        stop_pct = 6
                        target_pct = 12
                    elif pro_score >= 5:
                        action = "🟡 BEKLE"
                        stop_pct = 0
                        target_pct = 0
                    else:
                        action = "🔴 UZAK DUR"
                        stop_pct = 0
                        target_pct = 0
                    
                    msg1 += f"<b>{coin}</b> {analysis['price_formatted']}\n"
                    msg1 += f"   📊 Skor: <b>{pro_score}/10</b> → {action}\n"
                    
                    # RSI açıklaması
                    if rsi_val < 30:
                        rsi_text = "Aşırı satım (ucuz)"
                    elif rsi_val > 70:
                        rsi_text = "Aşırı alım (pahalı)"
                    else:
                        rsi_text = "Normal"
                    msg1 += f"   📈 RSI {rsi_val:.0f}: {rsi_text}\n"
                    
                    # Stop ve hedef (sadece AL sinyali için)
                    if pro_score >= 7 and price > 0:
                        stop = price * (1 - stop_pct/100)
                        target = price * (1 + target_pct/100)
                        msg1 += f"   🎯 Hedef: ₺{target:,.0f} (+%{target_pct})\n"
                        msg1 += f"   🛑 Stop: ₺{stop:,.0f} (-%{stop_pct})\n"
                    
                    msg1 += "\n"
            except Exception as e:
                logger.error(f"PRO {coin} hatası: {e}")
        
        # Fear & Greed Index
        try:
            fg = pro_analyzer.get_fear_greed_index()
            msg1 += f"\n{fg['emoji']} <b>Fear & Greed:</b> {fg['value']} - {fg['classification']}\n"
        except:
            pass
        
        msg1 += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if btc_analysis:
        msg1 += f"""
📊 <b>BTC TEKNİK ANALİZ</b>
   💰 Fiyat: ₺{btc_tl:,.0f} TL
   📈 RSI: {btc_analysis['rsi']}
   📉 MACD: {btc_analysis['macd']}
   🎯 Skor: {btc_analysis['score']}/100
   ✅ {btc_analysis['recommendation']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    msg1 += f"""
🌍 <b>GLOBAL PİYASA</b>
   {global_sentiment['sentiment']} | {global_sentiment['crypto_impact']}
"""
    for name, change in global_sentiment.get('indices', {}).items():
        msg1 += f"   {'📈' if change > 0 else '📉'} {name}: {'+' if change > 0 else ''}{change}%\n"
    
    send_telegram(msg1)
    time.sleep(1)
    
    # ==================== MESAJ 2: PUMP & FIRSATLAR ====================
    msg2 = """🚀 <b>PUMP TESPİT & FIRSATLAR</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Pump Detection
    if pro_analyzer:
        msg2 += "\n⚡ <b>HACİM PATLAMASI:</b>\n"
        pump_count = 0
        for t in tickers[:50]:
            try:
                symbol = t.get('pairNormalized', '').replace('_TRY', '')
                volume = float(t.get('volume', 0))
                change = float(t.get('dailyPercent', 0))
                avg_volume = volume * 0.7
                
                spike = pro_analyzer.detect_volume_spike(volume, avg_volume, change)
                if spike.get('spike') and change > 0:
                    pump_count += 1
                    price_tl = float(t.get('last', 0))
                    price_usd = price_tl / usd_try if usd_try > 0 else 0
                    msg2 += f"🔥 <b>{symbol}</b> ₺{price_tl:,.4f} | ${price_usd:,.4f}\n"
                    msg2 += f"   {spike['text']} | +{change:.1f}%\n"
                    if pump_count >= 5:
                        break
            except:
                pass
        
        if pump_count == 0:
            msg2 += "   ⚪ Şu an pump tespit edilmedi\n"
    
    msg2 += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔥 <b>YÜKSELENLER:</b>\n"
    if rising:
        for c in rising[:5]:
            price_tl = c.get('price', 0)
            price_usd = price_tl / usd_try if usd_try > 0 else 0
            risk_level = c.get('risk_level', 'NORMAL')
            warning = c.get('warning', '')
            change = c.get('change', 0)
            
            # Hedef ve stop hesapla
            target_price = price_tl * 1.10  # %10 hedef
            stop_price = price_tl * 0.92   # %8 stop
            
            # Risk seviyesine göre emoji
            if risk_level == "YUKSEK_RISK":
                emoji = "🔴"
            elif risk_level == "ORTA_RISK":
                emoji = "🟡"
            elif risk_level == "GUVENLI":
                emoji = "🟢"
            else:
                emoji = "🔵"
            
            msg2 += f"{emoji} <b>{c['symbol']}</b> +{change:.1f}%\n"
            msg2 += f"   ₺{price_tl:,.4f} | ${price_usd:,.4f}\n"
            msg2 += f"   {warning}\n"
            msg2 += f"   🎯 Hedef: ₺{target_price:,.4f} | 🛑 Stop: ₺{stop_price:,.4f}\n"
    else:
        msg2 += "⚠️ Yok\n"
    
    msg2 += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔮 <b>YÜKSELECEKLER (TAHMİN):</b>\n"
    if potential:
        for p in potential[:5]:
            price_tl = p['price']
            price_usd = price_tl / usd_try if usd_try > 0 else 0
            pot = p.get('potential', 0)
            risk = p.get('risk', 5)
            
            # Hedef ve stop hesapla
            target_price = price_tl * (1 + pot/100)
            stop_price = price_tl * 0.92  # %8 stop
            
            # Risk seviyesine göre emoji ve açıklama
            if risk <= 3:
                emoji = "🟢"
                risk_text = "Güvenli giriş bölgesi"
            elif risk <= 5:
                emoji = "🟡"
                risk_text = "Dikkatli al"
            elif risk <= 7:
                emoji = "🟠"
                risk_text = "Yüksek risk - Az miktarda"
            else:
                emoji = "🔴"
                risk_text = "ÇOK YÜKSEK - Tavsiye edilmez"
            
            msg2 += f"{emoji} <b>{p['symbol']}</b> +{pot}%\n"
            msg2 += f"   ₺{price_tl:,.4f} | ${price_usd:,.4f}\n"
            msg2 += f"   {risk_text}\n"
            msg2 += f"   🎯 Hedef: ₺{target_price:,.4f} | 🛑 Stop: ₺{stop_price:,.4f}\n"
    else:
        msg2 += "⚠️ Sinyal yok\n"
    
    send_telegram(msg2)
    time.sleep(1)
    
    # ==================== MESAJ 3: WHALE & SOSYAL ====================
    msg3 = """🐋 <b>WHALE & SOSYAL ANALİZ</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Whale Activity
    if whale_tracker:
        try:
            whale_data = whale_tracker.get_whale_summary()
            if whale_data:
                msg3 += "\n🐋 <b>BALİNA HAREKETLERİ:</b>\n"
                for w in whale_data.get('recent', [])[:3]:
                    msg3 += f"   {w.get('type', '')} {w.get('symbol', '')} {w.get('amount', '')}\n"
        except:
            pass
    
    # Social Sentiment
    if pro_analyzer:
        msg3 += "\n📱 <b>SOSYAL MEDYA:</b>\n"
        for coin in ['BTC', 'ETH', 'SOL']:
            try:
                social = pro_analyzer.analyze_social_sentiment(coin)
                msg3 += f"   <b>{coin}</b>: {social['text']} ({social['score']}/100)\n"
            except:
                pass
    
    # Hisse Senetleri
    msg3 += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n💻 <b>HİSSELER (USD):</b>\n"
    if strong_stocks:
        for s in strong_stocks:
            msg3 += f"🟢 <b>{s['symbol']}</b> ${s['price']} +{s['weekly']:.1f}%\n"
    else:
        msg3 += "⚠️ STRONG_BUY yok\n"
    
    # Sinyal Performansı
    if signal_tracker:
        try:
            signal_tracker.auto_record_signals(rising, potential)
            signal_tracker.check_signals()
            stats = signal_tracker.get_performance_stats()
            
            if stats["total_signals"] > 0:
                msg3 += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                msg3 += f"\n📊 <b>SİNYAL PERFORMANSI:</b>\n"
                msg3 += f"   🎯 Başarı Oranı: <b>%{stats['win_rate']}</b>\n"
                msg3 += f"   ✅ Kazanan: {stats['wins']} | ❌ Kaybeden: {stats['losses']}\n"
                msg3 += f"   🔄 Aktif: {stats['active']} sinyal\n"
                msg3 += f"   💰 Toplam Kar: %{stats['total_profit']}\n"
        except Exception as e:
            logger.error(f"Sinyal tracker hatası: {e}")
    
    msg3 += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ <b>Sonraki rapor: 2 saat</b>

📱 <b>KOMUTLAR:</b>
/pro BTC - PRO Analiz (8 modül)
/pump - Pump tespit
/performans - Sinyal başarı oranı
/analiz BTC - Detaylı analiz
/btc - Yükselecekler
/portfoy - Portföy durumu
"""
    
    if send_telegram(msg3):
        logger.info("✅ ULTRA Rapor Telegram'a gönderildi!")
    else:
        logger.error("❌ Telegram hatası")

# ===================== TELEGRAM BOT (Gelişmiş) =====================
def run_telegram_bot():
    logger.info("📱 Telegram bot başlatılıyor...")
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    last_update_id = 0
    
    while True:
        try:
            resp = requests.get(f"{api_url}/getUpdates", params={'offset': last_update_id + 1, 'timeout': 30}, timeout=35)
            
            if resp.status_code == 200:
                for update in resp.json().get('result', []):
                    last_update_id = update['update_id']
                    
                    if 'message' in update:
                        message = update['message']
                        chat_id = message.get('chat', {}).get('id')
                        text = message.get('text', '').strip()
                        
                        if text.startswith('/'):
                            parts = text.split()
                            cmd = parts[0].lower().split('@')[0]
                            args = parts[1:] if len(parts) > 1 else []
                            
                            # /start, /yardim
                            if cmd in ['/start', '/yardim', '/help']:
                                help_msg1 = """🚀 <b>AKILLI YATIRIM ASİSTANI - ULTRA</b>
━━━━━━━━━━━━━━━━━━━━━━
📊 341+ Kripto | 💰 Tüm Fiyatlar TL | 🤖 15 Modül Aktif
━━━━━━━━━━━━━━━━━━━━━━

📈 <b>ANALİZ KOMUTLARI:</b>

/btc
↳ Yükselecek kriptoları listeler
↳ Hedef fiyat, stop loss, potansiyel kar
↳ Örnek: Günlük en iyi 7 fırsat

/analiz BTC
↳ Tek kripto için detaylı teknik analiz
↳ RSI, MACD, Bollinger, trend durumu
↳ Örnek: /analiz ETH, /analiz AVAX

/piyasa
↳ Global piyasa durumu özeti
↳ BTC dominansı, toplam piyasa değeri
↳ Majör coinlerin anlık durumu

/fib BTC
↳ Fibonacci destek/direnç seviyeleri
↳ %23.6, %38.2, %50, %61.8, %78.6
↳ Alım-satım noktaları için kritik

/grafik BTC
↳ Fiyat grafiğini resim olarak gönderir
↳ Son 30 günlük fiyat hareketi
↳ Teknik göstergelerle birlikte

🔬 <b>PRO ANALİZ (8 MODÜL):</b>

/pro BTC
↳ 8 modüllü tam PRO analiz
↳ RSI(14) + MACD + Bollinger + Hacim
↳ Fear&Greed + BTC Korelasyon + Whale + Sosyal

/pump
↳ Pump dedektörü - anlık spike tespiti
↳ %10+ yükselenler + yüksek hacim

/korku
↳ Fear & Greed Index (Korku/Açgözlülük)
↳ Piyasa duygu durumu 0-100 skalası"""
                                send_telegram_to(chat_id, help_msg1)
                                
                                help_msg2 = """🎭 <b>SENTIMENT ANALİZİ:</b>

/sentiment
↳ Fear & Greed Index (Korku/Açgözlülük)
↳ Funding Rate (Long/Short oranı)
↳ Piyasa genel duygu durumu

/sosyal
↳ Twitter ve Reddit trend analizi
↳ Sosyal medyada en çok konuşulanlar
↳ Topluluk sentiment skoru

/haber
↳ AI destekli haber analizi
↳ Kripto haberlerinden sentiment çıkarımı
↳ Pozitif/negatif haber oranı

━━━━━━━━━━━━━━━━━━━━━━
📡 <b>SİNYAL SİSTEMİ:</b>

/sinyal
↳ Otomatik trade sinyalleri
↳ Giriş fiyatı, hedef, stop loss
↳ Risk/ödül oranı hesaplanmış

/whale
↳ Balina (büyük yatırımcı) hareketleri
↳ Borsa giriş/çıkış akışları
↳ Büyük alım/satım uyarıları

/ml
↳ Makine öğrenmesi fiyat tahmini
↳ 7 günlük fiyat projeksiyonu
↳ Güven oranı ile birlikte"""
                                send_telegram_to(chat_id, help_msg2)
                                
                                help_msg3 = """⭐ <b>WATCHLIST (TAKİP LİSTESİ):</b>

/favori
↳ Favori listeni görüntüle
↳ Eklediğin coinlerin anlık durumu

/favori BTC
↳ BTC'yi favorilere ekle
↳ Örnek: /favori ETH, /favori AVAX

/favori_sil BTC
↳ BTC'yi favorilerden çıkar

━━━━━━━━━━━━━━━━━━━━━━
👤 <b>KİŞİSEL RİSK YÖNETİMİ:</b>

/risk
↳ Mevcut risk profilini görüntüle
↳ Önerilen pozisyon büyüklükleri

/risk muhafazakar
↳ Düşük risk profili ayarla
↳ Küçük pozisyonlar, güvenli coinler

/risk dengeli
↳ Orta risk profili ayarla
↳ Dengeli portföy önerileri

/risk agresif
↳ Yüksek risk profili ayarla
↳ Yüksek potansiyel, yüksek risk

/sermaye 50000
↳ Toplam sermayeni TL olarak ayarla
↳ Pozisyon büyüklüğü hesaplaması için"""
                                send_telegram_to(chat_id, help_msg3)
                                
                                help_msg4 = """💹 <b>İŞLEM TAKİBİ:</b>

/islem BTC 3500000 0.01
↳ Yeni işlem kaydet
↳ Format: /islem [COIN] [FİYAT] [MİKTAR]
↳ Örnek: BTC'yi ₺3,500,000'dan 0.01 adet aldım

/kapat 1 3600000
↳ Açık işlemi kapat
↳ Format: /kapat [İŞLEM_ID] [ÇIKIŞ_FİYATI]
↳ Kar/zarar otomatik hesaplanır

/kz
↳ Kar/zarar raporu
↳ Tüm işlem geçmişi
↳ Toplam performans özeti

━━━━━━━━━━━━━━━━━━━━━━
💼 <b>PORTFÖY YÖNETİMİ:</b>

/portfoy
↳ Portföy durumu ve dağılımı
↳ Toplam değer (TL)
↳ Günlük kar/zarar

/ekle BTC 10000
↳ Portföye pozisyon ekle
↳ Format: /ekle [COIN] [TL_TUTAR]

/alarm
↳ Aktif fiyat alarmlarını listele

/backtest
↳ Strateji performans raporu
↳ Geçmiş sinyallerin başarı oranı

━━━━━━━━━━━━━━━━━━━━━━
🔄 Her 2 saatte otomatik rapor gönderilir
💰 Tüm fiyatlar Türk Lirası (₺) cinsindendir
🤖 15 modül 24/7 aktif çalışmaktadır"""
                                send_telegram_to(chat_id, help_msg4)
                            
                            # /btc - Yükselecekler (TL)
                            elif cmd == '/btc':
                                tickers = get_btcturk_data()
                                potential = analyze_potential_risers(tickers)
                                rising = analyze_rising_cryptos(tickers)
                                
                                msg = "🔮 <b>YÜKSELECEK KRİPTOLAR (TL)</b>\n\n"
                                
                                if potential:
                                    for i, p in enumerate(potential[:7], 1):
                                        msg += f"""<b>{i}. 🎯 {p['symbol']}</b>
   💰 ₺{p['price']:,.2f} TL
   📈 Potansiyel: +{p['potential']}%
   🎯 Hedef: ₺{p['target']:,.2f} TL
   🛑 Stop: ₺{p['stop']:,.2f} TL
   ⏱️ {p.get('days_estimate', '3-7 gün')}
   
"""
                                
                                if rising:
                                    msg += "\n🔥 <b>ŞU AN YÜKSELENLER:</b>\n"
                                    for r in rising[:3]:
                                        msg += f"• {r['symbol']} +{r['change']:.1f}% | ₺{r['price']:,.2f}\n"
                                
                                send_telegram_to(chat_id, msg or "⚠️ Sinyal yok")
                            
                            # /analiz [COIN] - Detaylı analiz (TL)
                            elif cmd == '/analiz':
                                symbol = args[0].upper() if args else 'BTC'
                                
                                if detailed:
                                    report = detailed.generate_report(symbol)
                                    send_telegram_to(chat_id, report)
                                else:
                                    analysis = analyze_crypto_detailed(symbol)
                                    if analysis:
                                        msg = f"""🔍 <b>DETAYLI ANALİZ: {symbol} (TL)</b>

💰 Fiyat: ₺{analysis['price']:,.2f} TL
📈 24s: {analysis['change']:+.2f}%
📊 RSI: {analysis['rsi']}
📉 MACD: {analysis['macd']}

{''.join([s + chr(10) for s in analysis['signals']])}
🎯 <b>Skor: {analysis['score']}/100</b>
✅ <b>{analysis['recommendation']}</b>

🎯 Hedef: ₺{analysis['target']:,.2f} TL
🛑 Stop: ₺{analysis['stop']:,.2f} TL"""
                                        send_telegram_to(chat_id, msg)
                                    else:
                                        send_telegram_to(chat_id, f"❌ {symbol} TL paritesi bulunamadı")
                            
                            # /piyasa - Global
                            elif cmd == '/piyasa':
                                gs = get_global_market_sentiment()
                                msg = f"""🌍 <b>GLOBAL PİYASA</b>

📊 Durum: {gs['sentiment']}
🪙 Kripto Etkisi: {gs['crypto_impact']}

📈 <b>ENDEKSler:</b>
"""
                                for n, c in gs.get('indices', {}).items():
                                    msg += f"{'📈' if c > 0 else '📉'} {n}: {'+' if c > 0 else ''}{c}%\n"
                                send_telegram_to(chat_id, msg)
                            
                            # /whale - Whale tracking
                            elif cmd == '/whale':
                                if whale_tracker:
                                    report = whale_tracker.generate_whale_report()
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "🐋 Whale tracker yükleniyor...")
                            
                            # /haber - AI Haberci
                            elif cmd == '/haber':
                                if news_analyzer:
                                    report = news_analyzer.generate_report()
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "📰 Haber analizi yükleniyor...")
                            
                            # /ml - ML Tahmin
                            elif cmd == '/ml':
                                if ml_predictor:
                                    report = ml_predictor.generate_report()
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "🤖 ML modeli yükleniyor...")
                            
                            # /portfoy - Portföy durumu
                            elif cmd == '/portfoy':
                                if portfolio:
                                    report = portfolio.generate_report()
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "💼 Portföy modülü yükleniyor...")
                            
                            # /ekle [COIN] [TUTAR] - Pozisyon ekle (TL)
                            elif cmd == '/ekle':
                                if portfolio and len(args) >= 2:
                                    symbol = args[0].upper()
                                    try:
                                        amount = float(args[1].replace('₺', '').replace('TL', ''))
                                        pos = portfolio.add_position(symbol, amount)
                                        if pos:
                                            send_telegram_to(chat_id, f"✅ {symbol} ₺{amount:,.2f} TL eklendi!")
                                        else:
                                            send_telegram_to(chat_id, "❌ Eklenemedi")
                                    except:
                                        send_telegram_to(chat_id, "❌ Format: /ekle BTC 1000")
                                else:
                                    send_telegram_to(chat_id, "📝 Kullanım: /ekle BTC 1000 (TL)")
                            
                            # /alarm - Aktif alarmlar (TL)
                            elif cmd == '/alarm':
                                if alert_system:
                                    alerts = alert_system.get_active_alerts()
                                    if alerts:
                                        msg = "🔔 <b>AKTİF ALARMLAR (TL)</b>\n\n"
                                        for a in alerts[:10]:
                                            msg += f"• {a['symbol']}: ₺{a['entry_price']:,.2f}\n  🎯 ₺{a['target_price']:,.2f} | 🛑 ₺{a['stop_loss']:,.2f}\n\n"
                                        send_telegram_to(chat_id, msg)
                                    else:
                                        send_telegram_to(chat_id, "🔔 Aktif alarm yok")
                                else:
                                    send_telegram_to(chat_id, "🔔 Alarm sistemi yükleniyor...")
                            
                            # /backtest - Performans
                            elif cmd == '/backtest':
                                if backtest:
                                    report = backtest.generate_report()
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "📊 Backtest modülü yükleniyor...")
                            
                            # /fib [COIN] - Fibonacci seviyeleri
                            elif cmd == '/fib':
                                symbol = args[0].upper() if args else 'BTC'
                                if indicators:
                                    report = indicators.generate_report(symbol)
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "📐 Fibonacci modülü yükleniyor...")
                            
                            # /sentiment - Fear & Greed + Funding Rate
                            elif cmd == '/sentiment':
                                if market_sent:
                                    report = market_sent.generate_report()
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "🎭 Sentiment modülü yükleniyor...")
                            
                            # /sosyal - Sosyal medya sentiment
                            elif cmd == '/sosyal':
                                if social_sent:
                                    report = social_sent.generate_report()
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "📱 Sosyal medya modülü yükleniyor...")
                            
                            # /grafik [COIN] - Fiyat grafiği gönder
                            elif cmd == '/grafik':
                                symbol = args[0].upper() if args else 'BTC'
                                if chart_gen:
                                    send_telegram_to(chat_id, f"📊 {symbol} grafiği hazırlanıyor...")
                                    success = chart_gen.generate_and_send(symbol, chat_id, 30)
                                    if not success:
                                        send_telegram_to(chat_id, f"❌ {symbol} grafiği oluşturulamadı")
                                else:
                                    send_telegram_to(chat_id, "📊 Grafik modülü yükleniyor...")
                            
                            # /sinyal - Trade sinyalleri
                            elif cmd == '/sinyal':
                                if trade_sig:
                                    report = trade_sig.generate_report()
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "📡 Sinyal modülü yükleniyor...")
                            
                            # /favori [COIN] - Watchlist'e ekle
                            elif cmd == '/favori':
                                if watchlist and args:
                                    symbol = args[0].upper()
                                    user = str(chat_id)
                                    if watchlist.add_to_watchlist(user, symbol):
                                        send_telegram_to(chat_id, f"⭐ {symbol} favorilere eklendi!")
                                    else:
                                        send_telegram_to(chat_id, f"⚠️ {symbol} zaten favorilerde")
                                elif watchlist:
                                    report = watchlist.generate_report(str(chat_id))
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "⭐ Watchlist modülü yükleniyor...")
                            
                            # /favori_sil [COIN] - Watchlist'ten çıkar
                            elif cmd == '/favori_sil':
                                if watchlist and args:
                                    symbol = args[0].upper()
                                    user = str(chat_id)
                                    if watchlist.remove_from_watchlist(user, symbol):
                                        send_telegram_to(chat_id, f"❌ {symbol} favorilerden çıkarıldı")
                                    else:
                                        send_telegram_to(chat_id, f"⚠️ {symbol} favorilerde yok")
                                else:
                                    send_telegram_to(chat_id, "📝 Kullanım: /favori_sil BTC")
                            
                            # /risk [seviye] - Risk profili ayarla
                            elif cmd == '/risk':
                                if risk_prof:
                                    user = str(chat_id)
                                    if args:
                                        level = args[0].lower()
                                        level_map = {'muhafazakar': 'conservative', 'dengeli': 'moderate', 'agresif': 'aggressive'}
                                        if level in level_map:
                                            risk_prof.set_profile(user, level_map[level])
                                            send_telegram_to(chat_id, f"✅ Risk profili: {level.title()}")
                                        else:
                                            send_telegram_to(chat_id, "📝 Seçenekler: muhafazakar, dengeli, agresif")
                                    else:
                                        report = risk_prof.generate_report(user)
                                        send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "👤 Risk modülü yükleniyor...")
                            
                            # /sermaye [TL] - Sermaye ayarla
                            elif cmd == '/sermaye':
                                if risk_prof and args:
                                    try:
                                        user = str(chat_id)
                                        amount = float(args[0].replace('₺', '').replace('TL', ''))
                                        profile = risk_prof.get_profile(user)
                                        level = profile.get('risk_level', 'moderate') if profile else 'moderate'
                                        risk_prof.set_profile(user, level, amount)
                                        send_telegram_to(chat_id, f"✅ Sermaye: ₺{amount:,.0f} TL")
                                    except:
                                        send_telegram_to(chat_id, "❌ Format: /sermaye 50000")
                                else:
                                    send_telegram_to(chat_id, "📝 Kullanım: /sermaye 50000")
                            
                            # /islem [COIN] [FIYAT] [MIKTAR] - İşlem kaydet
                            elif cmd == '/islem':
                                if trade_hist and len(args) >= 3:
                                    try:
                                        user = str(chat_id)
                                        symbol = args[0].upper()
                                        entry = float(args[1])
                                        amount = float(args[2])
                                        trade = trade_hist.add_trade(user, {
                                            'symbol': symbol,
                                            'entry_price': entry,
                                            'amount': amount
                                        })
                                        send_telegram_to(chat_id, f"✅ İşlem #{trade['id']} kaydedildi\n{symbol} ₺{entry:,.2f} x {amount}")
                                    except:
                                        send_telegram_to(chat_id, "❌ Format: /islem BTC 100000 0.5")
                                elif trade_hist:
                                    report = trade_hist.generate_report(str(chat_id))
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "💹 İşlem modülü yükleniyor...")
                            
                            # /kapat [ID] [FIYAT] - İşlem kapat
                            elif cmd == '/kapat':
                                if trade_hist and len(args) >= 2:
                                    try:
                                        user = str(chat_id)
                                        trade_id = int(args[0])
                                        exit_price = float(args[1])
                                        trade = trade_hist.close_trade(user, trade_id, exit_price)
                                        if trade:
                                            emoji = '📈' if trade['profit_loss'] >= 0 else '📉'
                                            send_telegram_to(chat_id, f"{emoji} İşlem #{trade_id} kapatıldı\nK/Z: ₺{trade['profit_loss']:,.2f} ({trade['profit_loss_pct']:+.1f}%)")
                                        else:
                                            send_telegram_to(chat_id, "❌ İşlem bulunamadı")
                                    except:
                                        send_telegram_to(chat_id, "❌ Format: /kapat 1 105000")
                                else:
                                    send_telegram_to(chat_id, "📝 Kullanım: /kapat 1 105000")
                            
                            # /kz - Kar/Zarar raporu
                            elif cmd == '/kz':
                                if trade_hist:
                                    report = trade_hist.generate_report(str(chat_id))
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "💹 K/Z modülü yükleniyor...")
                            
                            # /pro [COIN] - PRO Analiz (8 modül)
                            elif cmd == '/pro':
                                symbol = args[0].upper() if args else 'BTC'
                                if pro_analyzer:
                                    analysis = pro_analyzer.full_pro_analysis(symbol)
                                    report = pro_analyzer.format_pro_analysis(analysis)
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "🔬 PRO Analiz modülü yükleniyor...")
                            
                            # /pump - Pump dedektörü
                            elif cmd == '/pump':
                                tickers = get_btcturk_data()
                                pumps = []
                                for t in tickers:
                                    pair = t.get('pair', '')
                                    if not pair.endswith('TRY'):
                                        continue
                                    symbol = pair.replace('TRY', '')
                                    change = t.get('dailyPercent', 0)
                                    volume = t.get('volume', 0)
                                    price = t.get('last', 0)
                                    if change > 10 and volume * price > 1000000:
                                        pumps.append({'symbol': symbol, 'change': change, 'volume_tl': volume * price})
                                
                                pumps = sorted(pumps, key=lambda x: x['change'], reverse=True)[:10]
                                
                                if pumps:
                                    msg = "🚀🚀🚀 <b>PUMP TESPİT EDİLDİ!</b>\n\n"
                                    for p in pumps:
                                        msg += f"🔥 <b>{p['symbol']}</b>: +{p['change']:.1f}%\n"
                                        msg += f"   💰 Hacim: ₺{p['volume_tl']:,.0f}\n\n"
                                    send_telegram_to(chat_id, msg)
                                else:
                                    send_telegram_to(chat_id, "🔍 Şu an pump tespit edilmedi (>10% gerekli)")
                            
                            # /korku - Fear & Greed Index
                            elif cmd == '/korku':
                                if pro_analyzer:
                                    fg = pro_analyzer.get_fear_greed_index()
                                    msg = f"""😱 <b>FEAR & GREED INDEX</b>

{fg['emoji']} <b>Değer: {fg['value']}/100</b>
📊 Durum: {fg['classification']}

{fg['text']}

💡 <i>0-25: Aşırı Korku = AL fırsatı
75-100: Aşırı Açgözlülük = SAT sinyali</i>"""
                                    send_telegram_to(chat_id, msg)
                                else:
                                    send_telegram_to(chat_id, "😱 Fear & Greed modülü yükleniyor...")
                            
                            # /performans - Sinyal başarı oranı
                            elif cmd == '/performans':
                                if signal_tracker:
                                    msg = signal_tracker.format_performance_message()
                                    send_telegram_to(chat_id, msg)
                                else:
                                    send_telegram_to(chat_id, "📊 Performans modülü yükleniyor...")
                            
                            # /sniper - Gelişmiş fırsat tarama
                            elif cmd == '/sniper':
                                if sniper:
                                    send_telegram_to(chat_id, "🎯 Sniper taraması başlıyor... (10-15 sn)")
                                    scan = sniper.run_sniper_scan()
                                    report = sniper.format_sniper_report(scan)
                                    send_telegram_to(chat_id, report)
                                else:
                                    send_telegram_to(chat_id, "🎯 Sniper modülü yükleniyor...")
                            
                            # /derin - Derin tarihsel analiz
                            elif cmd == '/derin':
                                if historical_analyzer:
                                    send_telegram_to(chat_id, "🔬 Derin tarihsel analiz başlıyor... (15-20 sn)")
                                    tickers = get_btcturk_data()
                                    rising = analyze_rising_cryptos(tickers)
                                    if rising:
                                        report = historical_analyzer.deep_analysis_rising(rising)
                                        send_telegram_to(chat_id, report)
                                    else:
                                        send_telegram_to(chat_id, "📊 Şu an yükselen coin bulunamadı")
                                else:
                                    send_telegram_to(chat_id, "🔬 Tarihsel analiz modülü yükleniyor...")
            
            time.sleep(1)
        except Exception as e:
            logger.error(f"Bot error: {e}")
            time.sleep(5)

# ===================== FLASK API =====================
@app.route('/')
def home():
    return '''<html><head><title>Akıllı Yatırım - MAX</title>
    <meta charset="UTF-8">
    <style>body{background:#0f172a;color:#e2e8f0;font-family:Arial;padding:40px}h1{color:#60a5fa}.s{background:#10b981;padding:10px 20px;border-radius:5px;display:inline-block;margin:5px}.i{background:#1e293b;padding:20px;border-radius:10px;margin:20px 0}a{color:#60a5fa;text-decoration:none;margin:10px}.g{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}</style></head>
    <body><h1>🚀 AKILLI YATIRIM ASİSTANI - MAX VERSİYON</h1>
    <div class="s">✅ TÜM ÖZELLİKLER AKTIF</div>
    <div class="i"><h3>📊 ANALİZ</h3><div class="g">
    <a href="/api/analysis">📈 Tam Analiz</a>
    <a href="/api/potential">🔮 Yükselecekler</a>
    <a href="/api/btc">₿ BTC</a>
    <a href="/api/global">🌍 Global</a>
    <a href="/api/stocks">💻 Hisseler</a>
    </div></div>
    <div class="i"><h3>🚀 GELİŞMİŞ</h3><div class="g">
    <a href="/api/whale">🐋 Whale</a>
    <a href="/api/news">📰 Haberler</a>
    <a href="/api/ml">🤖 ML Tahmin</a>
    <a href="/api/portfolio">💼 Portföy</a>
    <a href="/api/alerts">🔔 Alarmlar</a>
    <a href="/api/backtest">📊 Backtest</a>
    </div></div>
    <div class="i"><h3>🔬 PRO ANALİZ</h3><div class="g">
    <a href="/api/pro/BTC">🔬 PRO BTC</a>
    <a href="/api/pro/ETH">🔬 PRO ETH</a>
    <a href="/api/pump">🚀 Pump Dedektör</a>
    <a href="/api/fear-greed">😱 Fear&Greed</a>
    </div></div>
    <div class="i"><a href="/api/send-now">📤 Rapor Gönder</a></div>
    </body></html>'''

@app.route('/api/analysis')
def api_analysis():
    tickers = get_btcturk_data()
    return jsonify({
        'rising': analyze_rising_cryptos(tickers), 
        'potential': analyze_potential_risers(tickers), 
        'btc': get_btc_technical_analysis(), 
        'global': get_global_market_sentiment(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/potential')
def api_potential():
    return jsonify(analyze_potential_risers(get_btcturk_data()))

@app.route('/api/btc')
def api_btc():
    return jsonify(get_btc_technical_analysis())

@app.route('/api/global')
def api_global():
    return jsonify(get_global_market_sentiment())

@app.route('/api/stocks')
def api_stocks():
    return jsonify(get_stock_data())

@app.route('/api/analyze/<symbol>')
def api_analyze_symbol(symbol):
    if detailed:
        return jsonify(detailed.full_analysis(symbol.upper()))
    return jsonify(analyze_crypto_detailed(symbol.upper()))

@app.route('/api/pro/<symbol>')
def api_pro_analysis(symbol):
    if pro_analyzer:
        return jsonify(pro_analyzer.full_pro_analysis(symbol.upper()))
    return jsonify({'error': 'PRO analyzer not loaded'})

@app.route('/api/pump')
def api_pump():
    tickers = get_btcturk_data()
    pumps = []
    for t in tickers:
        pair = t.get('pair', '')
        if not pair.endswith('TRY'):
            continue
        symbol = pair.replace('TRY', '')
        change = t.get('dailyPercent', 0)
        volume = t.get('volume', 0)
        price = t.get('last', 0)
        if change > 10 and volume * price > 1000000:
            pumps.append({
                'symbol': symbol,
                'change': change,
                'price': price,
                'volume_tl': volume * price
            })
    return jsonify(sorted(pumps, key=lambda x: x['change'], reverse=True)[:10])

@app.route('/api/fear-greed')
def api_fear_greed():
    if pro_analyzer:
        return jsonify(pro_analyzer.get_fear_greed_index())
    return jsonify({'error': 'PRO analyzer not loaded'})

@app.route('/api/whale')
def api_whale():
    if whale_tracker:
        return jsonify({
            'flows': whale_tracker.get_exchange_flows(),
            'top_coins': whale_tracker.track_top_coins()
        })
    return jsonify({'error': 'Whale tracker not loaded'})

@app.route('/api/news')
def api_news():
    if news_analyzer:
        return jsonify(news_analyzer.analyze_all_news())
    return jsonify({'error': 'News analyzer not loaded'})

@app.route('/api/ml')
def api_ml():
    if ml_predictor:
        return jsonify(ml_predictor.get_top_predictions())
    return jsonify({'error': 'ML predictor not loaded'})

@app.route('/api/portfolio')
def api_portfolio():
    if portfolio:
        return jsonify(portfolio.get_portfolio_value())
    return jsonify({'error': 'Portfolio tracker not loaded'})

@app.route('/api/alerts')
def api_alerts():
    if alert_system:
        return jsonify({
            'active': alert_system.get_active_alerts(),
            'stats': alert_system.get_stats()
        })
    return jsonify({'error': 'Alert system not loaded'})

@app.route('/api/backtest')
def api_backtest():
    if backtest:
        return jsonify(backtest.get_statistics())
    return jsonify({'error': 'Backtest engine not loaded'})

@app.route('/api/send-now')
def api_send():
    run_full_analysis()
    return jsonify({'success': True, 'message': 'Rapor gönderildi'})

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'active',
        'version': 'ULTRA',
        'features': {
            'technical_analysis': True,
            'prediction': True,
            'global_markets': True,
            'telegram_bot': True,
            'alerts': alert_system is not None,
            'portfolio': portfolio is not None,
            'whale_tracker': whale_tracker is not None,
            'news_analyzer': news_analyzer is not None,
            'ml_advanced': ml_predictor is not None,
            'backtesting': backtest is not None,
            'detailed_analyzer': detailed is not None,
            'fibonacci_ichimoku': indicators is not None,
            'fear_greed': market_sent is not None,
            'social_sentiment': social_sent is not None,
            'chart_generator': chart_gen is not None,
            'trade_signals': trade_sig is not None,
            'watchlist': watchlist is not None,
            'risk_profile': risk_prof is not None,
            'trade_history': trade_hist is not None
        },
        'total_modules': 15,
        'timestamp': datetime.now().isoformat()
    })

# ===================== MAIN =====================
def main():
    logger.info("=" * 60)
    logger.info("🚀 AKILLI YATIRIM ASİSTANI - ULTRA VERSİYON")
    logger.info("📊 RSI, MACD, BB, Fibonacci, Ichimoku | 🔮 Tahmin | 🌍 Global")
    logger.info("🐋 Whale | 📰 Haberci | 🤖 ML | 🔔 Alarm | 💼 Portföy | 📡 Sinyaller")
    logger.info("=" * 60)
    
    # Modül durumları - Temel
    logger.info(f"✅ Alert System: {'Aktif' if alert_system else 'Yok'}")
    logger.info(f"✅ Portfolio: {'Aktif' if portfolio else 'Yok'}")
    logger.info(f"✅ Whale Tracker: {'Aktif' if whale_tracker else 'Yok'}")
    logger.info(f"✅ Backtest: {'Aktif' if backtest else 'Yok'}")
    logger.info(f"✅ News Analyzer: {'Aktif' if news_analyzer else 'Yok'}")
    logger.info(f"✅ ML Predictor: {'Aktif' if ml_predictor else 'Yok'}")
    logger.info(f"✅ Detailed Analyzer: {'Aktif' if detailed else 'Yok'}")
    
    # Modül durumları - Yeni
    logger.info(f"✅ Advanced Indicators: {'Aktif' if indicators else 'Yok'}")
    logger.info(f"✅ Market Sentiment: {'Aktif' if market_sent else 'Yok'}")
    logger.info(f"✅ Social Sentiment: {'Aktif' if social_sent else 'Yok'}")
    logger.info(f"✅ Chart Generator: {'Aktif' if chart_gen else 'Yok'}")
    logger.info(f"✅ Trade Signals: {'Aktif' if trade_sig else 'Yok'}")
    logger.info(f"✅ Watchlist: {'Aktif' if watchlist else 'Yok'}")
    logger.info(f"✅ Risk Profile: {'Aktif' if risk_prof else 'Yok'}")
    logger.info(f"✅ Trade History: {'Aktif' if trade_hist else 'Yok'}")
    
    # Scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_full_analysis, IntervalTrigger(hours=2), id='analysis', replace_existing=True)
    
    # Alarm kontrolü her 5 dakika
    if alert_system:
        scheduler.add_job(alert_system.check_alerts, IntervalTrigger(minutes=5), id='alerts', replace_existing=True)
        alert_system.start_monitoring()
    
    scheduler.start()
    logger.info("✅ Scheduler aktif (2 saat)")
    
    # Telegram bot
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Telegram bot aktif")
    
    # İlk analiz
    run_full_analysis()
    
    # Flask
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    main()
