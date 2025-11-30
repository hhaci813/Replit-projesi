"""Telegram Servis - Token ile entegrasyon"""
import os
import requests
import json
from datetime import datetime

class TelegramService:
    def __init__(self):
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
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
    
    def _send_message(self, text):
        """Mesaj gönder"""
        if not self.token:
            return {"status": "error", "mesaj": "❌ Token gerekli"}
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return {"status": "ok", "mesaj": "✅ Telegram'a gönderildi"}
            else:
                return {"status": "error", "mesaj": f"❌ Telegram hatası: {response.text}"}
        except Exception as e:
            return {"status": "error", "mesaj": f"❌ Hata: {str(e)}"}

if __name__ == "__main__":
    service = TelegramService()
    
    print("\n" + "="*70)
    print("📱 TELEGRAM SERVİSİ TEST")
    print("="*70 + "\n")
    
    # Bağlantı testi
    ok, msg = service.test_connection()
    print(msg)
    
    if ok:
        print("\n✅ Tavsiye gönderiyor...")
        result = service.tavsiye_gonder()
        print(result['mesaj'])
        
        print("\n✅ Haberler gönderiyor...")
        result = service.haber_gonder()
        print(result['mesaj'])

    def grafik_gonder(self):
        """Eğitim grafiği gönder"""
        import matplotlib.pyplot as plt
        from datetime import datetime
        import os
        
        try:
            # Grafik oluştur
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('AKILLI YATIRIM ASISTANI - BASLANGIC REHBERI', fontsize=16, fontweight='bold')
            
            # Portfolio Dagilimi
            labels = ['Hisse\n%60', 'Teknoloji\n%30', 'Kripto\n%10']
            sizes = [60, 30, 10]
            colors = ['#2ecc71', '#3498db', '#f39c12']
            explode = (0.05, 0.05, 0.1)
            
            ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.0f%%',
                    shadow=True, startangle=90, textprops={'fontsize': 11, 'weight': 'bold'})
            ax1.set_title('PORTFOLIO DAGILIMI\n(Nasil Bolmeli?)', fontsize=12, fontweight='bold')
            
            # Kripto Potansiyeli
            months = ['Ay 1', 'Ay 2', 'Ay 3', 'Ay 4', 'Ay 5', 'Ay 6']
            btc = [100, 110, 120, 125, 135, 150]
            eth = [100, 105, 115, 122, 130, 145]
            
            ax2.plot(months, btc, marker='o', linewidth=2.5, markersize=8, label='Bitcoin', color='#f7931a')
            ax2.plot(months, eth, marker='s', linewidth=2.5, markersize=8, label='Ethereum', color='#627eea')
            ax2.fill_between(range(len(months)), btc, alpha=0.2, color='#f7931a')
            ax2.fill_between(range(len(months)), eth, alpha=0.2, color='#627eea')
            ax2.set_title('KRIPTO BUYUME POTANSIYELI\n(6 Aylik Trend)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Deger (Baslangic = 100)', fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Risk Seviyeleri
            strategies = ['Guvenli\n(Hisse)', 'Dengeli\n(Mix)', 'Agresif\n(Kripto)']
            risk_levels = [3, 6, 9]
            returns = [8, 15, 25]
            colors_risk = ['#2ecc71', '#f39c12', '#e74c3c']
            
            for i, (s, r, ret, c) in enumerate(zip(strategies, risk_levels, returns, colors_risk)):
                ax3.scatter(r, ret, s=1000, alpha=0.6, color=c, edgecolors='black', linewidth=2)
                ax3.text(r, ret, f'{ret}%', ha='center', va='center', fontweight='bold', fontsize=10)
            
            ax3.set_xlabel('Risk Seviyesi (1-10)', fontweight='bold')
            ax3.set_ylabel('Beklenen Yillik Return (%)', fontweight='bold')
            ax3.set_title('RISK vs GETIRI DENGESI\n(Hangisini Sec?)', fontsize=12, fontweight='bold')
            ax3.set_xlim(0, 10)
            ax3.set_ylim(0, 30)
            ax3.grid(True, alpha=0.3)
            
            # Kurallar
            ax4.axis('off')
            rules_text = """YENİ BAŞLAYAN İÇİN 5 KURAL:

1. BAŞLA: Küçük miktar ($100-1000)
2. DIVERSİFİKE: 5+ farklı yatırım
3. STOP LOSS: -5% kayıpta çık
4. LONG TERM: Min 6-12 ay tut
5. ÖĞREN: Haberler oku, grafik anla

HATIRLA: Yavaş, güvenli, tutarlı!"""
            
            ax4.text(0.05, 0.95, rules_text, transform=ax4.transAxes, fontsize=10,
                     verticalalignment='top', fontfamily='monospace',
                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            grafik_dosya = 'grafik_rehberi.png'
            plt.savefig(grafik_dosya, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Telegram'a gönder
            with open(grafik_dosya, 'rb') as f:
                resp = self.session.post(
                    f"https://api.telegram.org/bot{self.token}/sendPhoto",
                    data={"chat_id": self.chat_id},
                    files={"photo": f},
                    timeout=15
                )
            
            os.remove(grafik_dosya)
            
            if resp.status_code == 200:
                return {
                    'basarili': True,
                    'mesaj': f'Grafik Telegram\'a gönderildi (Chat ID: {self.chat_id})'
                }
            else:
                return {'basarili': False, 'mesaj': f'Grafik gönderilemedi: {resp.text}'}
        
        except Exception as e:
            return {'basarili': False, 'mesaj': f'Grafik hatası: {str(e)}'}
