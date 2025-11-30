"""Otomatik 2 Dakika Analiz - APScheduler ile"""
from apscheduler.schedulers.background import BackgroundScheduler
from symbol_analyzer import SymbolAnalyzer
from telegram_service import TelegramService
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
                price = result.get('price', None)
                rsi = result.get('rsi', 50)
                ma20 = result.get('ma20', None)
                ma50 = result.get('ma50', None)
                
                # Debug
                print(f"🔍 DEBUG BTC: price={price}, result_keys={list(result.keys())}")
                
                if price is None or price == 0:
                    price_str = "Veri Alınamıyor"
                else:
                    price_str = f"${price:.2f}"
                
                message = f"""
🪙 <b>BITCOIN ANALİZİ</b> #{count}

{result['signal']}

💰 <b>Fiyat:</b> {price_str}
📊 <b>RSI:</b> {rsi:.1f}
📈 <b>MA20:</b> {"$" + str(ma20)[:8] if ma20 else "N/A"}
📉 <b>MA50:</b> {"$" + str(ma50)[:8] if ma50 else "N/A"}
ℹ️ <b>Gerekçe:</b> {', '.join(result.get('reasons', [])[:2])}

⏰ {self._get_time()}
"""
            else:
                result = self.analyzer.generate_signal(symbol)
                price = result.get('price', None)
                rsi = result.get('rsi', 50)
                ma20 = result.get('ma20', None)
                
                # Debug
                print(f"🔍 DEBUG {symbol}: price={price}, result_keys={list(result.keys())}")
                
                if price is None or price == 0:
                    price_str = "Veri Alınamıyor"
                else:
                    price_str = f"${price:.2f}"
                
                message = f"""
📊 <b>{symbol} ANALİZİ</b> #{count}

{result['signal']}

💰 <b>Fiyat:</b> {price_str}
📊 <b>RSI:</b> {rsi:.1f}
📈 <b>MA20:</b> {"$" + str(ma20)[:8] if ma20 else "N/A"}
ℹ️ <b>Gerekçe:</b> {', '.join(result.get('reasons', [])[:2])}

⏰ {self._get_time()}
"""
            
            # Telegram'a gönder
            self.telegram._send_message(message)
            print(f"✅ #{count} Analiz gönderildi: {symbol}")
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
