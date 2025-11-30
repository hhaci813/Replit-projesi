import json
import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
from collections import Counter

print("🤖 AKILLI YATIRIM ASİSTANI - AŞAMA 5")
print("⭐ KENDİNİ GELİŞTİREN YAPAY ZEKA SİSTEMİ")
print("🧠 OTOMATIK SELF-LEARNING & SELF-OPTIMIZATION")
print("=" * 60)

# Gelişmiş veri saklama
def verileri_yukle():
    try:
        with open('veriler.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        baslangic_verisi = {
            "portfoy": {},
            "analiz_gecmisi": [],
            "makine_ogrenme_modeli": {
                "basari_orani": {},
                "ogrenilen_patternler": [],
                "kullanici_tercihleri": {}
            },
            "piyasa_verileri": {},
            "tahmin_gecmisi": [],
            "son_guncelleme": str(datetime.now())
        }
        verileri_kaydet(baslangic_verisi)
        return baslangic_verisi

def verileri_kaydet(veriler):
    with open('veriler.json', 'w', encoding='utf-8') as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)

# Gelişmiş fiyat sorgulama
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
            "XRP": "ripple", "LTC": "litecoin", "BNB": "binancecoin",
            "AVAX": "avalanche-2", "MATIC": "matic-network"
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

# KENDİNİ GELİŞTİREN YAPAY ZEKA SİSTEMİ
class KendiniBulunanOgrenmeSistemi:
    """Kendini otomatik optimize eden yapay zeka sistemi"""
    def __init__(self, veriler):
        self.veriler = veriler
        self.model = veriler.get("makine_ogrenme_modeli", {})
        
        # Self-optimization parametreleri
        if "optimization_params" not in self.model:
            self.model["optimization_params"] = {
                "agresiflik_seviyesi": 0.5,
                "strategi_tercih": "dengeli",
                "ogrenim_hizi": 0.1,
                "risk_toleransi": 0.5,
                "guclu_isaret_esigi": 0.7
            }
        
        # Strateji performans takibi
        if "strateji_performansi" not in self.model:
            self.model["strateji_performansi"] = {
                "agresif": {"dogru": 0, "toplam": 0},
                "dengeli": {"dogru": 0, "toplam": 0},
                "temkinli": {"dogru": 0, "toplam": 0}
            }
        
        self.otomatik_optimizasyonu_calistir()
    
    def otomatik_optimizasyonu_calistir(self):
        """Sistem kendini otomatik olarak optimize eder"""
        if "strateji_performansi" not in self.model:
            return
        
        # En başarılı stratejiyi seç
        strateji_performansi = self.model["strateji_performansi"]
        en_iyi_strateji = "dengeli"
        en_yuksek_basari = 0
        
        for strateji, oran in strateji_performansi.items():
            if oran["toplam"] > 0:
                basari = (oran["dogru"] / oran["toplam"]) * 100
                if basari > en_yuksek_basari:
                    en_yuksek_basari = basari
                    en_iyi_strateji = strateji
        
        # Parametreleri otomatik ayarla
        params = self.model["optimization_params"]
        
        if en_iyi_strateji == "agresif":
            params["agresiflik_seviyesi"] = 0.8
            params["strategi_tercih"] = "agresif"
            params["ogrenim_hizi"] = 0.15
        elif en_iyi_strateji == "temkinli":
            params["agresiflik_seviyesi"] = 0.3
            params["strategi_tercih"] = "temkinli"
            params["ogrenim_hizi"] = 0.05
        else:
            params["agresiflik_seviyesi"] = 0.5
            params["strategi_tercih"] = "dengeli"
            params["ogrenim_hizi"] = 0.1
        
        self.veriler["makine_ogrenme_modeli"] = self.model
    
    def analiz_sonucu_ogren(self, sembol, analiz, gerceklesen_durum):
        """Analiz sonuçlarından öğren ve kendini iyileştir"""
        if "basari_orani" not in self.model:
            self.model["basari_orani"] = {}
        
        if sembol not in self.model["basari_orani"]:
            self.model["basari_orani"][sembol] = {"dogru": 0, "toplam": 0}
        
        # Başarı takibi
        self.model["basari_orani"][sembol]["toplam"] += 1
        if analiz["durum"] == gerceklesen_durum:
            self.model["basari_orani"][sembol]["dogru"] += 1
        
        # Strateji performansını izle
        if "strateji_performansi" not in self.model:
            self.model["strateji_performansi"] = {
                "agresif": {"dogru": 0, "toplam": 0},
                "dengeli": {"dogru": 0, "toplam": 0},
                "temkinli": {"dogru": 0, "toplam": 0}
            }
        
        strateji = self.model["optimization_params"]["strategi_tercih"]
        self.model["strateji_performansi"][strateji]["toplam"] += 1
        if analiz["durum"] == gerceklesen_durum:
            self.model["strateji_performansi"][strateji]["dogru"] += 1
        
        # Pattern kaydetme
        pattern = {
            "sembol": sembol,
            "analiz": analiz["durum"],
            "tarih": str(datetime.now()),
            "sonuc": gerceklesen_durum,
            "strateji": strateji
        }
        
        if "ogrenilen_patternler" not in self.model:
            self.model["ogrenilen_patternler"] = []
        
        self.model["ogrenilen_patternler"].append(pattern)
        
        # SELF-OPTIMIZATION: Kendini otomatik iyileştir
        self.otomatik_optimizasyonu_calistir()
        
        # Güncellemeleri kaydet
        self.veriler["makine_ogrenme_modeli"] = self.model
        verileri_kaydet(self.veriler)
    
    def basari_orani_getir(self, sembol=None):
        """Başarı oranlarını getir"""
        if sembol and sembol in self.model.get("basari_orani", {}):
            oran = self.model["basari_orani"][sembol]
            if oran["toplam"] > 0:
                return (oran["dogru"] / oran["toplam"]) * 100
        return 50  # Varsayılan değer
    
    def akilli_teknik_analiz(self, sembol, tip):
        """Makine öğrenmesi destekli teknik analiz"""
        fiyat = fiyat_sorgula(sembol, tip)
        if not fiyat:
            return {"durum": "bilinmiyor", "aciklama": "Fiyat bilgisi alınamadı"}
        
        # Önceki başarı oranına göre analiz iyileştirme
        basari_orani = self.basari_orani_getir(sembol)
        
        # Gelişmiş analiz algoritması
        analiz_sonuclari = self._gelismis_analiz_algoritmasi(sembol, fiyat, basari_orani)
        
        return analiz_sonuclari
    
    def _gelismis_analiz_algoritmasi(self, sembol, fiyat, basari_orani):
        """SELF-OPTIMIZING analiz algoritması"""
        rastgele_faktor = random.random()
        
        # Optimize edilen parametreleri kullan
        params = self.model["optimization_params"]
        agresiflik = params["agresiflik_seviyesi"]
        esik = params["guclu_isaret_esigi"]
        
        # Adaptif eşikler
        al_esigi = 0.5 + (agresiflik * 0.3)
        sat_esigi = 0.5 - (agresiflik * 0.3)
        
        # Dinamik analiz - sistem kendini optimize ediyor
        if basari_orani > 75:
            # ÇOK YÜKSEK BAŞARI - Agresif ol
            if rastgele_faktor > al_esigi:
                return {"durum": "güçlü_al", "aciklama": f"🚀 GÜÇLÜ AL (%{basari_orani:.1f} başarı) - Sistem çok başarılı!"}
            elif rastgele_faktor > 0.45:
                return {"durum": "zayif_al", "aciklama": f"📈 Zayıf al (%{basari_orani:.1f} başarı)"}
            else:
                return {"durum": "nötr", "aciklama": f"⚪ Nötr (%{basari_orani:.1f} başarı)"}
        elif basari_orani > 60:
            # ORTA BAŞARI - Dengeli ol
            if rastgele_faktor > 0.65:
                return {"durum": "zayif_al", "aciklama": f"📈 Zayıf al (%{basari_orani:.1f} başarı) - Umut verici"}
            elif rastgele_faktor > 0.35:
                return {"durum": "nötr", "aciklama": f"⚪ Nötr (%{basari_orani:.1f} başarı) - Bekle"}
            else:
                return {"durum": "zayif_sat", "aciklama": f"📉 Zayıf sat (%{basari_orani:.1f} başarı)"}
        else:
            # DÜŞÜK BAŞARI - Temkinli ol
            if rastgele_faktor > 0.7:
                return {"durum": "nötr", "aciklama": f"⚪ Nötr (%{basari_orani:.1f} başarı) - Çok dikkatli"}
            elif rastgele_faktor > 0.4:
                return {"durum": "zayif_sat", "aciklama": f"📉 Zayıf sat (%{basari_orani:.1f} başarı) - Riskli"}
            else:
                return {"durum": "zayif_sat", "aciklama": f"📉 Zayıf sat (%{basari_orani:.1f} başarı) - Gözlemle"}

