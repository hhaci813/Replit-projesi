"""🚀 /btc System - Runs on startup"""
import os
from src.telegram.btc_analyzer import BTCAnalyzer
from src.telegram.message_formatter import format_telegram_message
from src.utils.telegram_sender import send_to_telegram

def initialize_btc_system():
    """Sistem başlat"""
    print("🔥 /btc SYSTEM STARTING...\n")
    
    # Analyze
    analyzer = BTCAnalyzer()
    data = analyzer.get_strong_recommendations()
    
    # Show recommendations
    print("✅ KESIN AL ÖNERİLERİ:\n")
    print("🔥 STRONG_BUY KRİPTO:")
    for c in [x for x in data['cryptos'] if x['recommendation'] == 'STRONG_BUY'][:3]:
        print(f"   {c['symbol']:8} +{c['change']:.2f}% → Hedef: +25%")
    
    print("\n💻 STRONG_BUY HİSSE:")
    for s in [x for x in data['stocks'] if x['recommendation'] == 'STRONG_BUY'][:3]:
        print(f"   {s['symbol']:8} +{s['change']:.2f}% → Hedef: +20%")
    
    # Try to send to Telegram
    print("\n📱 Telegram'a gönderiliyor...")
    msg = format_telegram_message(data)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and len(token) > 20:
        if send_to_telegram(msg):
            print("✅ Telegram'a gönderildi!")
        else:
            print("⚠️ Telegram gönderilemedi (bot offline?)")
    else:
        print("⚠️ Token yoktur - test modunda")
    
    print("\n🎯 Sistem hazır!")
    print("   Telegram'da /btc yazın")
    print("   Dashboard'da analiz görürsünüz")

if __name__ == "__main__":
    initialize_btc_system()

