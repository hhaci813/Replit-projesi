import json
import os
import requests
from datetime import datetime

print("🤖 YATIRIM ASİSTANI - AŞAMA 2")
print("=" * 50)

# Basit veri saklama
def verileri_yukle():
    try:
        with open('veriler.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        baslangic_verisi = {
            "portfoy": {},
            "ogrenilenler": [],
            "son_guncelleme": str(datetime.now())
        }
        verileri_kaydet(baslangic_verisi)
        return baslangic_verisi

def verileri_kaydet(veriler):
    with open('veriler.json', 'w', encoding='utf-8') as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)

# Fiyat sorgulama fonksiyonları
def hisse_fiyati_al(sembol):
    """Hisse fiyatını al"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sembol}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            fiyat = data['chart']['result'][0]['meta']['regularMarketPrice']
            return fiyat
        return None
    except:
        return None

def kripto_fiyati_al(sembol):
    """Kripto fiyatını al"""
    try:
        # Örnek kriptolar için basit eşleme
        kripto_eslestirme = {
            "BTC": "bitcoin",
            "ETH": "ethereum", 
            "ADA": "cardano",
            "DOT": "polkadot",
            "DOGE": "dogecoin"
        }
        
        kripto_id = kripto_eslestirme.get(sembol, sembol.lower())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={kripto_id}&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data[kripto_id]['usd']
        return None
    except:
        return None

def fiyat_sorgula(sembol, tip):
    """Sembolün fiyatını sorgula"""
    if tip == "hisse":
        return hisse_fiyati_al(sembol)
    elif tip == "kripto":
        return kripto_fiyati_al(sembol)
    else:
        return None

# Ana program
def main():
    veriler = verileri_yukle()
    
    print("✅ Sistem hazır! Portföyünüzde", len(veriler["portfoy"]), "yatırım var.")
    
    while True:
        print("\n" + "="*50)
        print("NE YAPMAK İSTERSİNİZ?")
        print("1 - Portföyü Görüntüle (Güncel Fiyatlarla)")
        print("2 - Yatırım Ekle") 
        print("3 - Yatırım Sil")
        print("4 - Fiyat Sorgula")
        print("5 - Çıkış")
        print("="*50)
        
        secim = input("Seçiminiz (1-5): ").strip()
        
        if secim == "1":
            print("\n💼 PORTFÖYÜNÜZ (Güncel Fiyatlarla):")
            if not veriler["portfoy"]:
                print("Portföyünüz boş")
            else:
                toplam_kar_zarar = 0
                toplam_yatirim = 0
                
                for sembol, bilgi in veriler["portfoy"].items():
                    tip = bilgi.get('tip', 'hisse')
                    adet = bilgi['adet']
                    maliyet = bilgi['maliyet']
                    
                    # Güncel fiyatı al
                    guncel_fiyat = fiyat_sorgula(sembol, tip)
                    
                    if guncel_fiyat:
                        guncel_deger = guncel_fiyat * adet
                        yatirim_degeri = maliyet * adet
                        kar_zarar = guncel_deger - yatirim_degeri
                        kar_zarar_yuzde = (kar_zarar / yatirim_degeri) * 100
                        
                        toplam_kar_zarar += kar_zarar
                        toplam_yatirim += yatirim_degeri
                        
                        durum = "🟢" if kar_zarar >= 0 else "🔴"
                        print(f"{durum} {sembol} ({tip}):")
                        print(f"   Adet: {adet}")
                        print(f"   Maliyet: ${maliyet:.2f}")
                        print(f"   Güncel: ${guncel_fiyat:.2f}")
                        print(f"   Kar/Zarar: ${kar_zarar:.2f} (%{kar_zarar_yuzde:.2f})")
                        print()
                    else:
                        print(f"❓ {sembol}: Fiyat bilgisi alınamadı")
                
                if toplam_yatirim > 0:
                    print(f"📊 TOPLAM DURUM:")
                    print(f"   Toplam Yatırım: ${toplam_yatirim:.2f}")
                    print(f"   Toplam Kar/Zarar: ${toplam_kar_zarar:.2f}")
                    getiri_orani = (toplam_kar_zarar / toplam_yatirim) * 100
                    print(f"   Getiri Oranı: %{getiri_orani:.2f}")
                    
        elif secim == "2":
            print("\n➕ YENİ YATIRIM EKLE")
            sembol = input("Sembol (Örnek: AAPL, BTC): ").upper()
            tip = input("Tip (hisse/kripto): ").lower()
            adet = float(input("Adet: "))
            maliyet = float(input("Maliyet ($): "))
            
            # Fiyat kontrolü
            guncel_fiyat = fiyat_sorgula(sembol, tip)
            if guncel_fiyat:
                print(f"💰 Güncel fiyat: ${guncel_fiyat:.2f}")
            
            veriler["portfoy"][sembol] = {
                "tip": tip,
                "adet": adet,
                "maliyet": maliyet,
                "tarih": str(datetime.now())
            }
            veriler["son_guncelleme"] = str(datetime.now())
            verileri_kaydet(veriler)
            print(f"✅ {sembol} portföye eklendi!")
            
        elif secim == "3":
            print("\n🗑️ YATIRIM SİL")
            sembol = input("Silinecek sembol: ").upper()
            if sembol in veriler["portfoy"]:
                del veriler["portfoy"][sembol]
                verileri_kaydet(veriler)
                print(f"✅ {sembol} portföyden silindi!")
            else:
                print("❌ Bu sembol portföyde bulunamadı")
                
        elif secim == "4":
            print("\n💰 FİYAT SORGULA")
            sembol = input("Sembol: ").upper()
            tip = input("Tip (hisse/kripto): ").lower()
            
            fiyat = fiyat_sorgula(sembol, tip)
            if fiyat:
                print(f"💰 {sembol} güncel fiyat: ${fiyat:.2f}")
            else:
                print(f"❌ {sembol} fiyatı alınamadı")
                
        elif secim == "5":
            print("👋 Güle güle! Verileriniz kaydedildi.")
            break
            
        else:
            print("❌ Geçersiz seçim! 1-5 arası bir sayı girin.")

# Programı başlat
if __name__ == "__main__":
    main()
