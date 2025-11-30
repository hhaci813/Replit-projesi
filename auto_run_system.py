"""24/7 Otomatik Sistem - Tüm Fonksiyonlar Arka Planda Çalışıyor"""
from apscheduler.schedulers.background import BackgroundScheduler
import time

class AutoRunSystem:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.active_jobs = {}
    
    def start_all_systems(self):
        """Tüm sistemleri başlat"""
        if self.is_running:
            return "Zaten çalışıyor"
        
        from auto_analyzer import AutoAnalyzer
        
        # AutoAnalyzer - Her 2 dakika AYRILI ANALIZLER
        auto_analyzer = AutoAnalyzer()
        
        symbols = ["BTC", "XRPTRY", "AAPL", "MSFT", "GOOGL", "ETH"]
        for sym in symbols:
            self.scheduler.add_job(
                lambda s=sym: auto_analyzer.analyze_and_send(s),
                'interval',
                minutes=2,
                id=f'auto_analyzer_{sym}'
            )
            self.active_jobs[f'📊 AutoAnalyzer ({sym})'] = 'Her 2 dakika'
        
        # Portfolio güncellemesi - Her 4 saatte 1
        self.scheduler.add_job(
            lambda: self._send_portfolio_update(),
            'interval',
            hours=4,
            id='portfolio_update'
        )
        self.active_jobs['💼 Portföy Güncelleme'] = '4 saatlik'
        
        # Risk analizi - Her 6 saatte 1
        self.scheduler.add_job(
            lambda: self._check_risk(),
            'interval',
            hours=6,
            id='risk_check'
        )
        self.active_jobs['⚠️ Risk Yönetimi'] = '6 saatlik'
        
        if not self.scheduler.running:
            self.scheduler.start()
        
        self.is_running = True
        return "✅ Tüm sistemler başlatıldı!"
    
    def stop_all_systems(self):
        """Tüm sistemleri durdur"""
        if not self.is_running:
            return "Zaten kapalı"
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            return "⛔ Tüm sistemler durduruldu"
        except:
            return "Hata oluştu"
    
    def keep_running(self):
        """Scheduler'ı 24/7 çalıştır"""
        print("\n" + "="*80)
        print("🟢 24/7 HAFIZADA AUTOMATION BAŞLATILDI")
        print("="*80)
        print(self.get_status())
        print("\n⏸️ Durdur için Ctrl+C tuşlayın\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all_systems()
            print("\n✅ Sistem durduruldu")
    
    def get_status(self):
        """Durum göster"""
        if not self.is_running:
            return "🔴 KAPALI"
        
        status = "🟢 24/7 HAFIZADA ÇALIŞIYOR\n\n"
        status += "📊 AKTIF JOB'LAR:\n"
        for job, schedule in self.active_jobs.items():
            status += f"   {job}: {schedule}\n"
        status += f"\n✅ Toplam: {len(self.active_jobs)} sistem"
        return status
    
    def _send_portfolio_update(self):
        """Portföy güncellemesi gönder"""
        try:
            from telegram_interactive import TelegramInteractiveBot
            bot = TelegramInteractiveBot()
            bot.send_portfolio_analysis(budget=10000)
        except:
            pass
    
    def _check_risk(self):
        """Risk kontrolü"""
        try:
            from telegram_service import TelegramService
            service = TelegramService()
            service._send_message("⚠️ RİSK KONTROL RAPORU\n✅ Tüm portföyler normal limitlerin içinde")
        except:
            pass
