"""🚀 MAIN SERVICE - 7/24 ÇALIŞAN ANA SERVİS
Her 2 saatte:
1. Yükselen kriptolar (mevcut)
2. YÜKSELECEK kriptolar (yeni!)
GERÇEK VERİ - DEMO YOK
"""
import os
import requests
import yfinance as yf
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = "8268294938:AAGCvDDNHhb5-pKFQYPJrZIJTxMVmu79oYo"
TELEGRAM_CHAT_ID = "8391537149"

app = Flask(__name__)
CORS(app)

def get_btcturk_data():
    """BTCTurk verilerini al"""
    try:
        resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=15)
        return resp.json().get('data', [])
    except:
        return []

def analyze_rising_cryptos(tickers):
    """Yükselmiş kriptoları analiz et"""
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
    """YÜKSELECEK kriptoları tespit et - henüz yükselmemiş ama potansiyeli olanlar"""
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
        
        if price <= 0:
            continue
        
        score = 0
        signals = []
        
        # Birikim: Düşük değişim + Yüksek hacim
        if -3 < change < 3 and volume > 1000000:
            score += 25
            signals.append("📦 Birikim")
        
        # Dip noktası
        if -10 < change < 0 and volume > 500000:
            score += 20
            signals.append("📉 Dip")
        
        # Breakout setup
        if high > 0 and low > 0:
            price_pos = (price - low) / (high - low) if high != low else 0.5
            if price_pos < 0.3 and volume > 500000:
                score += 30
                signals.append("🎯 Breakout")
        
        # Hacim patlaması
        if volume > 5000000 and abs(change) < 5:
            score += 20
            signals.append("📊 Hacim")
        
        # Henüz yükselmemiş
        if change < 5:
            score += 10
        
        if score >= 50 and signals:
            potential_gain = ((high - price) / price * 100) if high > price else 15
            potentials.append({
                'symbol': symbol, 'price': price, 'change': change,
                'volume': volume, 'score': score, 'signals': signals,
                'potential': round(min(potential_gain, 50), 1),
                'risk': 5 if volume > 1000000 else 7
            })
    
    return sorted(potentials, key=lambda x: x['score'], reverse=True)[:5]

def get_stock_data():
    """Hisse verilerini al"""
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
                stocks.append({'symbol': sym, 'price': round(current,2), 'weekly': round(weekly,2), 'rec': rec, 'target': round(min(weekly+15, 50),1)})
        except:
            pass
    return sorted(stocks, key=lambda x: x['weekly'], reverse=True)

def send_telegram(msg):
    """Telegram'a gönder"""
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'},
            timeout=10
        )
        return resp.status_code == 200
    except:
        return False

def run_analysis():
    """Her 2 saatte çalışan tam analiz"""
    logger.info("🔄 Analiz başlıyor...")
    
    tickers = get_btcturk_data()
    rising = analyze_rising_cryptos(tickers)
    potential = analyze_potential_risers(tickers)
    stocks = get_stock_data()
    strong_stocks = [s for s in stocks if s['rec'] == 'STRONG_BUY'][:3]
    
    logger.info(f"📊 {len(tickers)} kripto analiz edildi")
    
    now = datetime.now()
    msg = f"""🔔 <b>AKILLI YATIRIM RAPORU</b>
📅 {now.strftime('%d.%m.%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 <b>ŞU AN YÜKSELENLER:</b>
"""
    
    if rising:
        for i, c in enumerate(rising[:3], 1):
            msg += f"""
🔥 <b>{i}. {c['symbol']}</b> +{c['change']:.1f}%
   💰 {c['price']:.4f} TRY | 🎯 +{c['target']:.0f}%
"""
    else:
        msg += "\n   ⚠️ Güçlü yükseliş yok\n"
    
    msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔮 <b>YÜKSELECEKLER (TAHMİN):</b>
<i>Henüz yükselmemiş ama potansiyeli olanlar</i>
"""
    
    if potential:
        for i, p in enumerate(potential[:5], 1):
            signals_str = " ".join(p['signals'][:2])
            msg += f"""
🎯 <b>{i}. {p['symbol']}</b>
   💰 {p['price']:.4f} TRY
   📊 Şu an: {'+' if p['change'] > 0 else ''}{p['change']:.1f}%
   🚀 Potansiyel: +{p['potential']}%
   📈 Skor: {p['score']}/100
   {signals_str}
"""
    else:
        msg += "\n   ⚠️ Potansiyel sinyal yok\n"
    
    msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 <b>HİSSE TAVSİYELERİ:</b>
"""
    
    if strong_stocks:
        for s in strong_stocks:
            msg += f"\n🟢 <b>{s['symbol']}</b> ${s['price']} | +{s['weekly']:.1f}%"
    else:
        msg += "\n   ⚠️ STRONG_BUY hisse yok"
    
    msg += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ <b>UYARI:</b>
✅ Stop-loss ZORUNLU!
✅ DYOR - Kendi araştırmanı yap
⏰ Sonraki rapor: 2 saat sonra
🤖 7/24 Aktif
"""
    
    if send_telegram(msg):
        logger.info("✅ Telegram'a gönderildi!")
    else:
        logger.error("❌ Telegram hatası")

# Flask Routes
@app.route('/')
def home():
    return '''<html><head><title>7/24 Aktif</title>
    <style>body{background:#0f172a;color:#e2e8f0;font-family:Arial;padding:40px}
    h1{color:#60a5fa}.s{background:#10b981;padding:10px 20px;border-radius:5px;display:inline-block}
    .i{background:#1e293b;padding:20px;border-radius:10px;margin:20px 0}a{color:#60a5fa}</style></head>
    <body><h1>🚀 AKILLI YATIRIM ASİSTANI</h1><div class="s">✅ 7/24 AKTIF</div>
    <div class="i"><p>✅ Yükselen kriptolar</p><p>✅ YÜKSELECEK kriptolar (TAHMİN)</p><p>✅ Hisse tavsiyeleri</p></div>
    <div class="i"><a href="/api/analysis">/api/analysis</a> | <a href="/api/potential">/api/potential</a> | <a href="/api/send-now">/api/send-now</a></div>
    </body></html>'''

@app.route('/api/analysis')
def api_analysis():
    tickers = get_btcturk_data()
    rising = analyze_rising_cryptos(tickers)
    potential = analyze_potential_risers(tickers)
    stocks = get_stock_data()
    return jsonify({
        'rising_cryptos': rising,
        'potential_risers': potential,
        'stocks': [s for s in stocks if s['rec'] == 'STRONG_BUY'][:5]
    })

@app.route('/api/potential')
def api_potential():
    tickers = get_btcturk_data()
    return jsonify(analyze_potential_risers(tickers))

@app.route('/api/send-now')
def api_send():
    run_analysis()
    return jsonify({'success': True})

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'active', 'features': ['rising', 'potential', 'stocks'], 'schedule': 'every_2_hours'})

def main():
    logger.info("=" * 60)
    logger.info("🚀 7/24 SERVİS BAŞLIYOR")
    logger.info("📊 GERÇEK VERİ + TAHMİN SİSTEMİ")
    logger.info("=" * 60)
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_analysis, IntervalTrigger(hours=2), id='analysis', replace_existing=True)
    scheduler.start()
    logger.info("✅ Scheduler aktif - her 2 saat")
    
    run_analysis()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    main()
