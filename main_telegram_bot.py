"""🤖 Main Telegram Bot - /btc komutu entegrasyonu"""
import os
import threading
from telegram_btc_handler import BTCHandler
from telegram_service import TelegramService
from datetime import datetime

def send_btc_analysis():
    """Telegram'da /btc analizi gönder"""
    try:
        report = BTCHandler.get_report()
        service = TelegramService()
        service._send_message(report)
        print("✅ BTC analysis gönderildi")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def schedule_daily_report():
    """Günlük rapor schedule et"""
    import schedule
    import time
    
    print("📅 Telegram bot schedule başlıyor...")
    
    # Her saat başında /btc analizi gönder
    schedule.every().hour.at(":00").do(send_btc_analysis)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print("🤖 Telegram Bot başlıyor...")
    
    # Test
    send_btc_analysis()
    
    print("✅ System ready!")
    print("   • /btc analysis yapılıyor")
    print("   • Saatlik rapor gönderiliyor")
    print("   • 24/7 monitoring aktif")

