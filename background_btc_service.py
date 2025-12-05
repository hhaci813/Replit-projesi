"""🔒 BACKGROUND BTC SERVICE - 7/24 ÇALIŞIR
Her 2 saatte bir BTCTurk analizi yapar ve Telegram'a gönderir.
GERÇEK VERİ - DEMO YOK - SÜREKLİ ÇALIŞIR
"""
import os
import time
import requests
import yfinance as yf
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Config
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = 8391537149

class RealDataBTCAnalyzer:
    """SADECE GERÇEK VERİ - DEMO YOK"""
    
    @staticmethod
    def get_btcturk_real_data():
        """BTCTurk'den GERÇEK kripto verileri al"""
        try:
            url = "https://api.btcturk.com/api/v2/ticker"
            resp = requests.get(url, timeout=15)
            
            if resp.status_code != 200:
                logger.error(f"BTCTurk API error: {resp.status_code}")
                return []
            
            data = resp.json()
            tickers = data.get('data', []) if isinstance(data, dict) else data
            
            cryptos = []
            for t in tickers:
                if isinstance(t, dict) and 'TRY' in t.get('pairNormalized', ''):
                    symbol = t['pairNormalized'].split('_')[0]
                    change = float(t.get('dailyPercent', 0))
                    price = float(t.get('last', 0))
                    volume = float(t.get('volume', 0))
                    high = float(t.get('high', 0))
                    low = float(t.get('low', 0))
                    
                    if price > 0:
                        # Momentum score
                        momentum = 0
                        if change > 15:
                            momentum = 100
                        elif change > 10:
                            momentum = 80
                        elif change > 5:
                            momentum = 60
                        elif change > 2:
                            momentum = 40
                        elif change > 0:
                            momentum = 20
                        
                        # Volume boost
                        if volume > 10000000:
                            momentum += 20
                        elif volume > 1000000:
                            momentum += 10
                        
                        recommendation = "STRONG_BUY" if momentum >= 80 else ("BUY" if momentum >= 50 else ("HOLD" if momentum >= 20 else "AVOID"))
                        
                        cryptos.append({
                            'symbol': symbol,
                            'price': price,
                            'change': change,
                            'volume': volume,
                            'high': high,
                            'low': low,
                            'momentum': momentum,
                            'recommendation': recommendation,
                            'target_profit': min(change + 25, 100),
                            'stop_loss': -5
                        })
            
            # Sort by momentum
            return sorted(cryptos, key=lambda x: x['momentum'], reverse=True)
        
        except Exception as e:
            logger.error(f"BTCTurk data error: {e}")
            return []
    
    @staticmethod
    def get_stock_real_data():
        """YFinance'den GERÇEK hisse verileri al"""
        stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'ADBE', 'CRM', 'INTC']
        stock_data = []
        
        for symbol in stocks:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="30d")
                
                if len(hist) >= 5:
                    current = hist['Close'].iloc[-1]
                    prev_day = hist['Close'].iloc[-2]
                    prev_week = hist['Close'].iloc[-5]
                    ma_20 = hist['Close'].tail(20).mean()
                    
                    daily_change = ((current - prev_day) / prev_day * 100) if prev_day > 0 else 0
                    weekly_change = ((current - prev_week) / prev_week * 100) if prev_week > 0 else 0
                    
                    # Momentum calculation
                    momentum = 0
                    if weekly_change > 10:
                        momentum = 90
                    elif weekly_change > 5:
                        momentum = 70
                    elif weekly_change > 2:
                        momentum = 50
                    elif weekly_change > 0:
                        momentum = 30
                    
                    if current > ma_20:
                        momentum += 10  # Above MA20
                    
                    recommendation = "STRONG_BUY" if momentum >= 80 else ("BUY" if momentum >= 50 else "HOLD")
                    
                    stock_data.append({
                        'symbol': symbol,
                        'price': round(current, 2),
                        'daily_change': round(daily_change, 2),
                        'weekly_change': round(weekly_change, 2),
                        'ma_20': round(ma_20, 2),
                        'momentum': momentum,
                        'recommendation': recommendation,
                        'target_profit': round(min(weekly_change + 15, 50), 1),
                        'stop_loss': -3
                    })
            except Exception as e:
                logger.warning(f"Stock {symbol} error: {e}")
        
        return sorted(stock_data, key=lambda x: x['momentum'], reverse=True)

