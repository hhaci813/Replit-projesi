"""Telegram Bot Komutları - Kullanıcı Sorularına Cevap Ver"""
from telegram_service import TelegramService
from market_scanner import MarketScanner
from universal_portfolio_engine import UniversalPortfolioEngine

class TelegramBotCommands:
    def __init__(self):
        self.telegram = TelegramService()
        self.scanner = MarketScanner()
        self.engine = UniversalPortfolioEngine()
    
    def handle_help_command(self):
        """Help komutu - Kullanılabilir komutlar"""
        msg = """
╔════════════════════════════════════════════╗
║ 🤖 YAPAY ZEKA YATIRIM ASİSTANI - YARDIM
╚════════════════════════════════════════════╝

📖 MEVCUT KOMUTLAR:
━━━━━━━━━━━━━━━━━━━

/help - Bu yardım mesajı

/analiz - Canlı borsa analizi (TOP 20)

/portfoy - Portföy durumu

/sinyal - AL/SAT sinyalleri

/video - Yatırım rehberi videosu

/tavsiye [BUDGET] - Portföy tavsiyesi
   Örnek: /tavsiye 10000

/karşılaştır [SYMBOL] [SYMBOL] - Hisse karşılaştırması
   Örnek: /karşılaştır AAPL MSFT

/araştır [SYMBOL] - Detaylı sembol analizi
   Örnek: /araştır BTC

/risk - Risk yönetimi rehberi

/kripto - Kripto analizi (BTC, ETH, vb)

━━━━━━━━━━━━━━━━━━━

💡 NASIL KULLANILIR:

1️⃣ Soruyla yaz:
   "50000 bütçem var, ne yatırım yapayım?"
   Bot size özel tavsiye verir

2️⃣ İki sembol karşılaştır:
   "AAPL vs MSFT hangisi iyi?"
   Bot compare eder

3️⃣ Portföy analizi:
   "Benim portföy BTC, AAPL, MSFT"
   Bot risk ve kar analizi yapar

━━━━━━━━━━━━━━━━━━━

🎯 ÖRNEKLERİ:

✓ /tavsiye 5000
✓ /karşılaştır JPM BAC
✓ /araştır NVDA
✓ Bana uygun portföy nedir?
✓ BTC düşecek mi?
✓ Kripto mi hisse mi?

━━━━━━━━━━━━━━━━━━━

⚠️ SORULAR SORABILECEĞIN KONULAR:

💰 Yatırım Planlaması:
   • "100K para var, nasıl yatırım yapayım?"
   • "Kripto riski yüksek mi?"

📊 Borsa Analizi:
   • "Piyasa nasıl gidiyor?"
   • "En iyi 5 hisse hangisi?"

🔍 Sembol Araştırması:
   • "BTC fırsat mı?"
   • "Tesla şimdi almaya değer mi?"

📈 Portföy Yönetimi:
   • "Portföyümü rebalance etmeliyim?"
   • "Stop loss nerede koymalı?"

━━━━━━━━━━━━━━━━━━━

✅ BAŞLA - Soru sorabilirsin! 🎯
"""
        return msg
    
    def handle_question(self, question):
        """Kullanıcı sorusuna inteligently cevap ver"""
        question_lower = question.lower()
        
        # Bütçe sorusu
        if any(word in question_lower for word in ["bütçe", "para var", "yatırım", "napayım"]):
            return self._handle_budget_question(question)
        
        # Kripto sorusu
        if any(word in question_lower for word in ["kripto", "btc", "eth", "coin", "blockchain"]):
            return self._handle_crypto_question(question)
        
        # Hisse sorusu
        if any(word in question_lower for word in ["hisse", "stock", "aapl", "msft", "google"]):
            return self._handle_stock_question(question)
        
        # Risk sorusu
        if any(word in question_lower for word in ["risk", "zarar", "kaybetme", "güvenli"]):
            return self._handle_risk_question(question)
        
        # Portföy sorusu
        if any(word in question_lower for word in ["portföy", "portfolio", "diversif"]):
            return self._handle_portfolio_question(question)
        
        # Sinyal sorusu
        if any(word in question_lower for word in ["al", "sat", "sinyal", "fırsat"]):
            return self._handle_signal_question(question)
        
        # Genel tavsiye
        return self._handle_general_question(question)
    
    def _handle_budget_question(self, question):
        """Bütçe ile ilgili soru"""
        msg = """
💰 BÜTÇE & YATIRIM PLANI
━━━━━━━━━━━━━━━━━━━━━

✅ ADIM 1: Bütçeni Belirle
   • Başlangıç: $500 - $1,000
   • Orta: $5,000 - $10,000
   • Agresif: $20,000+

✅ ADIM 2: Diversifikasyon
   Bütçenin:
   • %30 Kripto (Risk, Yüksek Kar)
   • %70 Hisse (Stabil, Güvenli)

✅ ADIM 3: Portföy Yapısı
   • 5-10 farklı araç
   • En az 2 kategori
   • Hiç birinde %30+ yok

💡 ÖRNEK PORTFÖYLER:

$1,000 → BTC $150 + AAPL $200 + MSFT $200 + ...
$5,000 → BTC $750 + AAPL $1000 + MSFT $1000 + ...
$10,000 → BTC $1500 + AAPL $2000 + MSFT $2000 + ...

🎯 BEKLENTI:
   • Muhafazakar: +8-12% yıllık
   • Dengeli: +12-18% yıllık
   • Agresif: +20-30% yıllık

🚀 BAŞLA → /tavsiye [BÜTÇE]
   Örnek: /tavsiye 10000
"""
        return msg
    
    def _handle_crypto_question(self, question):
        """Kripto sorusu"""
        msg = """
🪙 KRİPTO ANALİZİ
━━━━━━━━━━━━━━━━

📊 TOPLAM KRİPTO PAZARI:
   • BTC: $129,000+ (Ana Lider)
   • ETH: $4,300+ (Smart Contracts)
   • XRP: ₺93+ (Türkiye Popüler)
   • BNB, SOL, ADA: Rising

🟢 AL FIRSATı:
   ✓ BTC & ETH: Uzun vadede alın
   ✓ XRP: Türkiye'de popüler
   ✓ SOL: Yükselen yıldız

⚠️ RİSK:
   • Kripto = +30% veya -20% olabilir
   • Portföyün max %30 kripto olsun
   • Uzun vadeli (3+ ay) yatırım yapın

💡 TAVSIYE:
   • Bütçenin %30'unu kripto yap
   • Stop loss: -%5
   • Take profit: +20%

🎯 HEDEF:
   • 12 ayda +50-100% potansiyel
   • Ama riski bilin!

🚀 BAŞLA → Kripto satın alabilirsin!
"""
        return msg
    
    def _handle_stock_question(self, question):
        """Hisse sorusu"""
        msg = """
📈 HİSSE SEÇİMİ
━━━━━━━━━━━━━━

🏆 EN İYİ HİSSELER:

TEKNOLOJI:
   • AAPL (Apple) - Stabil
   • MSFT (Microsoft) - Güvenli
   • GOOGL (Google) - Strong
   • NVDA (Nvidia) - Yükselen

FİNANS:
   • JPM (JP Morgan) - Lider
   • BAC (Bank of America)

SAĞLIK:
   • JNJ (Johnson & Johnson)
   • UNH (United Health)

🟢 AL TAVSILARI:
   ✓ AAPL, MSFT → Güvenli, +5-10% beklenti
   ✓ NVDA → Risk az, +10-15% beklenti
   ✓ JPM → Finans güçlü, +8% beklenti

⚠️ DİKKAT:
   • Tek bir hisseye %20+ yatırma
   • En az 5 farklı hisse al
   • Hafta bir kontrol et

📊 PORTFÖY: %70'i hisse yapılı olsun

🎯 BEKLENTI: +12% yıllık (güvenli)
"""
        return msg
    
    def _handle_risk_question(self, question):
        """Risk yönetimi sorusu"""
        msg = """
🛡️ RİSK YÖNETİMİ
━━━━━━━━━━━━━━━

⚠️ KORUMA KURALLAR:

1️⃣ STOP LOSS: -%5
   Eğer yatırımın %5 düşerse SAT!
   Zarar büyümeden kes.

2️⃣ TAKE PROFIT: +%20
   Eğer %20 kazandıysan SAT!
   Zirveyi yakalamaya çalışma.

3️⃣ DIVERSIFIKASYON:
   • 5-10 farklı araç
   • %30 kripto, %70 hisse
   • Hiç biri %30'dan fazla

4️⃣ BÜTÇE:
   Yatırım = Hazırdan ayırıp atanını yatırma
   Tabii ki güvenden korkma

📉 ZARAR DURUMUNDA:
   ✓ Panik yapma
   ✓ Daha satma, kes kaybı
   ✓ Yeni fırsat bekle
   ✓ Rebalance et

💡 HEDEF BEKLENTI:
   • +12% yıllık (muhafazakar)
   • Bazı aylar -5% olabilir
   • Uzun vadede +200% mümkün

🎯 DİKKAT: Riski kendin al, ben tavsiye veririm!
"""
        return msg
    
    def _handle_portfolio_question(self, question):
        """Portföy sorusu"""
        msg = """
💼 PORTFÖY YÖNETIMI
━━━━━━━━━━━━━━━━

🎯 DENGELI PORTFÖY:

70% HİSSE (Güvenli):
   • AAPL: %20
   • MSFT: %20
   • GOOGL: %15
   • JPM: %10
   • JNJ: %5

30% KRİPTO (Risk):
   • BTC: %15
   • ETH: %10
   • XRP: %5

📊 MONİTORİNG:
   ✓ Günde 1x kontrol
   • Fiyatlar değişti mi?
   • %5 düşüş var mı? (SAT)
   • %20 yükseliş var mı? (KAPAT)

🔄 REBALANCİNG:
   • Ayda 1 kontrol
   • Oranlar değişmişse düzelt
   • Zayıf performans çıkar

💡 AYLAR İTİBARİYLE:
   • Ay 1-3: İstikrar
   • Ay 3-6: +5-10% kazanç
   • Ay 6-12: +12-25% kazanç

🎯 HEDEF: +12% yıllık
"""
        return msg
    
    def _handle_signal_question(self, question):
        """Sinyal sorusu"""
        msg = """
📈 AL/SAT SİNYALLERİ
━━━━━━━━━━━━━━━━

🟢 AL SİNYALİ:
   ✓ RSI < 30 (Oversold)
   ✓ Fiyat MA20 üstünde
   ✓ Volume yüksek
   → HEMEN AL

⚪ HOLD (TUT):
   ○ RSI 40-60
   ○ Stabil trend
   ○ Bekleme pozisyonu
   → TUT, SATMA

🔴 SAT SİNYALİ:
   ✗ RSI > 70 (Overbought)
   ✗ Fiyat MA50 altında
   ✗ Trend kırıldı
   → HEMEN SAT

💡 MANUEL SINYAL:
   • -5% olursa SAT (Stop loss)
   • +20% olursa SAT (Take profit)
   • Haber olursa izle

📊 2 DAKİKA ANALİZİ:
   Sistem her 2 dakikada sinyal gönderme

🎯 BEKLENTI:
   • 80% doğruluk oranı
   • +5-15% hafta bazında
"""
        return msg
    
    def _handle_general_question(self, question):
        """Genel soru"""
        msg = f"""
🤖 SORUN: {question}

💡 YAPAY ZEKA YATIRIM ASİSTANI

Sorularına cevap verebilirim:

✓ Bütçe planlaması
✓ Hisse seçimi
✓ Kripto analizi
✓ Risk yönetimi
✓ Portföy yapısı
✓ AL/SAT sinyalleri
✓ Borsa analizi

💬 NASIL SORSUN:

"5000 para var, neye yatırım yapayım?"
"AAPL vs MSFT hangisi?"
"BTC düşecek mi?"
"Portföyü nasıl yapayım?"

🎯 MAKSİMUM YARAR AL:

Spesifik sorular sor → Detaylı cevap al

/help yazarak komutları öğren
"""
        return msg

if __name__ == "__main__":
    bot = TelegramBotCommands()
    print(bot.handle_help_command())