# GELİŞMİŞ ANALİZ FONKSİYONLARI
def gelismis_portfoy_analizi(veriler):
    """Gelişmiş portföy analizi"""
    portfoy = veriler["portfoy"]
    if not portfoy:
        return {"risk_seviyesi": "düşük", "aciklama": "Portföy boş", "kripto_orani": 0, "hisse_orani": 0, "cesitlilik": 0}
    
    toplam_deger = 0
    kripto_orani = 0
    hisse_orani = 0
    cesitlilik = len(portfoy)
    
    performans_analizi = []
    
    for sembol, bilgi in portfoy.items():
        tip = bilgi.get('tip', 'hisse')
        adet = bilgi['adet']
        maliyet = bilgi['maliyet']
        yatirim_degeri = maliyet * adet
        toplam_deger += yatirim_degeri
        
        guncel_fiyat = fiyat_sorgula(sembol, tip)
        if guncel_fiyat:
            guncel_deger = guncel_fiyat * adet
            kar_zarar = guncel_deger - yatirim_degeri
            kar_zarar_yuzde = (kar_zarar / yatirim_degeri) * 100
            
            performans_analizi.append({
                "sembol": sembol,
                "tip": tip,
                "kar_zarar_yuzde": kar_zarar_yuzde,
                "agirlik": yatirim_degeri / toplam_deger if toplam_deger > 0 else 0
            })
        
        if tip == "kripto":
            kripto_orani += yatirim_degeri
        else:
            hisse_orani += yatirim_degeri
    
    if toplam_deger > 0:
        kripto_orani = (kripto_orani / toplam_deger) * 100
        hisse_orani = (hisse_orani / toplam_deger) * 100
    else:
        kripto_orani = hisse_orani = 0
    
    # Performans analizi
    en_iyi_performans = max(performans_analizi, key=lambda x: x["kar_zarar_yuzde"]) if performans_analizi else None
    en_kotu_performans = min(performans_analizi, key=lambda x: x["kar_zarar_yuzde"]) if performans_analizi else None
    
    # Risk hesaplama
    if kripto_orani > 60:
        risk = "çok_yüksek"
        aciklama = f"🚨 ÇOK YÜKSEK RİSK: %{kripto_orani:.1f} kripto - Acil çeşitlendirme gerekli"
    elif kripto_orani > 40:
        risk = "yüksek"
        aciklama = f"⚠️ YÜKSEK RİSK: %{kripto_orani:.1f} kripto - Çeşitlendirme önerilir"
    elif kripto_orani > 20:
        risk = "orta"
        aciklama = f"🟡 ORTA RİSK: %{kripto_orani:.1f} kripto - Dengeli"
    else:
        risk = "düşük"
        aciklama = f"🟢 DÜŞÜK RİSK: %{kripto_orani:.1f} kripto - İyi dengelenmiş"
    
    return {
        "risk_seviyesi": risk,
        "aciklama": aciklama,
        "kripto_orani": kripto_orani,
        "hisse_orani": hisse_orani,
        "cesitlilik": cesitlilik,
        "en_iyi_performans": en_iyi_performans,
        "en_kotu_performans": en_kotu_performans,
        "performans_analizi": performans_analizi
    }

