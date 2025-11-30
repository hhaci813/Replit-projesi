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
        self.symbol = None
        self.analysis_count = 0
    
    def analyze_and_send(self):
        """Analiz yap ve Telegram'a gönder"""
        if not self.symbol:
            return
        
        self.analysis_count += 1
        
        # Analiz
        if self.symbol == "XRPTRY":
            result = self.analyzer.xrptry_manual_analysis()
            message = f"""
📊 OTOMATİK ANALIZ #{self.analysis_count}

{result['signal']} {self.symbol}

💰 Fiyat: ₺{result['current_price']}
📈 Hedef: ₺{result['target']}
🛑 Stop Loss: ₺{result['stop_loss']}

Risk/Reward: {result['risk_reward']}x
"""
        else:
            result = self.analyzer.generate_signal(self.symbol)
            if result['signal'] == "?":
                return
            
            message = f"""
📊 OTOMATİK ANALIZ #{self.analysis_count}

{result['signal']} {self.symbol}

💰 Fiyat: ${result['price']:.2f}
📊 RSI: {result['rsi']:.1f}

Target: ${result.get('price', 0) * 1.2:.2f}
"""
        
        # Telegram'a gönder
        self.telegram._send_message(message)
        print(f"✅ #{self.analysis_count} Analiz gönderildi: {self.symbol}")
    
    def start(self, symbol):
        """Otomatik analiz başlat"""
        if self.is_running:
            return "Zaten çalışıyor"
        
        self.symbol = symbol
        self.analysis_count = 0
        
        # Job ekle (her 120 saniye)
        self.scheduler.add_job(
            self.analyze_and_send,
            'interval',
            seconds=120,
            id='auto_analyzer'
        )
        
        if not self.scheduler.running:
            self.scheduler.start()
        
        self.is_running = True
        return f"✅ {symbol} için 2 dakikalık analiz başladı"
    
    def stop(self):
        """Otomatik analizi durdur"""
        if not self.is_running:
            return "Zaten durmuş"
        
        try:
            self.scheduler.remove_job('auto_analyzer')
            self.is_running = False
            return f"⛔ Analiz durduruldu. Toplam: {self.analysis_count} analiz"
        except:
            return "Hata oluştu"
    
    def status(self):
        """Durum kontrol et"""
        if self.is_running:
            return f"🟢 ÇALIŞIYOR - {self.symbol}\nToplam: {self.analysis_count} analiz"
        else:
            return "🔴 KAPALI"

if __name__ == "__main__":
    aa = AutoAnalyzer()
    print(aa.start("XRPTRY"))
    time.sleep(3)
    print(aa.status())
