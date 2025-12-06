"""🚀 AKILLI YATIRIM ASİSTANI - TAM VERSİYON
Tüm özellikler entegre
"""
import os
import requests
import yfinance as yf
import numpy as np
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Config - Environment variables ile güvenli
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "8268294938:AAFIdr7FfJdtq__FueMOdsvym19H8IBWdNs"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or ""

# Fallback - secrets yoksa hardcoded (geliştirme için)
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = "8268294938:AAGCvDDNHhb5-pKFQYPJrZIJTxMVmu79oYo"
if not TELEGRAM_CHAT_ID:
    TELEGRAM_CHAT_ID = "8391537149"

app = Flask(__name__)
CORS(app)

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

# ===================== ANALİZ FONKSİYONLARI =====================
def analyze_rising_cryptos(tickers):
    cryptos = []
    for t in tickers:
        if isinstance(t, dict) and 'TRY' in t.get('pairNormalized', ''):
            symbol = t['pairNormalized'].split('_')[0]
            change = float(t.get('dailyPercent', 0))
            price = float(t.get('last', 0))
            volume = float(t.get('volume', 0))
            if price > 0 and change > 5:
                momentum = 100 if change > 15 else (80 if change > 10 else 60)
                if volume > 1000000: momentum += 10
                cryptos.append({
                    'symbol': symbol, 'change': change, 'price': price,
                    'momentum': momentum, 'rec': 'STRONG_BUY' if momentum >= 80 else 'BUY',
                    'target': min(change + 25, 100)
                })
    return sorted(cryptos, key=lambda x: x['change'], reverse=True)[:5]

def analyze_potential_risers(tickers):
    potentials = []
    for t in tickers:
        if not isinstance(t, dict) or 'TRY' not in t.get('pairNormalized', ''):
            continue
        
        symbol = t['pairNormalized'].split('_')[0]
        price = float(t.get('last', 0))
        change = float(t.get('dailyPercent', 0))
        volume = float(t.get('volume', 0))
        high = float(t.get('high', 0))
        low = float(t.get('low', 0))
        
        if price <= 0 or change > 5:
            continue
        
        score = 0
        signals = []
        
        if -3 < change < 3 and volume > 1000000:
            score += 25
            signals.append("📦 Birikim")
        
        if -10 < change < 0 and volume > 500000:
            score += 20
            signals.append("📉 Dip")
        
        if high > 0 and low > 0 and high != low:
            price_pos = (price - low) / (high - low)
            if price_pos < 0.3 and volume > 500000:
                score += 30
                signals.append("🎯 Breakout")
        
        if volume > 5000000 and abs(change) < 5:
            score += 20
            signals.append("📊 Hacim")
        
        if change < -5:
            score += 15
            signals.append("📈 Oversold")
        
        if score >= 50 and signals:
            potential_gain = ((high - price) / price * 100) if high > price else 15
            potentials.append({
                'symbol': symbol, 'price': price, 'change': change,
                'volume': volume, 'score': score, 'signals': signals,
                'potential': round(min(potential_gain, 50), 1),
                'risk': 5 if volume > 1000000 else 7
            })
    
    return sorted(potentials, key=lambda x: x['score'], reverse=True)[:5]

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
                stocks.append({'symbol': sym, 'price': round(current,2), 'weekly': round(weekly,2), 'rec': rec})
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

def run_full_analysis():
    logger.info("🔄 Tam analiz başlıyor...")
    
    tickers = get_btcturk_data()
    rising = analyze_rising_cryptos(tickers)
    potential = analyze_potential_risers(tickers)
    stocks = get_stock_data()
    strong_stocks = [s for s in stocks if s['rec'] == 'STRONG_BUY'][:3]
    btc_analysis = get_btc_technical_analysis()
    global_sentiment = get_global_market_sentiment()
    
    logger.info(f"📊 {len(tickers)} kripto analiz edildi")
    
    now = datetime.now()
    msg = f"""🔔 <b>AKILLI YATIRIM RAPORU</b>
📅 {now.strftime('%d.%m.%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    if btc_analysis:
        msg += f"""