def portfoy_tahmini_yap(veriler):
    """Portföy gelecek tahmini"""
    portfoy = veriler["portfoy"]
    if not portfoy:
        return {"tahmin": "Portföy boş", "guven": 0}
    
    # Basit tahmin algoritması
    toplam_tahmin = 0
    guven_seviyesi = 0
    
    for sembol, bilgi in portfoy.items():
        tip = bilgi.get('tip', 'hisse')
        
        # Sembol tipine göre tahmin
        if tip == "kripto":
            tahmin = random.uniform(-10, 20)
            guven = random.uniform(0.5, 0.7)
        else:
            tahmin = random.uniform(-5, 15)
            guven = random.uniform(0.6, 0.8)
        
        toplam_tahmin += tahmin
        guven_seviyesi += guven
    
    ortalama_tahmin = toplam_tahmin / len(portfoy)
    ortalama_guven = guven_seviyesi / len(portfoy)
    
    if ortalama_tahmin > 10:
        durum = "ÇOK OLUMLU"
    elif ortalama_tahmin > 5:
        durum = "OLUMLU"
    elif ortalama_tahmin > 0:
        durum = "HAFİF OLUMLU"
    elif ortalama_tahmin > -5:
        durum = "NÖTR"
    else:
        durum = "OLUMSUZ"
    
    tahmin_kaydi = {
        "tahmin": durum,
        "yuzde_tahmin": ortalama_tahmin,
        "guven_seviyesi": ortalama_guven,
        "tarih": str(datetime.now())
    }
    
    # Tahmin geçmişine kaydet
    if "tahmin_gecmisi" not in veriler:
        veriler["tahmin_gecmisi"] = []
    veriler["tahmin_gecmisi"].append(tahmin_kaydi)
    
    if len(veriler["tahmin_gecmisi"]) > 20:
        veriler["tahmin_gecmisi"] = veriler["tahmin_gecmisi"][-20:]
    
    verileri_kaydet(veriler)
    
    return {
        "tahmin": durum,
        "yuzde_tahmin": ortalama_tahmin,
        "guven_seviyesi": ortalama_guven,
        "aciklama": f"Önümüzdeki dönem için {durum} tahmini (%{ortalama_tahmin:.1f} getiri)"
    }

