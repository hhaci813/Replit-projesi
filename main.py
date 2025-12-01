#!/usr/bin/env python3
"""🤖 AKILLI YATIRIM ASİSTANI - OTOMATIK TELEGRAM ANALIZI"""
import threading
import sys

print("\n" + "="*80)
print("🤖 AKILLI YATIRIM ASİSTANI - PRODUCTION")
print("⭐ 24/7 TELEGRAM ANALIZI + PORTFÖY MOTORü")
print("="*80)

try:
    from auto_run_system import AutoRunSystem
    from telegram_interactive import TelegramInteractiveBot
    from universal_portfolio_engine import UniversalPortfolioEngine
    
    # Sistem başlat
    auto_run_system = AutoRunSystem()
    msg = auto_run_system.start_all_systems()
    print(msg)
    print("\n✅ TELEGRAM BOTUNUZ ARKA PLANDA ÇALIŞIYOR")
    print("🔔 6 SYMBOL (BTC, XRPTRY, AAPL, MSFT, GOOGL, ETH)")
    print("⏰ DEVAMLI BACKEND ANALİZİ YAPILIYOR (Mesaj yok)")
    print("💼 100+ ARAÇ PORTFÖY MOTORü AKTIF\n")
    
    # Hoş geldiniz mesajı gönder
    bot = TelegramInteractiveBot()
    welcome_msg = """
╔═══════════════════════════════════════════╗
║ 🤖 AKILLI YATIRIM ASİSTANI BAŞLATILDI! 🤖
╚═══════════════════════════════════════════╝

✅ Sistem 24/7 Arka Planda Çalışıyor!

📊 ÖZELLIKLER:
  • 100+ Yatırım Aracı Analizi
  • Devamlı Backend Analizi Yapılıyor
  • Kişisel Portföy Tavsiyesi
  • Gerçek Zamanlı Fiyat Güncellemeleri
  
💡 KULLANMA:
  "100000" yazarsan → $100,000 bütçe için portföy önerisi
  "5000" yazarsan → $5,000 için tavsiye
  Herhangi bir miktar yazabilirsin!
  
🚀 Sistem aktif. Yatırım aracı analizi başladı!
📊 Dashboard: http://localhost:5000/
"""
    bot.telegram._send_message(welcome_msg)
    
    # Örnek portföy analizi gönder (1 dakika sonra)
    import time
    def send_sample_portfolio():
        time.sleep(60)
        try:
            bot.send_portfolio_analysis(budget=10000)
        except:
            pass
    
    portfolio_thread = threading.Thread(target=send_sample_portfolio, daemon=True)
    portfolio_thread.start()
    
    # Scheduler background thread'de çalış
    scheduler_thread = threading.Thread(
        target=auto_run_system.keep_running, 
        daemon=False
    )
    scheduler_thread.start()
    print("✅ Sistem çalışıyor... CTRL+C ile durdur\n")
    scheduler_thread.join()
    
except KeyboardInterrupt:
    print("\n❌ Sistem durduruldu")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ HATA: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
