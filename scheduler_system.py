"""APScheduler - 24/7 Otomatik İşlem Sistemi"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
import os

class BrokerScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """Scheduler'ı başlat"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            print("✅ APScheduler başlatıldı")
    
    def stop(self):
        """Scheduler'ı durdur"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("⛔ APScheduler durduruldu")
    
    def schedule_daily_tavsiye(self):
        """Her gün 09:00'da tavsiye gönder"""
        from telegram_service import TelegramService
        
        def send_daily():
            service = TelegramService()
            service.tavsiye_gonder()
            print(f"📤 Günlük tavsiye gönderildi - {datetime.now()}")
        
        self.scheduler.add_job(
            send_daily,
            CronTrigger(hour=9, minute=0),
            id='daily_tavsiye',
            name='Günlük Tavsiye'
        )
    
    def schedule_hourly_check(self):
        """Her saat fiyat kontrolü yap"""
        def check_prices():
            print(f"⏰ Saatlik fiyat kontrolü - {datetime.now()}")
        
        self.scheduler.add_job(
            check_prices,
            CronTrigger(minute=0),
            id='hourly_check',
            name='Saatlik Kontrol'
        )
    
    def schedule_trading_hours(self):
        """Pazar saati içinde otomatik işlem"""
        def market_trading():
            print(f"📊 Market saati içinde işlem - {datetime.now()}")
        
        self.scheduler.add_job(
            market_trading,
            CronTrigger(hour='9-16', minute='*/15'),  # 9:00-16:00 arası 15 dakikada bir
            id='market_trading',
            name='Market Trading'
        )
    
    def schedule_daily_report(self):
        """Günlük rapor oluştur"""
        def generate_report():
            print(f"📋 Günlük rapor oluşturuldu - {datetime.now()}")
        
        self.scheduler.add_job(
            generate_report,
            CronTrigger(hour=17, minute=0),  # Pazar kapanışında
            id='daily_report',
            name='Günlük Rapor'
        )
    
    def list_jobs(self):
        """Tüm zamanlanmış işleri göster"""
        jobs = self.scheduler.get_jobs()
        if not jobs:
            return "Zamanlanmış iş yok"
        
        result = "📅 ZAMANLANMIŞ İŞLER:\n\n"
        for job in jobs:
            result += f"• {job.name} (ID: {job.id})\n"
            result += f"  Trigger: {job.trigger}\n\n"
        return result
    
    def remove_job(self, job_id):
        """İşi kaldır"""
        try:
            self.scheduler.remove_job(job_id)
            return f"✅ İş '{job_id}' kaldırıldı"
        except:
            return f"❌ İş '{job_id}' bulunamadı"

if __name__ == "__main__":
    scheduler = BrokerScheduler()
    scheduler.start()
    scheduler.schedule_daily_tavsiye()
    scheduler.schedule_hourly_check()
    scheduler.schedule_trading_hours()
    scheduler.schedule_daily_report()
    print(scheduler.list_jobs())
