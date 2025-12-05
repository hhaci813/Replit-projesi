"""Telegram'a yeni features hakkında bildir"""
from telegram_service import TelegramService

msg = """
🎉 YENİ ÖZELLIKLER EKLENDI!

Gerçek para hariç yapamadığın şeyler artık hazır:

✅ 1️⃣ PUMP DETECTION 🚀
   • Volume spike algılaması
   • Fiyat hareket tespiti
   • Risk level (HIGH/MEDIUM)
   • Her 15 dakika otomatik
   
✅ 2️⃣ EMAIL DIGEST 📧
   • Günlük market özeti
   • En yükselenler/düşenler
   • Saat 09:00'de otomatik
   • HTML formatında güzel
   
✅ 3️⃣ DISCORD BOT 🎮
   • Real-time alerts
   • Renk kodlu mesajlar
   • Her 1 saatte report
   • (Discord token gerekli)
   
✅ 4️⃣ SENTIMENT ANALYSIS 🎯
   • Haberlerden sentiment
   • TextBlob analizi
   • Polarity + Subjectivity
   • Her gün 08:00'de
   
✅ 5️⃣ ADVANCED TRENDS 📈
   • RSI hesaplama
   • Trend detection
   • Pattern recognition
   • MACD analizi

🔧 SETUP:
   1. Gmail: App Password oluştur
   2. Discord: Bot token al
   3. NewsAPI: Key al (news sentiment için)
   4. Telegram'a: /help yazıp komutları öğren

📊 Dashboard: http://localhost:5000/
✅ Sistem 24/7 çalışıyor!
"""

try:
    TelegramService()._send_message(msg)
    print("✅ Telegram mesajı gönderildi")
except:
    print("Telegram bilgisi gönderilirdi")