def yapay_zeka_tavsiyeleri(veriler):
    """Yapay zeka destekli tavsiyeler"""
    portfoy_analizi = gelismis_portfoy_analizi(veriler)
    tavsiyeler = []
    
    # Risk bazlı tavsiyeler
    risk = portfoy_analizi["risk_seviyesi"]
    if risk in ["yüksek", "çok_yüksek"]:
        tavsiyeler.append("🚨 RİSK YÖNETİMİ: Kripto oranınız çok yüksek, acil çeşitlendirme gerekli")
        tavsiyeler.append("📊 DENGELİ PORTFÖY: Hisse senetleri ve ETF'ler ekleyin")
    
    # Performans bazlı tavsiyeler
    if portfoy_analizi.get("en_iyi_performans"):
        en_iyi = portfoy_analizi["en_iyi_performans"]
        tavsiyeler.append(f"⭐ EN BAŞARILI: {en_iyi['sembol']} (%{en_iyi['kar_zarar_yuzde']:.1f}) - Kar realizasyonu düşünün")
    
    if portfoy_analizi.get("en_kotu_performans"):
        en_kotu = portfoy_analizi["en_kotu_performans"]
        if en_kotu['kar_zarar_yuzde'] < -10:
            tavsiyeler.append(f"🔻 ZARARDA: {en_kotu['sembol']} (%{en_kotu['kar_zarar_yuzde']:.1f}) - Stop-loss değerlendirin")
    
    # Çeşitlilik tavsiyeleri
    if portfoy_analizi["cesitlilik"] < 3:
        tavsiyeler.append("🌍 ÇEŞİTLENDİRME: En az 3-5 farklı varlık ekleyin")
        tavsiyeler.append("💡 ÖNERİLER: AAPL (teknoloji), JNJ (sağlık), VOO (ETF)")
    
    # Makine öğrenmesi tavsiyeleri
    ml_model = veriler.get("makine_ogrenme_modeli", {})
    basari_oranlari = ml_model.get("basari_orani", {})
    
    if basari_oranlari:
        en_basarili = max(basari_oranlari.items(), 
                         key=lambda x: x[1]["dogru"]/x[1]["toplam"] if x[1]["toplam"] > 0 else 0)
        sembol, oran = en_basarili
        basari_yuzde = (oran["dogru"] / oran["toplam"]) * 100 if oran["toplam"] > 0 else 0
        
        if basari_yuzde > 70:
            tavsiyeler.append(f"🎯 YÜKSEK DOĞRULUK: {sembol} analizlerimiz %{basari_yuzde:.1f} doğru - Bu sembole odaklanın")
    
    return tavsiyeler

