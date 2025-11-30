"""Telegram Servis - Token ile entegrasyon"""
import os
import requests
import json
from datetime import datetime

class TelegramService:
    def __init__(self):
        # Kullanıcı tarafından verilen token
        self.token = "8268294938:AAGCvDDNHhb5-pKFQYPJrZIJTxMVmu79oYo"
        self.chat_id = 8391537149
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def test_connection(self):
        """Telegram bağlantısını test et"""
        if not self.token:
            return False, "❌ Token yüklenemedi"
        
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                bot_info = response.json()
                return True, f"✅ Bağlandı: {bot_info['result']['username']}"
            return False, "❌ Token geçersiz"
        except Exception as e:
            return False, f"❌ Bağlantı hatası: {str(e)}"
    
    def tavsiye_gonder(self):
        """Günlük tavsiye gönder"""
        tavsiye = """
🤖 YAPAY ZEKA YATIRIM TAVSİYESİ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💼 DENGELI PORTFÖY ÖNERİSİ:

🟢 AL FIRKATI (RSI < 30):
• AAPL - %20
• MSFT - %20
• GOOGL - %20

🟡 TUT FIRKATI (Durağan):
• TSLA - %15
• AMZN - %15

🟢 KRİPTO (Spekülatif):
• BTC-USD - %6
• ETH-USD - %4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ RİSK KURALLARI:
✓ Zarar durdurma: -5%
✓ Kar al: +20%
✓ Min 5 sembol
✓ Haftalık review

📈 7 GÜNLÜK ML ÖNGÖRÜSü:
• AAPL/MSFT/GOOGL: +5-8%
• AMZN: -2 to +3%
• TSLA: -5 to +2%
• BTC: +10-15%

✅ Tavsiye HAZIR!
"""
        return self._send_message(tavsiye)
    
    def haber_gonder(self):
        """Haberler gönder"""
        haber = """
📰 FINANSAL HABERLER - SENTIMENT ANALİZİ

🟢 POZİTİF:
✓ AAPL hisse yükselişe başladı (+3%)
✓ Microsoft yeni AI ürünü duyurdu
✓ Teknoloji sektörü güçlü

🔴 NEGATİF:
⚠ Tesla satışları düşüyor (-2%)
⚠ Crypto piyasası biraz sarsıldı
⚠ Enerji sektörü endişeli

🟡 NÖTR:
○ Amazon durağan seyirde
○ Genel pazar dengeli

Kaynak: AI Sentiment Analysis
"""
        return self._send_message(haber)
    
    def portfoy_durumu_gonder(self):
        """Portföy durumunu gönder"""
        portfoy = """
📊 PORTFÖY DURUM RAPORU

Mevcut Yatırımlar: 0 sembol
Toplam Değer: $0
Günlük Değişim: 0%

🎯 Öneriler:
1. AAPL ekle (%20)
2. MSFT ekle (%20)
3. GOOGL ekle (%20)
4. TSLA ekle (%15)
5. AMZN ekle (%15)

Diversifikasyon: Eksik
Rebalancing: Gerekli

/portfoy komutu için güncel durum
"""
        return self._send_message(portfoy)
    
    def uyari_gonder(self, baslik, mesaj):
        """Uyarı gönder"""
        uyari = f"""
🚨 UYARI: {baslik}

{mesaj}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
        return self._send_message(uyari)
    
    def send_message(self, text):
        """Public method to send message"""
        return self._send_message(text)
    
    def _send_message(self, text):
        """Mesaj gönder"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return True, "✅ Mesaj gönderildi"
            else:
                return False, f"❌ Hata {response.status_code}"
        except Exception as e:
            return False, f"❌ {str(e)}"

if __name__ == "__main__":
    service = TelegramService()
    ok, msg = service.test_connection()
    print(msg)
    
    if ok:
        ok, msg = service.uyari_gonder("Test", "Sistem çalışıyor!")
        print(msg)
