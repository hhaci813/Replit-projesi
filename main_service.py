"""🚀 MAIN SERVICE - 7/24 ÇALIŞAN ANA SERVİS
Background BTC analizi + Flask Dashboard + Telegram Bot
"""
import os
import threading
import time
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)
CORS(app)

# Import analyzers
from background_btc_service import RealDataBTCAnalyzer, TelegramNotifier, run_scheduled_analysis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Global scheduler
scheduler = None

@app.route('/')
def home():
    """Ana sayfa"""
    return '''
    <html>
    <head>
        <title>Akıllı Yatırım Asistanı - 7/24 AKTIF</title>
        <style>
            body { background: #0f172a; color: #e2e8f0; font-family: Arial; padding: 40px; }
            h1 { color: #60a5fa; }
            .status { background: #10b981; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block; }
            .info { background: #1e293b; padding: 20px; border-radius: 10px; margin: 20px 0; }
            a { color: #60a5fa; }
        </style>
    </head>
    <body>
        <h1>🚀 AKILLI YATIRIM ASİSTANI</h1>
        <div class="status">✅ 7/24 AKTIF - GERÇEK VERİ</div>
        
        <div class="info">
            <h2>📊 Sistem Durumu</h2>
            <p>✅ BTCTurk analizi: Her 2 saatte bir</p>
            <p>✅ Hisse analizi: Her 2 saatte bir</p>
            <p>✅ Telegram bildirimi: Otomatik</p>
            <p>✅ Veri tipi: GERÇEK (Demo yok)</p>
        </div>
        
        <div class="info">
            <h2>🔗 API Endpoints</h2>
            <p><a href="/api/analysis">/api/analysis</a> - Güncel analiz JSON</p>
            <p><a href="/api/status">/api/status</a> - Sistem durumu</p>
            <p><a href="/api/send-now">/api/send-now</a> - Şimdi Telegram'a gönder</p>
        </div>
        
        <div class="info">
            <h2>📱 Telegram</h2>
            <p>Bot otomatik olarak her 2 saatte bir analiz gönderir.</p>
            <p>Replit kapansa bile scheduled deployment ile çalışmaya devam eder.</p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/status')
def status():
    """Sistem durumu"""
    return jsonify({
        'status': 'active',
        'mode': 'REAL_DATA',
        'schedule': 'every_2_hours',
        'telegram': 'enabled',
        'security': 'token_based'
    })

@app.route('/api/analysis')
def analysis():
    """Güncel analiz"""
    analyzer = RealDataBTCAnalyzer()
    cryptos = analyzer.get_btcturk_real_data()
    stocks = analyzer.get_stock_real_data()
    
    return jsonify({
        'cryptos': {
            'total': len(cryptos),
            'strong_buy': [c for c in cryptos if c['recommendation'] == 'STRONG_BUY'][:5],
            'buy': [c for c in cryptos if c['recommendation'] == 'BUY'][:5]
        },
        'stocks': {
            'total': len(stocks),
            'strong_buy': [s for s in stocks if s['recommendation'] == 'STRONG_BUY'][:5],
            'buy': [s for s in stocks if s['recommendation'] == 'BUY'][:5]
        }
    })

@app.route('/api/send-now')
def send_now():
    """Şimdi Telegram'a gönder"""
    try:
        run_scheduled_analysis()
        return jsonify({'success': True, 'message': 'Sent to Telegram!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def start_scheduler():
    """Scheduler'ı başlat"""
    global scheduler
    
    scheduler = BackgroundScheduler()
    
    # Her 2 saatte bir çalış
    scheduler.add_job(
        run_scheduled_analysis,
        IntervalTrigger(hours=2),
        id='btc_analysis_job',
        name='BTCTurk 2-Hour Analysis',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started - every 2 hours")

def main():
    """Ana fonksiyon"""
    logger.info("=" * 60)
    logger.info("🚀 MAIN SERVICE STARTING - 7/24 AKTIF")
    logger.info("=" * 60)
    logger.info("📊 Mode: REAL DATA ONLY")
    logger.info("⏰ Schedule: Every 2 hours")
    logger.info("📱 Telegram: Auto-enabled")
    logger.info("🔒 Security: Token-based")
    logger.info("=" * 60)
    
    # Start scheduler in background
    start_scheduler()
    
    # Run initial analysis
    logger.info("🔄 Running initial analysis...")
    run_scheduled_analysis()
    
    # Start Flask
    logger.info("🌐 Starting web server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    main()

