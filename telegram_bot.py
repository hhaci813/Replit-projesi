"""Telegram Bot Entegrasyonu - Yatırım Tavsiyelerini Telegram'a Gönder"""
import requests
import json
from datetime import datetime

class TelegramBot:
    """Telegram Bot API entegrasyonu"""
    
    def __init__(self, bot_token=None):
        """
        Bot tokeni ayarla
        Token format: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
        """
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None
        self.yapilan_gonderimler = []
    
    @staticmethod
    def token_gecerliligi_kontrol(token):
        """Token geçerliliğini kontrol et"""
        if not token or ":" not in token:
            return False, "❌ Geçersiz token formatı"
        
        try:
            # Test mesajı gönder
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True, "✅ Token geçerli!"
            else:
                return False, "❌ Token reddedildi"
        except:
            return False, "❌ Bağlantı hatası"
    
    def sohbet_id_al(self):
        """Kullanıcının Telegram chat ID'sini al"""
        print("\n📱 TELEGRAM SOHBET ID'İ ALMAK İÇİN:")
        print("1. @BotFather'a Telegram'da yazın")
        print("2. /start yazın, ardından /newbot")
        print("3. Bot adını girin (örn: YatırımAsistanıBot)")
        print("4. Bot kullanıcı adını girin (örn: yatirim_bot)")
        print("5. Token'ı alacaksınız (örn: 123456:ABC-DEF...)")
        print("\n6. Sonra @YourBotUsername'e yazın ve /start'a tıklayın")
        print("7. Alınan chat_id'yi aşağıda girin\n")
        
        chat_id = input("Telegram Chat ID (sadece sayı): ").strip()
        return chat_id
    
    def tavsiye_gonder(self, chat_id, tavsiye_metni):
        """Tavsiye mesajını Telegram'a gönder"""
        if not self.bot_token or not chat_id:
            return {"status": "error", "mesaj": "❌ Token veya Chat ID eksik"}
        
        try:
            url = f"{self.base_url}/sendMessage"
            
            mesaj = f"""
🤖 YAPAY ZEKA YATIRIM TAVSİYESİ

{tavsiye_metni}

🔐 Gönderme Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
            """
            
            data = {
                "chat_id": chat_id,
                "text": mesaj,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                self.yapilan_gonderimler.append({
                    "tarih": datetime.now().isoformat(),
                    "chat_id": chat_id,
                    "durum": "BAŞARILI"
                })
                return {"status": "success", "mesaj": "✅ Telegram'a gönderildi!"}
            else:
                return {"status": "error", "mesaj": f"❌ Hata: {response.text}"}
        
        except Exception as e:
            return {"status": "error", "mesaj": f"❌ Bağlantı hatası: {str(e)}"}
    
    def gunluk_tavsiye_gonder(self, chat_id):
        """Günlük tavsiye gönder"""
        tavsiye = """
💼 BUGÜNÜN DENGELI PORTFÖY ÖNERİSİ:

60% Hisse Senedi:
🟢 AAPL: 20% - AL
🟢 MSFT: 20% - AL
🟢 GOOGL: 20% - AL

30% Teknoloji:
🟡 TSLA: 15% - TUT
🟡 AMZN: 15% - TUT

10% Kripto:
🟢 BTC: 6% - AL
🟡 ETH: 4% - TUT

⚠️ RİSK KURALLARI:
• Zarar durdurma: -5%
• Kar al: +20%
• Min 5 sembol diversifikasyonu
        """
        
        return self.tavsiye_gonder(chat_id, tavsiye)
    
    def fiyat_bildirimi_gonder(self, chat_id, sembol, fiyat, degisim):
        """Fiyat değişim bildirimi gönder"""
        if degisim > 0:
            emoji = "📈"
            durum = "Yükselmekte"
        else:
            emoji = "📉"
            durum = "Düşmekte"
        
        mesaj = f"""
{emoji} {sembol} Fiyat Bildirimi

Fiyat: ${fiyat:.2f}
Değişim: {degisim:+.2f}%
Durum: {durum}

⏰ {datetime.now().strftime('%H:%M:%S')}
        """
        
        return self.tavsiye_gonder(chat_id, mesaj)
    
    def uyari_gonder(self, chat_id, uyari_metni):
        """Önemli uyarı gönder"""
        mesaj = f"""
🚨 ÖNEMLI UYARI

{uyari_metni}

⚠️ Lütfen hemen dikkat edin!
        """
        
        return self.tavsiye_gonder(chat_id, mesaj)
    
    def gonderim_gecmisini_goster(self):
        """Gönderilen mesajları göster"""
        print("\n📋 TELEGRAM GÖNDERME GEÇMİŞİ\n")
        
        if not self.yapilan_gonderimler:
            print("Henüz mesaj gönderilmedi")
            return
        
        for i, gonderi in enumerate(self.yapilan_gonderimler, 1):
            print(f"{i}. Chat ID: {gonderi['chat_id']} - {gonderi['durum']} ({gonderi['tarih']})")
    
    @staticmethod
    def demo_calistir():
        """Demo - Token olmadan göster"""
        print("\n" + "="*70)
        print("🤖 TELEGRAM BOT DEMO")
        print("="*70)
        
        print("\n✅ Telegram Bot Özellikleri:")
        print("   • Günlük yatırım tavsiyesi gönderme")
        print("   • Fiyat değişim bildirimleri")
        print("   • Önemli uyarılar")
        print("   • İşlem sonuçları")
        print("   • Portföy güncellemeleri")
        
        print("\n📱 Kurulum Adımları:")
        print("   1. @BotFather'a Telegram'da /newbot yaz")
        print("   2. Bot adı ve kullanıcı adı belirle")
        print("   3. Token'ı al (örn: 123456:ABC-DEF...)")
        print("   4. Sisteme token ver")
        print("   5. Chat ID ile mesaj almaya başla")
        
        print("\n💬 Gönderilecek Mesajlar:")
        print("   📈 Tavsiye: Günlük portföy önerisi")
        print("   💰 Fiyat: Real-time fiyat değişimleri")
        print("   🚨 Uyarı: Önemli pazar olayları")
        
        return True

if __name__ == "__main__":
    TelegramBot.demo_calistir()
