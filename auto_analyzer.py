"""Otomatik 2 Dakika Analiz - APScheduler ile"""
from apscheduler.schedulers.background import BackgroundScheduler
from symbol_analyzer import SymbolAnalyzer
from telegram_service import TelegramService
from price_fetcher import PriceFetcher
from trade_history import TradeHistory
import time

class AutoAnalyzer:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.analyzer = SymbolAnalyzer()
        self.telegram = TelegramService()
        self.is_running = False
        self.symbols = {}  # {symbol: count}
    
    def analyze_and_send(self, symbol):
        """Analiz yap ve Telegram'a gönder"""
        if symbol not in self.symbols:
            self.symbols[symbol] = 0
        
        self.symbols[symbol] += 1
        count = self.symbols[symbol]
        
        # Analiz
        try:
            if symbol == "XRPTRY":
                result = self.analyzer.xrptry_manual_analysis()
                message = f"""
🔍 <b>{symbol} ANALİZİ</b> #{count}

{result['signal']}

💰 <b>Fiyat:</b> ₺{result['current_price']}
📈 <b>Hedef:</b> ₺{result['target']}
🛑 <b>Stop Loss:</b> ₺{result['stop_loss']}

<b>Risk/Reward:</b> {result['risk_reward']}x
⏰ {self._get_time()}
"""
            elif symbol == "BTC":
                result = self.analyzer.generate_signal("BTC-USD")
                price = result.get('price', 0)
                rsi = result.get('rsi', 50)
                ma20 = result.get('ma20', 0)
                ma50 = result.get('ma50', 0)
                source = result.get('source', 'unknown')
                
                if price and price > 0:
                    price_str = f"${price:,.0f}"
                    ma20_str = f"${ma20:.0f}" if ma20 > 0 else "N/A"
                    ma50_str = f"${ma50:.0f}" if ma50 > 0 else "N/A"
                else:
                    price_str = "🔴 Veri Alınamıyor"
                    ma20_str = "N/A"
                    ma50_str = "N/A"
                
                print(f"✅ #{count} BTC: ${price:,.0f} ({source})")
                
                message = f"""
🪙 <b>BTC ANALİZİ</b> #{count}

{result['signal']}

💰 <b>Fiyat:</b> {price_str}
📊 <b>RSI:</b> {rsi:.1f}
📈 <b>MA20:</b> {ma20_str}
📉 <b>MA50:</b> {ma50_str}

⏰ {self._get_time()}
"""
            else:
                result = self.analyzer.generate_signal(symbol)
                price = result.get('price', 0)
                rsi = result.get('rsi', 50)
                ma20 = result.get('ma20', 0)
                source = result.get('source', 'unknown')
                
                if price and price > 0:
                    price_str = f"${price:,.2f}"
                    ma20_str = f"${ma20:.2f}" if ma20 > 0 else "N/A"
                else:
                    price_str = "🔴 Veri Alınamıyor"
                    ma20_str = "N/A"
                
                print(f"✅ #{count} {symbol}: ${price:,.2f} ({source})")
                
                message = f"""
📊 <b>{symbol} ANALİZİ</b> #{count}

{result['signal']}

💰 <b>Fiyat:</b> {price_str}
📊 <b>RSI:</b> {rsi:.1f}
📈 <b>MA20:</b> {ma20_str}

⏰ {self._get_time()}
"""
            
            # ❌ 2 DAKİKA TELEGRAM MESAJI KAPANDI - Sadece backend analizi yapılıyor
            # self.telegram._send_message(message)
            TradeHistory.log_trade(symbol, result['signal'], price, result['signal'], rsi)
            print(f"✅ #{count} {symbol}: Analiz yapıldı + Kayıt yapıldı")
        except Exception as e:
            print(f"❌ Analiz hatası {symbol}: {str(e)}")
    
    def _get_time(self):
        """Saat bilgisi"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def start(self, symbol):
        """Otomatik analiz başlat"""
        if self.is_running:
            return "Zaten çalışıyor"
        
        self.is_running = True
        return f"✅ {symbol} için 2 dakikalık analiz başladı"
    
    def stop(self):
        """Otomatik analizi durdur"""
        self.is_running = False
        return "⛔ Analiz durduruldu"
    
    def status(self):
        """Durum kontrol et"""
        if self.is_running:
            return f"🟢 ÇALIŞIYOR\nAktif: {list(self.symbols.keys())}\nToplam: {sum(self.symbols.values())} analiz"
        else:
            return "🔴 KAPALI"

if __name__ == "__main__":
    aa = AutoAnalyzer()
    print(aa.start("XRPTRY"))
    time.sleep(3)
    print(aa.status())
