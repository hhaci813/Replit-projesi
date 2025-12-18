"""📱 TELEGRAM INTERACTIVE BOT - İNTERAKTİF KOMUTLAR
/btc, /analiz, /tahmin, /piyasa komutları + Grafik Analizi
"""
import requests
import threading
import time
from datetime import datetime
import os
from pathlib import Path

TELEGRAM_TOKEN = "8268294938:AAGCvDDNHhb5-pKFQYPJrZIJTxMVmu79oYo"
TELEGRAM_CHAT_ID = "8391537149"

class TelegramBot:
    """İnteraktif Telegram botu"""
    
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self.running = False
        
        # Komutlar
        self.commands = {
            '/btc': self.cmd_btc,
            '/analiz': self.cmd_analysis,
            '/tahmin': self.cmd_prediction,
            '/piyasa': self.cmd_market,
            '/yardim': self.cmd_help,
            '/help': self.cmd_help,
            '/start': self.cmd_start,
        }
    
    def send_message(self, chat_id, text):
        """Mesaj gönder"""
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            resp = requests.post(url, json=payload, timeout=10)
            return resp.status_code == 200
        except:
            return False
    
    def get_updates(self):
        """Yeni mesajları al"""
        try:
            url = f"{self.api_url}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 30}
            resp = requests.get(url, params=params, timeout=35)
            
            if resp.status_code == 200:
                return resp.json().get('result', [])
            return []
        except:
            return []
    
    def cmd_start(self, chat_id, args):
        """Başlangıç mesajı"""
        msg = """🚀 <b>AKILLI YATIRIM ASİSTANI</b>

Hoş geldiniz! Ben 7/24 çalışan yatırım asistanınızım.

<b>Komutlar:</b>
/btc - BTCTurk kripto analizi
/analiz - Detaylı teknik analiz
/tahmin - ML ile fiyat tahmini
/piyasa - Global piyasa durumu
/yardim - Yardım

Her 2 saatte otomatik rapor alacaksınız!
"""
        return msg
    
    def cmd_help(self, chat_id, args):
        """Yardım"""
        return """📖 <b>KOMUTLAR</b>

/btc - Yükselen ve yükselecek kriptolar
/analiz [SEMBOL] - Detaylı analiz (örn: /analiz BTC)
/tahmin [SEMBOL] - ML fiyat tahmini
/piyasa - S&P500, Altın, DXY durumu
/yardim - Bu menü

<b>Otomatik Raporlar:</b>
Her 2 saatte bir analiz raporu gelir.
"""
    
    def cmd_btc(self, chat_id, args):
        """BTCTurk analizi"""
        try:
            from predictive_analyzer import PredictiveAnalyzer
            
            analyzer = PredictiveAnalyzer()
            opportunities = analyzer.get_best_opportunities(5)
            
            if not opportunities:
                return "⚠️ Şu an potansiyel sinyal bulunamadı."
            
            msg = """🔮 <b>YÜKSELECEK KRİPTOLAR</b>
<i>Henüz yükselmemiş ama potansiyeli olanlar</i>

"""
            for i, opp in enumerate(opportunities, 1):
                signals = " ".join(opp['signals'][:2])
                msg += f"""🎯 <b>{i}. {opp['symbol']}</b>
   💰 {opp['price']:.4f} TRY
   📊 Şu an: {'+' if opp['change'] > 0 else ''}{opp['change']:.1f}%
   🚀 Potansiyel: +{opp['potential']}%
   📈 Skor: {opp['score']}/100
   {signals}

"""
            
            msg += "\n⚠️ Stop-loss ZORUNLU! DYOR"
            return msg
            
        except Exception as e:
            return f"❌ Hata: {str(e)}"
    
    def cmd_analysis(self, chat_id, args):
        """Detaylı analiz"""
        symbol = args[0].upper() if args else 'BTC'
        
        try:
            from technical_indicators import TechnicalIndicators
            import yfinance as yf
            
            # Fiyat verisi al
            ticker_map = {
                'BTC': 'BTC-USD',
                'ETH': 'ETH-USD',
                'SOL': 'SOL-USD',
                'XRP': 'XRP-USD'
            }
            
            yf_symbol = ticker_map.get(symbol, f'{symbol}-USD')
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period='30d')
            
            if len(hist) < 20:
                return f"⚠️ {symbol} için yeterli veri yok"
            
            prices = hist['Close'].tolist()
            
            ti = TechnicalIndicators()
            result = ti.get_full_analysis(prices)
            
            msg = f"""📊 <b>{symbol} TEKNİK ANALİZ</b>

<b>Göstergeler:</b>
📈 RSI: {result['rsi']}
📉 MACD: {result['macd']['trend']}
📊 Bollinger: {result['bollinger']['position']}
📈 MA Trend: {result['moving_averages'].get('trend', 'N/A')}

<b>Skor:</b> {result['score']}/100
<b>Tavsiye:</b> {result['recommendation']}

<b>Sinyaller:</b>
"""
            for signal in result['signals']:
                msg += f"• {signal}\n"
            
            return msg
            
        except Exception as e:
            return f"❌ Analiz hatası: {str(e)}"
    
    def cmd_prediction(self, chat_id, args):
        """ML tahmin"""
        symbol = args[0].upper() if args else 'BTC'
        
        try:
            from ml_price_predictor import MLPricePredictor
            import yfinance as yf
            
            ticker_map = {
                'BTC': 'BTC-USD',
                'ETH': 'ETH-USD',
                'SOL': 'SOL-USD'
            }
            
            yf_symbol = ticker_map.get(symbol, f'{symbol}-USD')
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period='60d')
            
            if len(hist) < 30:
                return f"⚠️ {symbol} için yeterli veri yok"
            
            prices = hist['Close'].tolist()
            
            predictor = MLPricePredictor()
            result = predictor.predict_next(prices)
            
            if not result:
                return "❌ Tahmin yapılamadı"
            
            msg = f"""🤖 <b>{symbol} ML TAHMİNİ</b>

💰 Mevcut: ${result['current_price']:,.2f}
🎯 Tahmin: ${result['predicted_price']:,.2f}
📊 Değişim: {'+' if result['change_percent'] > 0 else ''}{result['change_percent']}%
📈 Yön: {result['direction']}
🎯 Güven: {result['confidence']}%

<b>Tavsiye:</b> {result['recommendation']}

⚠️ ML tahminleri kesin değildir!
"""
            return msg
            
        except Exception as e:
            return f"❌ Tahmin hatası: {str(e)}"
    
    def cmd_market(self, chat_id, args):
        """Global piyasa"""
        try:
            from global_markets import GlobalMarketsAnalyzer
            
            analyzer = GlobalMarketsAnalyzer()
            result = analyzer.get_crypto_correlation_signals()
            
            sentiment = result['market_sentiment']
            
            msg = f"""🌍 <b>GLOBAL PİYASA DURUMU</b>

<b>Sentiment:</b> {sentiment['sentiment']}
<b>Kripto Etkisi:</b> {sentiment['crypto_impact']}

<b>Sinyaller:</b>
"""
            for signal in result['signals']:
                msg += f"{signal}\n"
            
            msg += "\n<b>Endeksler:</b>\n"
            for name, data in list(result.get('indices', {}).items())[:4]:
                emoji = "📈" if data['change'] > 0 else "📉"
                msg += f"{emoji} {name}: {'+' if data['change'] > 0 else ''}{data['change']}%\n"
            
            return msg
            
        except Exception as e:
            return f"❌ Piyasa hatası: {str(e)}"
    
    def download_file(self, file_id, chat_id):
        """Telegram'dan dosya indir"""
        try:
            # File info al
            url = f"{self.api_url}/getFile"
            resp = requests.get(url, params={'file_id': file_id}, timeout=10)
            
            if resp.status_code != 200:
                return None
            
            file_path = resp.json()['result']['file_path']
            
            # Dosyayı indir
            file_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
            file_resp = requests.get(file_url, timeout=10)
            
            if file_resp.status_code != 200:
                return None
            
            # Geçici klasör oluştur
            temp_dir = Path('/tmp/telegram_charts')
            temp_dir.mkdir(exist_ok=True)
            
            # Dosyayı kaydet
            local_path = temp_dir / f"{file_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(file_resp.content)
            
            return str(local_path)
            
        except Exception as e:
            print(f"Dosya indirme hatası: {e}")
            return None
    
    def process_photo(self, message):
        """Fotoğrafı işle ve analiz et"""
        try:
            chat_id = message.get('chat', {}).get('id')
            caption = message.get('caption', '').strip()
            
            # En yüksek kaliteli fotoğrafı seç
            photo = message.get('photo', [])
            if not photo:
                return
            
            file_id = photo[-1]['file_id']
            
            # Dosyayı indir
            local_path = self.download_file(file_id, chat_id)
            if not local_path:
                self.send_message(chat_id, "❌ Grafik indirilemedi")
                return
            
            # Chart analyzer'ı çağır
            from chart_analyzer import ChartAnalyzer
            analyzer = ChartAnalyzer()
            summary = analyzer.get_summary(local_path)
            
            # Sonucu gönder
            if caption:
                summary = f"<b>Grafik Adı:</b> {caption}\n\n" + summary
            
            self.send_message(chat_id, summary)
            
            # Dosyayı sil
            try:
                os.remove(local_path)
            except:
                pass
                
        except Exception as e:
            print(f"Fotoğraf işleme hatası: {e}")
            self.send_message(chat_id, f"❌ Analiz hatası: {str(e)}")
    
    def process_message(self, message):
        """Mesajı işle"""
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        
        if not text.startswith('/'):
            return
        
        parts = text.split()
        command = parts[0].lower().split('@')[0]  # @botname kaldır
        args = parts[1:]
        
        if command in self.commands:
            response = self.commands[command](chat_id, args)
            self.send_message(chat_id, response)
    
    def run_polling(self):
        """Polling ile çalıştır"""
        print("📱 Telegram bot polling başladı...")
        self.running = True
        
        while self.running:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        message = update['message']
                        
                        # Metin mesajı
                        if 'text' in message:
                            self.process_message(message)
                        
                        # Fotoğraf
                        elif 'photo' in message:
                            self.process_photo(message)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Bot error: {e}")
                time.sleep(5)
    
    def start_background(self):
        """Arka planda başlat"""
        thread = threading.Thread(target=self.run_polling, daemon=True)
        thread.start()
        return thread


if __name__ == '__main__':
    bot = TelegramBot()
    print("📱 Bot başlatılıyor...")
    bot.run_polling()
