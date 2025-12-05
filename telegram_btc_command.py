"""📱 Telegram /btc Command Handler - Özellikle BTC komutu"""
import telebot
import os
import json
from datetime import datetime
import requests
import yfinance as yf

# Bot initialize
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or "8268294938:AAGCvDDNHhb5-pKFQYPJrZIJTxMVmu79oYo"
CHAT_ID = 8391537149

bot = telebot.TeleBot(TOKEN)

class BTCCommandHandler:
    """Telegram /btc komutu handler"""
    
    @staticmethod
    def analyze_btcturk_cryptos():
        """BTCTurk'deki TÜM kriptolara analiz yap"""
        try:
            url = "https://api.btcturk.com/api/v2/ticker"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if isinstance(data, dict) and 'data' in data:
                tickers = data['data']
            else:
                tickers = data if isinstance(data, list) else []
            
            # Filter and analyze
            cryptos = []
            for ticker in tickers:
                if isinstance(ticker, dict):
                    pair = ticker.get('pairNormalized', ticker.get('pair', ''))
                    if 'TRY' in pair:
                        symbol = pair.split('_')[0] if '_' in pair else ''
                        if symbol:
                            change = float(ticker.get('dailyPercent', 0))
                            price = float(ticker.get('last', 0))
                            volume = float(ticker.get('volume', 0))
                            
                            if price > 0:
                                cryptos.append({
                                    'symbol': symbol,
                                    'change': change,
                                    'price': price,
                                    'volume': volume
                                })
            
            # Sort by change
            gainers = sorted([c for c in cryptos if c['change'] > 0], key=lambda x: x['change'], reverse=True)
            losers = sorted([c for c in cryptos if c['change'] < 0], key=lambda x: x['change'])
            
            return {
                'gainers': gainers[:10],
                'losers': losers[:5],
                'total': len(cryptos)
            }
        except Exception as e:
            return {'error': str(e), 'gainers': [], 'losers': []}
    
    @staticmethod
    def analyze_stocks():
        """Hisse senetlerinin yükselenlerini bul"""
        stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'INTC', 'AMD']
        stock_data = []
        
        for symbol in stocks:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                
                if len(hist) > 1:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = ((current - prev) / prev * 100) if prev != 0 else 0
                    
                    stock_data.append({
                        'symbol': symbol,
                        'change': change,
                        'price': current
                    })
            except:
                pass
        
        gainers = sorted([s for s in stock_data if s['change'] > 0], key=lambda x: x['change'], reverse=True)
        losers = sorted([s for s in stock_data if s['change'] < 0], key=lambda x: x['change'])
        
        return {'gainers': gainers, 'losers': losers}
    
    @staticmethod
    def generate_report():
        """BTCTurk + Stocks detaylı rapor"""
        # BTC analysis
        crypto_data = BTCCommandHandler.analyze_btcturk_cryptos()
        stock_data = BTCCommandHandler.analyze_stocks()
        
        msg = f"""
🔍 *BTCTURK DETAYLI ANALİZİ + HİSSE GAINER'LAR* - {datetime.now().strftime('%d.%m.%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 *YÜKSELEN KRİPTO (Top 5):*
"""
        
        if crypto_data.get('gainers'):
            for i, g in enumerate(crypto_data['gainers'][:5], 1):
                emoji = "🔥" if g['change'] > 5 else "📈"
                msg += f"{i}. {emoji} {g['symbol']:8} +{g['change']:6.2f}% 💰\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *YÜKSELEN HİSSELER (Top 5):*
"""
        
        if stock_data.get('gainers'):
            for i, s in enumerate(stock_data['gainers'][:5], 1):
                emoji = "🟢" if s['change'] > 3 else "📊"
                msg += f"{i}. {emoji} {s['symbol']:8} +{s['change']:6.2f}%\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *ÖNERİLER (Yükselecek):*
   
💻 *TECH STOCKS:*
"""
        
        tech_gainers = [s for s in stock_data.get('gainers', []) if s['symbol'] in ['AAPL', 'MSFT', 'GOOGL', 'NVDA']]
        for s in tech_gainers[:3]:
            msg += f"   ✅ {s['symbol']} +{s['change']:.2f}%\n"
        
        msg += f"""
🪙 *CRYPTO:*
"""
        
        for c in crypto_data.get('gainers', [])[:3]:
            msg += f"   ✅ {c['symbol']:8} +{c['change']:.2f}%\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *STATİSTİKLER:*
   • Toplam kripto: {crypto_data.get('total', 0)}
   • Yükselen: {len([c for c in crypto_data.get('gainers', []) if c['change'] > 0])}
   • Hisse sample: {len(stock_data.get('gainers', []))}

⚠️ *UYARI:*
   • Stop Loss: -5%
   • Take Profit: +25%
   • Max Position: 5% portfolio
   • Diversifikasyon: MUST!

✅ Grafik analizi yapılıyor... (dashboard'da)
"""
        
        return msg

# Command handler
@bot.message_handler(commands=['btc'])
def handle_btc_command(message):
    """Telegram /btc komutu"""
    handler = BTCCommandHandler()
    report = handler.generate_report()
    bot.send_message(CHAT_ID, report, parse_mode='Markdown')

# Start handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    """Start command"""
    msg = """
👋 *AKILLI YATIRIM ASİSTANI* - Telegram Bot

🎯 *Komutlar:*
   /btc - BTCTurk analiz + hisse gainer'lar
   /portfolio [amount] - Portföy tavsiyesi
   /help - Tüm komutlar

📊 *Özellikler:*
   • Real-time kripto analiz
   • Hisse senedi tracking
   • Deep research
   • Kar/zarar tahmini
   • Günlük raporlar

/btc yazıp başla! 🚀
"""
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

# Help handler
@bot.message_handler(commands=['help'])
def handle_help(message):
    """Help command"""
    msg = """
📱 *KOMUTLAR:*

/btc - Detaylı analiz (Kripto + Hisse)
/portfolio [miktar] - Portföy tavsiyesi
/ticker [symbol] - Spesifik sembol analiz
/deep [asset] - Deep research
/news [keyword] - Haber arama

💡 *ÖRNEK:*
   /btc
   /portfolio 50000
   /ticker AAPL
   /deep BTC
   /news bitcoin
"""
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

# Start polling
if __name__ == "__main__":
    print("🤖 Telegram Bot başlıyor (polling mode)...")
    try:
        bot.polling()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import time
        time.sleep(15)

