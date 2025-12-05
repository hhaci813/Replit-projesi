"""🚀 MAIN SERVICE - 7/24 ÇALIŞAN ANA SERVİS
Her 2 saatte BTCTurk + Hisse analizi + Telegram bildirimi
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

# Telegram Config
TELEGRAM_TOKEN = "8268294938:AAGCvDDNHhb5-pKFQYPJrZIJTxMVmu79oYo"
TELEGRAM_CHAT_ID = "8391537149"

app = Flask(__name__)
CORS(app)

def get_btcturk_data():
    """BTCTurk GERÇEK kripto verileri"""
    try:
        resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=15)
        tickers = resp.json().get('data', [])
        
        cryptos = []
        for t in tickers:
            if isinstance(t, dict) and 'TRY' in t.get('pairNormalized', ''):
                symbol = t['pairNormalized'].split('_')[0]
                change = float(t.get('dailyPercent', 0))
                price = float(t.get('last', 0))
                volume = float(t.get('volume', 0))
                
                if price > 0:
                    momentum = 100 if change > 15 else (80 if change > 10 else (60 if change > 5 else (40 if change > 2 else 20 if change > 0 else 0)))
                    if volume > 1000000: momentum += 10
                    rec = "STRONG_BUY" if momentum >= 80 else ("BUY" if momentum >= 50 else "HOLD")
                    cryptos.append({'symbol': symbol, 'change': change, 'price': price, 'rec': rec, 'target': min(change+25, 100)})
        
        return sorted(cryptos, key=lambda x: x['change'], reverse=True)
    except Exception as e:
        logger.error(f"BTCTurk error: {e}")
        return []

def get_stock_data():
    """YFinance GERÇEK hisse verileri"""
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
    """Her 2 saatte çalışan analiz"""
    logger.info("🔄 Analiz başlıyor...")
    
    cryptos = get_btcturk_data()
    stocks = get_stock_data()
    strong_crypto = [c for c in cryptos if c['rec'] == 'STRONG_BUY'][:5]
    strong_stocks = [s for s in stocks if s['rec'] == 'STRONG_BUY'][:5]
    
    logger.info(f"📊 {len(cryptos)} kripto, {len(stocks)} hisse analiz edildi")
    
    now = datetime.now()
    msg = f"""🔔 <b>OTOMATİK ANALİZ RAPORU</b>
📅 {now.strftime('%d.%m.%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 <b>YÜKSELIŞE GEÇECEK KRİPTOLAR:</b>
(BTCTurk - GERÇEK VERİ)
"""
    
    if strong_crypto:
        for i, c in enumerate(strong_crypto, 1):
            msg += f"""
🔥 <b>{i}. {c['symbol']}</b>
   💰 Fiyat: {c['price']:.4f} TRY
   📈 Değişim: +{c['change']:.2f}%
   🎯 Hedef: +{c['target']:.1f}%
   ✅ <b>KESIN AL</b>
"""
    else:
        msg += "\n   ⚠️ Şu an STRONG_BUY kripto yok\n"
    
    msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 <b>YÜKSELIŞE GEÇECEK HİSSELER:</b>
(YFinance - GERÇEK VERİ)
"""
    
    if strong_stocks:
        for i, s in enumerate(strong_stocks, 1):
            msg += f"""
🟢 <b>{i}. {s['symbol']}</b>
   💵 Fiyat: ${s['price']}
   📊 Haftalık: +{s['weekly']:.2f}%
   🎯 Hedef: +{s['target']:.1f}%
   ✅ <b>KESIN AL</b>
"""
    else:
        msg += "\n   ⚠️ Şu an STRONG_BUY hisse yok\n"
    
    msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ <b>RİSK YÖNETİMİ:</b>
✅ STRONG_BUY = Kesin al
❌ Stop Loss: ZORUNLU!
❌ Diversify: Min 5 sembol

⏰ Sonraki rapor: 2 saat sonra
🤖 7/24 Aktif Sistem
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
    <div class="i"><p>✅ Her 2 saatte analiz</p><p>✅ Telegram bildirimi</p><p>✅ GERÇEK VERİ</p></div>
    <div class="i"><a href="/api/analysis">/api/analysis</a> | <a href="/api/send-now">/api/send-now</a></div>
    </body></html>'''

@app.route('/api/analysis')
def api_analysis():
    cryptos = get_btcturk_data()
    stocks = get_stock_data()
    return jsonify({
        'cryptos': [c for c in cryptos if c['rec'] == 'STRONG_BUY'][:5],
        'stocks': [s for s in stocks if s['rec'] == 'STRONG_BUY'][:5],
        'total_cryptos': len(cryptos),
        'total_stocks': len(stocks)
    })

@app.route('/api/send-now')
def api_send():
    run_analysis()
    return jsonify({'success': True})

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'active', 'mode': 'REAL_DATA', 'schedule': 'every_2_hours', 'bot': '@Sivas94bot'})

def main():
    logger.info("=" * 60)
    logger.info("🚀 7/24 SERVİS BAŞLIYOR")
    logger.info("📊 GERÇEK VERİ - DEMO YOK")
    logger.info("⏰ Her 2 saatte analiz")
    logger.info("📱 Telegram: @Sivas94bot")
    logger.info("=" * 60)
    
    # Scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_analysis, IntervalTrigger(hours=2), id='analysis', replace_existing=True)
    scheduler.start()
    logger.info("✅ Scheduler aktif - her 2 saat")
    
    # İlk analiz
    run_analysis()
    
    # Flask
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    main()