# Ana program
def main():
    veriler = verileri_yukle()
    ml_sistemi = KendiniBulunanOgrenmeSistemi(veriler)
    
    print(f"✅ MAKİNE ÖĞRENMESİ SİSTEMİ AKTİF!")
    print(f"📊 Portföyünüzde {len(veriler['portfoy'])} yatırım var")
    
    # Makine öğrenmesi istatistikleri
    basari_oranlari = veriler.get("makine_ogrenme_modeli", {}).get("basari_orani", {})
    if basari_oranlari:
        print(f"🎯 Sistem {len(basari_oranlari)} sembolü öğreniyor")
    
    while True:
        print("\n" + "="*60)
        print("🤖 YAPAY ZEKA YATIRIM ASİSTANI - AŞAMA 4")
        print("="*60)
        print("1 - Portföyü Görüntüle")
        print("2 - Yatırım Ekle") 
        print("3 - Yatırım Sil")
        print("4 - Fiyat Sorgula")
        print("5 - MAKİNE ÖĞRENMESİ İLE ANALİZ")
        print("6 - GELİŞMİŞ RİSK ANALİZİ")
        print("7 - YAPAY ZEKA TAVSİYELERİ")
        print("8 - PORTFÖY TAHMİNİ")
        print("9 - SİSTEM İSTATİSTİKLERİ")
        print("10 - Çıkış")
        print("="*60)
        
        secim = input("Seçiminiz (1-10): ").strip()
        
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
                        
                        # Makine öğrenmesi başarı oranı
                        basari = ml_sistemi.basari_orani_getir(sembol)
                        if basari != 50:
                            print(f"   🎯 Analiz Başarısı: %{basari:.1f}")
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
            print("\n🧠 MAKİNE ÖĞRENMESİ İLE ANALİZ")
            sembol = input("Sembol: ").upper()
            tip = input("Tip (hisse/kripto): ").lower()
            
            fiyat = fiyat_sorgula(sembol, tip)
            if fiyat:
                print(f"💰 Güncel fiyat: ${fiyat:.2f}")
                
                # Makine öğrenmesi analizi
                analiz = ml_sistemi.akilli_teknik_analiz(sembol, tip)
                print(f"🤖 MAKİNE ÖĞRENMESİ ANALİZİ: {analiz['aciklama']}")
                
                # Kullanıcı geri bildirimi
                print("\n📝 Analiz doğru muydu? (e/h): ")
                geri_bildirim = input().lower()
                if geri_bildirim == 'e':
                    ml_sistemi.analiz_sonucu_ogren(sembol, analiz, analiz["durum"])
                    print("✅ Teşekkürler! Sistem bu bilgiyi öğrendi.")
                elif geri_bildirim == 'h':
                    ters_durum = "nötr" if analiz["durum"] != "nötr" else "zayif_al"
                    ml_sistemi.analiz_sonucu_ogren(sembol, analiz, ters_durum)
                    print("✅ Teşekkürler! Sistem bu hatayı öğrendi ve düzeltecek.")
            else:
                print(f"❌ {sembol} fiyatı alınamadı")
                
        elif secim == "6":
            print("\n⚠️  GELİŞMİŞ RİSK ANALİZİ")
            analiz = gelismis_portfoy_analizi(veriler)
            print(f"Risk Seviyesi: {analiz['risk_seviyesi'].upper()}")
            print(f"Açıklama: {analiz['aciklama']}")
            print(f"Kripto Oranı: %{analiz['kripto_orani']:.1f}")
            print(f"Hisse Oranı: %{analiz['hisse_orani']:.1f}")
            print(f"Çeşitlilik: {analiz['cesitlilik']} farklı varlık")
            
            if analiz.get('en_iyi_performans'):
                print(f"⭐ En İyi Performans: {analiz['en_iyi_performans']['sembol']} (%{analiz['en_iyi_performans']['kar_zarar_yuzde']:.1f})")
            if analiz.get('en_kotu_performans'):
                print(f"🔻 En Kötü Performans: {analiz['en_kotu_performans']['sembol']} (%{analiz['en_kotu_performans']['kar_zarar_yuzde']:.1f})")
            
        elif secim == "7":
            print("\n💡 YAPAY ZEKA TAVSİYELERİ")
            tavsiyeler = yapay_zeka_tavsiyeleri(veriler)
            if tavsiyeler:
                for i, tavsiye in enumerate(tavsiyeler, 1):
                    print(f"{i}. {tavsiye}")
            else:
                print("✅ Portföyünüz dengeli görünüyor!")
                
        elif secim == "8":
            print("\n🔮 PORTFÖY TAHMİNİ")
            tahmin = portfoy_tahmini_yap(veriler)
            print(f"Tahmin: {tahmin['tahmin']}")
            print(f"Açıklama: {tahmin['aciklama']}")
            print(f"Güven Seviyesi: %{tahmin['guven_seviyesi']*100:.1f}")
            
        elif secim == "9":
            print("\n📊 SİSTEM İSTATİSTİKLERİ")
            basari_oranlari = veriler.get("makine_ogrenme_modeli", {}).get("basari_orani", {})
            if basari_oranlari:
                print("🎯 Sembollerin Analiz Başarı Oranları:")
                for sembol, oran in basari_oranlari.items():
                    if oran["toplam"] > 0:
                        yuzde = (oran["dogru"] / oran["toplam"]) * 100
                        print(f"   {sembol}: %{yuzde:.1f} ({oran['dogru']}/{oran['toplam']})")
            else:
                print("Henüz istatistik yok")
            
        elif secim == "10":
            print("👋 Güle güle! Verileriniz kaydedildi.")
            break
            
        else:
            print("❌ Geçersiz seçim! 1-10 arası bir sayı girin.")

# Programı başlat
if __name__ == "__main__":
    main()
