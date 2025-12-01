"""Send detailed dashboard to Telegram"""
from telegram_service import TelegramService
import json

def send_dashboard_telegram():
    """Send formatted dashboard to Telegram"""
    try:
        from btcturk_market_scanner import BTCTurkMarketScanner
        scanner = BTCTurkMarketScanner()
        data = scanner.analyze_all()
        
        assets = []
        if isinstance(data, list):
            assets = data
        elif isinstance(data, dict) and 'assets' in data:
            assets = data['assets']
        
        rising = [a for a in assets if a.get('change', 0) > 0]
        falling = [a for a in assets if a.get('change', 0) < 0]
        
        # Build message
        msg = """
╔════════════════════════════════════════╗
║  🤖 AKILLI YATIRIM ASİSTANI            ║
║     DETAYLI MARKET ANALIZI             ║
╚════════════════════════════════════════╝

📊 1️⃣ PORTFÖY DAĞILIMI (Nasıl Bölmeliyiz?)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🪙 Kripto: %40
  💻 Teknoloji: %30
  📈 Hisse Senedi: %30

📈 2️⃣ KRİPTO BÜYÜME POTANSİYELİ (6 Aylık Trend)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🟠 Bitcoin: 100 → 145 (+45%)
  🔵 Ethereum: 100 → 150 (+50%)

⚠️ 3️⃣ RİSK vs GETİRİ DENGESİ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🟢 Devlet Tahvili: Risk 2/10 → Return %8
  🔵 AAPL: Risk 5/10 → Return %15
  🟠 Bitcoin: Risk 8/10 → Return %25
  🔴 Penny Stock: Risk 10/10 → Return %25

💹 CANLI FİYATLAR - EN YÜKSELENLER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        top_rising = sorted(rising, key=lambda x: x.get('change', 0), reverse=True)[:5]
        for asset in top_rising:
            symbol = asset.get('symbol', 'N/A')
            price = asset.get('price', 0)
            change = asset.get('change', 0)
            msg += f"  ✅ {symbol:8} ₺{price:>10.0f}  +{change:>6.2f}%\n"
        
        msg += "\n⚠️ CANLI FİYATLAR - EN DÜŞENLER\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        top_falling = sorted(falling, key=lambda x: x.get('change', 0))[:5]
        for asset in top_falling:
            symbol = asset.get('symbol', 'N/A')
            price = asset.get('price', 0)
            change = asset.get('change', 0)
            msg += f"  📉 {symbol:8} ₺{price:>10.0f}  {change:>6.2f}%\n"
        
        msg += """
📋 YENİ BAŞLAYAN İÇİN 5 KURAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1️⃣ BAŞLA: Küçük miktar (100-1000)
     💡 Panik yapma, öğren!

  2️⃣ DIVERSİFİKE: 5+ farklı yatırım
     💡 Tüm yumurtaları bir sepete koyma!

  3️⃣ STOP LOSS SET: -5% kaybına çık
     💡 Zarar sınırla, risk al!

  4️⃣ LONG TERM: Min 6-12 ay tut
     💡 Günlük ticarete girme!

  5️⃣ ÖĞREN: Haberler oku, grafik anla
     💡 Bilgili ol, duyguşal karar verme!

⚠️ HATIRLAT:
Hızlı para kazanmak = Kolaylı para kaybetmek
Yavaş, güvenli, tutarlı kazansamna! 🚀

╔════════════════════════════════════════╗
║  Dashboard: http://localhost:5000/    ║
║  Analiz: Her 30 dakika güncelleme     ║
║  ADA Tracking: Günlük rapor           ║
╚════════════════════════════════════════╝
"""
        
        telegram = TelegramService()
        telegram._send_message(msg)
        print("✅ Detaylı dashboard Telegram'a gönderildi")
        return True
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    send_dashboard_telegram()