class TelegramNotifier:
    """Telegram'a gerçek zamanlı bildirim gönderici"""
    
    @staticmethod
    def send_message(message):
        """Telegram'a mesaj gönder"""
        if not TELEGRAM_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not set!")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown'
            }
            resp = requests.post(url, json=payload, timeout=10)
            
            if resp.status_code == 200:
                logger.info("✅ Telegram message sent!")
                return True
            else:
                logger.error(f"Telegram error: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    @staticmethod
    def format_analysis_message(cryptos, stocks):
        """Analiz mesajını formatla"""
        now = datetime.now()
        
        msg = f"""
🔔 *OTOMATIK ANALİZ RAPORU*
📅 {now.strftime('%d.%m.%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 *YÜKSELIŞE GEÇECEK KRİPTOLAR:*
(BTCTurk - GERÇEK VERİ)

"""
        
        # Top 5 crypto
        strong_buy_crypto = [c for c in cryptos if c['recommendation'] == 'STRONG_BUY'][:5]
        buy_crypto = [c for c in cryptos if c['recommendation'] == 'BUY'][:3]
        
        if strong_buy_crypto:
            for i, c in enumerate(strong_buy_crypto, 1):
                msg += f"🔥 *{i}. {c['symbol']}*\n"
                msg += f"   💰 Fiyat: {c['price']:.4f} TRY\n"
                msg += f"   📈 Değişim: +{c['change']:.2f}%\n"
                msg += f"   🎯 Hedef: +{c['target_profit']:.1f}%\n"
                msg += f"   ⛔ Stop: {c['stop_loss']}%\n"
                msg += f"   ✅ *KESIN AL*\n\n"
        else:
            msg += "   ⚠️ Şu an STRONG_BUY kripto yok\n\n"
        
        if buy_crypto:
            msg += "📈 *FIRSAT KRİPTOLAR (BUY):*\n"
            for c in buy_crypto:
                msg += f"   • {c['symbol']} +{c['change']:.2f}%\n"
        
        msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 *YÜKSELIŞE GEÇECEK HİSSELER:*
(YFinance - GERÇEK VERİ)

"""
        
        # Top 5 stocks
        strong_buy_stocks = [s for s in stocks if s['recommendation'] == 'STRONG_BUY'][:5]
        buy_stocks = [s for s in stocks if s['recommendation'] == 'BUY'][:3]
        
        if strong_buy_stocks:
            for i, s in enumerate(strong_buy_stocks, 1):
                msg += f"🟢 *{i}. {s['symbol']}*\n"
                msg += f"   💵 Fiyat: ${s['price']}\n"
                msg += f"   📊 Haftalık: +{s['weekly_change']:.2f}%\n"
                msg += f"   🎯 Hedef: +{s['target_profit']:.1f}%\n"
                msg += f"   ⛔ Stop: {s['stop_loss']}%\n"
                msg += f"   ✅ *KESIN AL*\n\n"
        else:
            msg += "   ⚠️ Şu an STRONG_BUY hisse yok\n\n"
        
        if buy_stocks:
            msg += "📊 *FIRSAT HİSSELER (BUY):*\n"
            for s in buy_stocks:
                msg += f"   • {s['symbol']} +{s['weekly_change']:.2f}%\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ *RİSK YÖNETİMİ:*
✅ STRONG_BUY = Kesin al
✅ BUY = Fırsat varsa al
❌ Stop Loss: ZORUNLU!
❌ Diversify: Min 5 sembol
❌ Position: Max %5

⏰ *Sonraki rapor: 2 saat sonra*
🤖 *Otomatik Sistem - 7/24 Aktif*
"""
        
        return msg

def run_scheduled_analysis():
    """Her 2 saatte bir çalışan analiz"""
    logger.info("🔄 Scheduled analysis starting...")
    
    try:
        # Get real data
        analyzer = RealDataBTCAnalyzer()
        cryptos = analyzer.get_btcturk_real_data()
        stocks = analyzer.get_stock_real_data()
        
        logger.info(f"📊 Analyzed {len(cryptos)} cryptos, {len(stocks)} stocks")
        
        # Format and send
        notifier = TelegramNotifier()
        message = notifier.format_analysis_message(cryptos, stocks)
        
        if notifier.send_message(message):
            logger.info("✅ Analysis sent to Telegram!")
        else:
            logger.error("❌ Failed to send to Telegram")
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")

def start_background_service():
    """Background service başlat - 7/24 ÇALIŞIR"""
    logger.info("=" * 60)
    logger.info("🚀 BACKGROUND BTC SERVICE STARTING")
    logger.info("=" * 60)
    logger.info("📊 Mode: REAL DATA ONLY (No Demo)")
    logger.info("⏰ Schedule: Every 2 hours")
    logger.info("📱 Telegram: Automatic notifications")
    logger.info("🔒 Security: Token-based authentication")
    logger.info("=" * 60)
    
    # Create scheduler
    scheduler = BackgroundScheduler()
    
    # Add job - every 2 hours
    scheduler.add_job(
        run_scheduled_analysis,
        IntervalTrigger(hours=2),
        id='btc_analysis',
        name='BTCTurk 2-Hour Analysis',
        replace_existing=True
    )
    
    # Start scheduler
    scheduler.start()
    logger.info("✅ Scheduler started - running every 2 hours")
    
    # Run immediately on start
    logger.info("🔄 Running initial analysis...")
    run_scheduled_analysis()
    
    # Keep running
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    start_background_service()

