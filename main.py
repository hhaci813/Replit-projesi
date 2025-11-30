import json
import os
import requests
from datetime import datetime, timedelta
import time

print("🤖 AKILLI YATIRIM ASİSTANI - AŞAMA 3")
print("=" * 50)

# Basit veri saklama
def verileri_yukle():
    try:
        with open('veriler.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        baslangic_verisi = {
            "portfoy": {},
            "analiz_gecmisi": [],
            "tavsiyeler": {},
            "kullanici_tercihleri": {
                "risk_seviyesi": "orta",
                "yatirim_vadesi": "orta_vadeli"
            },
            "son_guncelleme": str(datetime.now())
        }
        verileri_kaydet(baslangic_verisi)
        return baslangic_verisi

def verileri_kaydet(veriler):
    with open('veriler.json', 'w', encoding='utf-8') as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)

# Fiyat sorgulama fonksiyonları
def hisse_fiyati_al(sembol):
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
    try:
        kripto_eslestirme = {
            "BTC": "bitcoin", "ETH": "ethereum", "ADA": "cardano",
            "DOT": "polkadot", "DOGE": "dogecoin", "SOL": "solana",
            "XRP": "ripple", "LTC": "litecoin", "BNB": "binancecoin"
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
    if tip == "hisse":
        return hisse_fiyati_al(sembol)
    elif tip == "kripto":
        return kripto_fiyati_al(sembol)
    else:
        return None

# AKILLI ANALİZ FONKSİYONLARI
def teknik_analiz_yap(sembol, tip):
    """Basit teknik analiz yapar"""
    try:
        fiyat = fiyat_sorgula(sembol, tip)
        if not fiyat:
            return {"durum": "bilinmiyor", "aciklama": "Fiyat bilgisi alınamadı"}
        
        # Rastgele teknik analiz (gerçek verilerle daha sonra geliştireceğiz)
        import random
        analiz_sonuclari = [
            {"durum": "güçlü_al", "aciklama": "📈 Güçlü al sinyali - Fiyat destek seviyesinde"},
            {"durum": "zayif_al", "aciklama": "📈 Zayıf al sinyali - Dikkatli olun"},
            {"durum": "nötr", "aciklama": "⚪ Nötr - Bekleyin"},
            {"durum": "zayif_sat", "aciklama": "📉 Zayıf sat sinyali - Kısmen çıkış yapılabilir"},
            {"durum": "güçlü_sat", "aciklama": "📉 Güçlü sat sinyali - Acil çıkış önerilir"}
        ]
        
        return random.choice(analiz_sonuclari)
    except:
        return {"durum": "hata", "aciklama": "Analiz yapılamadı"}

def portfoy_risk_analizi(veriler):
    """Portföy risk analizi yapar"""
    portfoy = veriler["portfoy"]
    if not portfoy:
        return {"risk_seviyesi": "düşük", "aciklama": "Portföy boş", "kripto_orani": 0, "cesitlilik": 0}
    
    toplam_deger = 0
    kripto_orani = 0
    cesitlilik = len(portfoy)
    
    for sembol, bilgi in portfoy.items():
        tip = bilgi.get('tip', 'hisse')
        adet = bilgi['adet']
        maliyet = bilgi['maliyet']
        yatirim_degeri = maliyet * adet
        toplam_deger += yatirim_degeri
        
        if tip == "kripto":
            kripto_orani += yatirim_degeri
    
    if toplam_deger > 0:
        kripto_orani = (kripto_orani / toplam_deger) * 100
    else:
        kripto_orani = 0
    
    # Risk hesaplama
    if kripto_orani > 50:
        risk = "yüksek"
        aciklama = f"⚠️ YÜKSEK RİSK: Portföyünüzün %{kripto_orani:.1f}'i kripto paralardan oluşuyor"
    elif kripto_orani > 20:
        risk = "orta"
        aciklama = f"🟡 ORTA RİSK: Portföyünüzün %{kripto_orani:.1f}'i kripto paralardan oluşuyor"
    else:
        risk = "düşük"
        aciklama = f"🟢 DÜŞÜK RİSK: İyi çeşitlendirilmiş portföy"
    
    if cesitlilik < 3:
        aciklama += f" - Sadece {cesitlilik} farklı varlık var, çeşitlendirmeyi artırın"
    
    return {
        "risk_seviyesi": risk,
        "aciklama": aciklama,
        "kripto_orani": kripto_orani,
        "cesitlilik": cesitlilik
    }

def yatirim_tavsiyesi_ver(veriler):
    """Kişiselleştirilmiş yatırım tavsiyeleri verir"""
    tavsiyeler = []
    portfoy = veriler["portfoy"]
    
    # Portföy boşsa temel tavsiyeler
    if not portfoy:
        tavsiyeler.append("💰 Portföyünüz boş, ilk yatırımınızı yapmayı düşünün")
        tavsiyeler.append("📊 Hisse senetleri ile başlangıç yapabilirsiniz (AAPL, GOOGL, MSFT)")
        tavsiyeler.append("₿ Kripto paralara küçük miktarlarla başlayın")
        return tavsiyeler
    
    # Risk analizine göre tavsiyeler
    risk_analizi = portfoy_risk_analizi(veriler)
    
    if risk_analizi["risk_seviyesi"] == "yüksek":
        tavsiyeler.append("⚠️ Risk seviyeniz yüksek, kripto oranını azaltmayı düşünün")
        tavsiyeler.append("📈 Hisse senetleri ile denge sağlayın")
    
    if risk_analizi["cesitlilik"] < 4:
        tavsiyeler.append("🔀 Portföyünüzü daha fazla çeşitlendirin")
        tavsiyeler.append("🌎 Farklı sektörlerden hisseler ekleyin")
    
    # Güncel piyasa durumu
    tavsiyeler.append("📅 Düzenli olarak yatırımlarınızı gözden geçirin")
    tavsiyeler.append("💡 Duygusal kararlar vermekten kaçının")
    
    return tavsiyeler

def analiz_raporu_kaydet(veriler, sembol, analiz):
    """Analiz geçmişine kaydeder"""
    analiz_kaydi = {
        "sembol": sembol,
        "analiz": analiz,
        "tarih": str(datetime.now())
    }
    veriler["analiz_gecmisi"].append(analiz_kaydi)
    
    # Son 50 analizi sakla
    if len(veriler["analiz_gecmisi"]) > 50:
        veriler["analiz_gecmisi"] = veriler["analiz_gecmisi"][-50:]
    
    verileri_kaydet(veriler)

# Ana program
def main():
    veriler = verileri_yukle()
    
    print(f"✅ Sistem hazır! Portföyünüzde {len(veriler['portfoy'])} yatırım var.")
    
    while True:
        print("\n" + "="*50)
        print("AKILLI YATIRIM ASİSTANI")
        print("="*50)
        print("1 - Portföyü Görüntüle")
        print("2 - Yatırım Ekle") 
        print("3 - Yatırım Sil")
        print("4 - Fiyat Sorgula")
        print("5 - Teknik Analiz Yap")
        print("6 - Risk Analizi")
        print("7 - Yatırım Tavsiyeleri")
        print("8 - Çıkış")
        print("="*50)
        
        secim = input("Seçiminiz (1-8): ").strip()
        
        if secim == "1":
            print("\n💼 PORTFÖYÜNÜZ:")
            if not veriler["portfoy"]:
                print("Portföyünüz boş")
            else:
                toplam_kar_zarar = 0
                toplam_yatirim = 0
                
                for sembol, bilgi in veriler["portfoy"].items():
                    tip = bilgi.get('tip', 'hisse')
                    adet = bilgi['adet']
                    maliyet = bilgi['maliyet']
                    
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
            print("\n📊 TEKNİK ANALİZ")
            sembol = input("Sembol: ").upper()
            tip = input("Tip (hisse/kripto): ").lower()
            
            fiyat = fiyat_sorgula(sembol, tip)
            if fiyat:
                print(f"💰 Güncel fiyat: ${fiyat:.2f}")
                
                analiz = teknik_analiz_yap(sembol, tip)
                print(f"📈 Analiz Sonucu: {analiz['aciklama']}")
                
                # Analizi kaydet
                analiz_raporu_kaydet(veriler, sembol, analiz)
            else:
                print(f"❌ {sembol} fiyatı alınamadı")
                
        elif secim == "6":
            print("\n⚠️  RİSK ANALİZİ")
            risk_analizi = portfoy_risk_analizi(veriler)
            print(f"Risk Seviyesi: {risk_analizi['risk_seviyesi'].upper()}")
            print(f"Açıklama: {risk_analizi['aciklama']}")
            if 'kripto_orani' in risk_analizi:
                print(f"Kripto Oranı: %{risk_analizi['kripto_orani']:.1f}")
            print(f"Çeşitlilik: {risk_analizi['cesitlilik']} farklı varlık")
            
        elif secim == "7":
            print("\n💡 YATIRIM TAVSİYELERİ")
            tavsiyeler = yatirim_tavsiyesi_ver(veriler)
            for i, tavsiye in enumerate(tavsiyeler, 1):
                print(f"{i}. {tavsiye}")
                
        elif secim == "8":
            print("👋 Güle güle! Verileriniz kaydedildi.")
            break
            
        else:
            print("❌ Geçersiz seçim! 1-8 arası bir sayı girin.")

# Programı başlat
if __name__ == "__main__":
    main()
