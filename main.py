#!/usr/bin/env python3
"""🤖 AKILLI YATIRIM ASİSTANI - OTOMATIK TELEGRAM ANALIZI"""
import threading
import sys

print("\n" + "="*80)
print("🤖 AKILLI YATIRIM ASİSTANI - PRODUCTION")
print("⭐ 24/7 TELEGRAM ANALIZI - HER 2 DAKİKA")
print("="*80)

try:
    from auto_run_system import AutoRunSystem
    
    auto_run_system = AutoRunSystem()
    msg = auto_run_system.start_all_systems()
    print(msg)
    print("\n✅ TELEGRAM BOTUNUZ ARKA PLANDA ÇALIŞIYOR")
    print("🔔 6 SYMBOL (BTC, XRPTRY, AAPL, MSFT, GOOGL, ETH)")
    print("⏰ HER 2 DAKİKADA ANALİZ GÖNDERİLECEK\n")
    
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