📊 <b>BTC TEKNİK ANALİZ</b>
   💰 Fiyat: ${btc_analysis['price']:,}
   📈 RSI: {btc_analysis['rsi']}
   📉 MACD: {btc_analysis['macd']}
   🎯 Skor: {btc_analysis['score']}/100
   ✅ {btc_analysis['recommendation']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    msg += f"""
🌍 <b>GLOBAL PİYASA</b>
   {global_sentiment['sentiment']} | {global_sentiment['crypto_impact']}
"""
    for name, change in global_sentiment.get('indices', {}).items():
        msg += f"   {'📈' if change > 0 else '📉'} {name}: {'+' if change > 0 else ''}{change}%\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔥 <b>YÜKSELENLER:</b>\n"
    if rising:
        for c in rising[:3]:
            msg += f"🔥 <b>{c['symbol']}</b> +{c['change']:.1f}%\n"
    else:
        msg += "⚠️ Yok\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔮 <b>YÜKSELECEKLER:</b>\n"
    if potential:
        for p in potential[:5]:
            msg += f"🎯 <b>{p['symbol']}</b> | Pot: +{p['potential']}% | Skor: {p['score']}\n"
    else:
        msg += "⚠️ Sinyal yok\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n💻 <b>HİSSELER:</b>\n"
    if strong_stocks:
        for s in strong_stocks:
            msg += f"🟢 <b>{s['symbol']}</b> ${s['price']} +{s['weekly']:.1f}%\n"
    else:
        msg += "⚠️ STRONG_BUY yok\n"
    
    msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Sonraki: 2 saat
📱 /btc /analiz /piyasa
"""
    
    if send_telegram(msg):
        logger.info("✅ Telegram'a gönderildi!")
    else:
        logger.error("❌ Telegram hatası")

# ===================== TELEGRAM BOT =====================
def run_telegram_bot():
    logger.info("📱 Telegram bot başlatılıyor...")
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    last_update_id = 0
    
    import time
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
                            cmd = text.split()[0].lower().split('@')[0]
                            
                            if cmd in ['/start', '/yardim', '/help']:
                                send_telegram_to(chat_id, "🚀 <b>AKILLI YATIRIM ASİSTANI</b>\n\n/btc - Yükselecekler\n/analiz - BTC teknik\n/piyasa - Global")
                            
                            elif cmd == '/btc':
                                tickers = get_btcturk_data()
                                potential = analyze_potential_risers(tickers)
                                if potential:
                                    msg = "🔮 <b>YÜKSELECEKLER</b>\n\n"
                                    for i, p in enumerate(potential[:5], 1):
                                        msg += f"🎯 <b>{i}. {p['symbol']}</b>\n   {p['price']:.4f} TRY | +{p['potential']}%\n\n"
                                    send_telegram_to(chat_id, msg)
                                else:
                                    send_telegram_to(chat_id, "⚠️ Sinyal yok")
                            
                            elif cmd == '/analiz':
                                btc = get_btc_technical_analysis()
                                if btc:
                                    send_telegram_to(chat_id, f"📊 <b>BTC</b>\n💰 ${btc['price']:,}\n📈 RSI: {btc['rsi']}\n📉 MACD: {btc['macd']}\n✅ {btc['recommendation']}")
                            
                            elif cmd == '/piyasa':
                                gs = get_global_market_sentiment()
                                msg = f"🌍 <b>GLOBAL</b>\n{gs['sentiment']} | {gs['crypto_impact']}\n"
                                for n, c in gs.get('indices', {}).items():
                                    msg += f"{'📈' if c > 0 else '📉'} {n}: {'+' if c > 0 else ''}{c}%\n"
                                send_telegram_to(chat_id, msg)
            
            time.sleep(1)
        except Exception as e:
            logger.error(f"Bot error: {e}")
            time.sleep(5)

# ===================== FLASK =====================
@app.route('/')
def home():
    return '''<html><head><title>Akıllı Yatırım</title>
    <style>body{background:#0f172a;color:#e2e8f0;font-family:Arial;padding:40px}h1{color:#60a5fa}.s{background:#10b981;padding:10px 20px;border-radius:5px;display:inline-block}.i{background:#1e293b;padding:20px;border-radius:10px;margin:20px 0}a{color:#60a5fa}</style></head>
    <body><h1>🚀 AKILLI YATIRIM ASİSTANI</h1><div class="s">✅ TÜM ÖZELLİKLER AKTIF</div>
    <div class="i"><a href="/api/analysis">/api/analysis</a> | <a href="/api/potential">/api/potential</a> | <a href="/api/btc">/api/btc</a> | <a href="/api/send-now">/api/send-now</a></div></body></html>'''

@app.route('/api/analysis')
def api_analysis():
    tickers = get_btcturk_data()
    return jsonify({'rising': analyze_rising_cryptos(tickers), 'potential': analyze_potential_risers(tickers), 'btc': get_btc_technical_analysis(), 'global': get_global_market_sentiment()})

@app.route('/api/potential')
def api_potential():
    return jsonify(analyze_potential_risers(get_btcturk_data()))

@app.route('/api/btc')
def api_btc():
    return jsonify(get_btc_technical_analysis())

@app.route('/api/global')
def api_global():
    return jsonify(get_global_market_sentiment())

@app.route('/api/send-now')
def api_send():
    run_full_analysis()
    return jsonify({'success': True})

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'active', 'features': ['technical', 'prediction', 'global', 'bot']})

# ===================== MAIN =====================
def main():
    logger.info("=" * 60)
    logger.info("🚀 AKILLI YATIRIM ASİSTANI - TAM VERSİYON")
    logger.info("📊 RSI, MACD | 🔮 Tahmin | 🌍 Global | 📱 Bot")
    logger.info("=" * 60)
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_full_analysis, IntervalTrigger(hours=2), id='analysis', replace_existing=True)
    scheduler.start()
    logger.info("✅ Scheduler aktif")
    
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Telegram bot aktif")
    
    run_full_analysis()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    main()
