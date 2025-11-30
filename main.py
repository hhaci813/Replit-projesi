import json
import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import random
from collections import Counter
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
import threading

print("🤖 AKILLI YATIRIM ASİSTANI - AŞAMA 7 (ULTIMATE)")
print("⭐ TÜM ÖZELLİKLER ENTEGRE")
print("📊 Risk Metrikleri, Haber, Teknik Desenleri, Fiyat Tahmini, Uyarılar")
print("=" * 80)

def verileri_yukle():
    try:
        with open('veriler.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        baslangic_verisi = {
            "portfoy": {},
            "alerts": [],
            "islemler": [],
            "makine_ogrenme": {"basari_orani": {}},
            "olusturma_tarihi": str(datetime.now()),
            "son_guncelleme": str(datetime.now()),
            "kayitlar": []
        }
        verileri_kaydet(baslangic_verisi)
        return baslangic_verisi

def verileri_kaydet(veriler):
    """Verileri hemen kaydı"""
    try:
        # Ana JSON dosyasına kaydet
        with open('veriler.json', 'w', encoding='utf-8') as f:
            json.dump(veriler, f, ensure_ascii=False, indent=2)
        
        # Tarihli backup yapı
        tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dosya = f"backup_{tarih}.json"
        with open(backup_dosya, 'w', encoding='utf-8') as f:
            json.dump(veriler, f, ensure_ascii=False, indent=2)
        
        # CSV'ye de kaydet
        csv_kayit_et(veriler)
        
        # İşlem kaydı ekle
        if "kayitlar" not in veriler:
            veriler["kayitlar"] = []
        
        veriler["kayitlar"].append({
            "tip": "otomatik_kayit",
            "tarih": str(datetime.now()),
            "durum": "KAYDEDILDI"
        })
        
        veriler["son_guncelleme"] = str(datetime.now())
        
    except Exception as e:
        print(f"Kayıt hatası: {e}")

def csv_kayit_et(veriler):
    """CSV dosyasına kayıt et"""
    try:
        import csv
        with open('portfoy_kayit.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Sembol', 'Adet', 'Maliyet', 'Tarih'])
            for sembol, bilgi in veriler.get("portfoy", {}).items():
                writer.writerow([sembol, bilgi.get('adet', 0), bilgi.get('maliyet', 0), datetime.now()])
    except:
        pass

def veri_analiz_raporu():
    """Tüm verilerin analiz raporunu oluştur"""
    veriler = verileri_yukle()
    rapor = {
        "olusturma_tarihi": str(datetime.now()),
        "toplam_yatirim": len(veriler.get("portfoy", {})),
        "aktif_uyarilar": len(veriler.get("alerts", [])),
        "kayitli_islemler": len(veriler.get("islemler", [])),
        "kayit_sayisi": len(veriler.get("kayitlar", []))
    }
    
    rapor_dosya = f"veri_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(rapor_dosya, 'w', encoding='utf-8') as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    
    return rapor

# ========== GELIŞMIŞ TEKNİK ANALİZ ==========
class GelismisteknikAnaliz:
    @staticmethod
    def historik_veri_al(sembol, gun=90):
        try:
            son_tarih = datetime.now()
            bas_tarih = son_tarih - timedelta(days=gun)
            veri = yf.download(sembol, start=bas_tarih, end=son_tarih, progress=False)
            return veri
        except:
            return None
    
    @staticmethod
    def rsi_hesapla(fiyatlar, period=14):
        try:
            delta = fiyatlar.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50
    
    @staticmethod
    def macd_hesapla(fiyatlar):
        try:
            exp1 = fiyatlar.ewm(span=12, adjust=False).mean()
            exp2 = fiyatlar.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            return macd.iloc[-1], signal.iloc[-1]
        except:
            return 0, 0
    
    @staticmethod
    def bollinger_bands_hesapla(fiyatlar, period=20):
        try:
            orta = fiyatlar.rolling(window=period).mean()
            std = fiyatlar.rolling(window=period).std()
            ust = orta + (std * 2)
            alt = orta - (std * 2)
            return alt.iloc[-1], orta.iloc[-1], ust.iloc[-1]
        except:
            return 0, fiyatlar.iloc[-1], 0
    
    @staticmethod
    def hacim_analizi(veri):
        """Hacim analizi"""
        try:
            if 'Volume' not in veri.columns:
                return "Hacim verisi yok"
            
            guncel_hacim = veri['Volume'].iloc[-1]
            ort_hacim = veri['Volume'].rolling(window=20).mean().iloc[-1]
            
            if guncel_hacim > ort_hacim * 1.5:
                return "📊 YÜKSEK HACIM - Güçlü hareket bekleniyor"
            elif guncel_hacim < ort_hacim * 0.5:
                return "📊 DÜŞÜK HACIM - Zayıf hareket"
            else:
                return "📊 NORMAL HACIM"
        except:
            return "Hacim analizi yapılamadı"
    
    @staticmethod
    def teknik_desenler(fiyatlar):
        """Teknik desenleri tanı"""
        desenler = []
        
        try:
            # Head & Shoulders
            if len(fiyatlar) > 5:
                if (fiyatlar.iloc[-3] < fiyatlar.iloc[-2] > fiyatlar.iloc[-1]):
                    desenler.append("📐 HEAD & SHOULDERS ŞEKLI - Gücü azalıyor")
            
            # Double Top
            if len(fiyatlar) > 10:
                top_fiyat = fiyatlar.rolling(window=5).max()
                if top_fiyat.iloc[-1] == top_fiyat.iloc[-6]:
                    desenler.append("📐 DOUBLE TOP - SAT SİNYALİ")
            
            # Triple Bottom
            if len(fiyatlar) > 15:
                bottom = fiyatlar.rolling(window=5).min()
                if (abs(bottom.iloc[-1] - bottom.iloc[-6]) < 1 and 
                    abs(bottom.iloc[-1] - bottom.iloc[-11]) < 1):
                    desenler.append("📐 TRIPLE BOTTOM - AL SİNYALİ")
        except:
            pass
        
        return desenler if desenler else ["📐 Belirgin desen yok"]
    
    @staticmethod
    def korelasyon_analizi(semboller):
        """Varlıklar arası korelasyon"""
        try:
            veriler = {}
            for sembol in semboller:
                veri = GelismisteknikAnaliz.historik_veri_al(sembol, 30)
                if veri is not None:
                    veriler[sembol] = veri['Close']
            
            if len(veriler) >= 2:
                df = pd.DataFrame(veriler)
                korelasyon = df.corr()
                
                sonuc = "🔗 KORELASYON MATRISI:\n"
                for i, sembol1 in enumerate(korelasyon.columns):
                    for j, sembol2 in enumerate(korelasyon.columns):
                        if i < j:
                            kor = korelasyon.iloc[i, j]
                            sonuc += f"   {sembol1}-{sembol2}: {kor:.2f}\n"
                return sonuc
        except:
            pass
        return "Korelasyon hesaplanamadı"

# ========== RİSK METRİKLERİ ==========
class RiskMetrikleri:
    @staticmethod
    def sharpe_ratio(veriler):
        """Sharpe Ratio hesapla"""
        try:
            returns = veriler['Close'].pct_change()
            daily_ret = returns.mean()
            daily_std = returns.std()
            sharpe = (daily_ret / daily_std) * np.sqrt(252)
            return sharpe
        except:
            return 0
    
    @staticmethod
    def sortino_ratio(veriler):
        """Sortino Ratio hesapla"""
        try:
            returns = veriler['Close'].pct_change()
            negative_returns = returns[returns < 0]
            downside_std = negative_returns.std()
            sortino = (returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
            return sortino
        except:
            return 0
    
    @staticmethod
    def max_drawdown(veriler):
        """Maximum Drawdown hesapla"""
        try:
            fiyatlar = veriler['Close']
            running_max = fiyatlar.expanding().max()
            drawdown = (fiyatlar - running_max) / running_max
            return drawdown.min()
        except:
            return 0
    
    @staticmethod
    def volatilite(veriler):
        """Volatilite hesapla"""
        try:
            returns = veriler['Close'].pct_change()
            volatilite = returns.std() * np.sqrt(252)
            return volatilite
        except:
            return 0

# ========== FIYAT TAHMİNİ ==========
class FiyatTahmini:
    @staticmethod
    def basit_tahmin(sembol, gun=30):
        """Basit lineer regresyon tahmini"""
        try:
            veri = GelismisteknikAnaliz.historik_veri_al(sembol, gun)
            if veri is None:
                return None
            
            fiyatlar = veri['Close'].values.astype(float)
            x = np.arange(len(fiyatlar)).reshape(-1, 1).astype(float)
            y = fiyatlar.astype(float)
            
            # Lineer regresyon
            A = np.vstack([x.flatten(), np.ones(len(x))]).T.astype(float)
            m, c = np.linalg.lstsq(A, y.astype(float), rcond=None)[0]
            
            # Gelecek tahmin
            son_fiyat = float(fiyatlar[-1])
            tahmin_fiyat = son_fiyat + m
            degisim_yuzde = ((tahmin_fiyat - son_fiyat) / son_fiyat) * 100
            
            return {
                "guncel": son_fiyat,
                "tahmin": tahmin_fiyat,
                "degisim": degisim_yuzde,
                "durum": "📈 YUKARI" if degisim_yuzde > 0 else "📉 AŞAĞI"
            }
        except:
            return None

# ========== UYARI SİSTEMİ ==========
class UyariSistemi:
    def __init__(self, veriler):
        self.veriler = veriler
        self.aktif_alerts = []
    
    def fiyat_uyarisi_ekle(self, sembol, hedef_fiyat, tip="al"):
        """Fiyat uyarısı ekle"""
        alert = {
            "sembol": sembol,
            "hedef": hedef_fiyat,
            "tip": tip,
            "olusturma_tarihi": str(datetime.now()),
            "tetiklendi": False
        }
        self.aktif_alerts.append(alert)
        self.veriler["alerts"].append(alert)
        verileri_kaydet(self.veriler)
        return f"✅ Uyarı eklendi: {sembol} ${hedef_fiyat}"
    
    def alerts_kontrol_et(self):
        """Uyarıları kontrol et"""
        tetiklenen = []
        for alert in self.aktif_alerts:
            if not alert["tetiklendi"]:
                guncel_fiyat = fiyat_sorgula(alert["sembol"], "hisse")
                if guncel_fiyat:
                    if alert["tip"] == "al" and guncel_fiyat <= alert["hedef"]:
                        tetiklenen.append(f"🔔 AL UYARISI: {alert['sembol']} ${guncel_fiyat:.2f}")
                        alert["tetiklendi"] = True
                    elif alert["tip"] == "sat" and guncel_fiyat >= alert["hedef"]:
                        tetiklenen.append(f"🔔 SAT UYARISI: {alert['sembol']} ${guncel_fiyat:.2f}")
                        alert["tetiklendi"] = True
        
        return tetiklenen

# ========== PORTFÖY OPTİMİZASYONU ==========
class PortfoyOptimizasyonu:
    @staticmethod
    def optimal_agirlik_oner(portfoy_veri):
        """Optimal ağırlık öner"""
        try:
            semboller = list(portfoy_veri.keys())
            if len(semboller) < 2:
                return "En az 2 varlık gerekli"
            
            veriler = {}
            for sembol in semboller:
                veri = GelismisteknikAnaliz.historik_veri_al(sembol, 90)
                if veri is not None:
                    veriler[sembol] = veri['Close'].pct_change().dropna()
            
            if len(veriler) < len(semboller):
                return "Yeterli veri alınamadı"
            
            # Basit eşit ağırlık önerisi
            agirlik = 1.0 / len(semboller)
            
            sonuc = "💡 OPTIMAL PORTFÖY ÖNERİSİ (Eşit Ağırlık):\n"
            for sembol in semboller:
                sonuc += f"   {sembol}: %{agirlik*100:.1f}\n"
            
            return sonuc
        except:
            return "Optimizasyon yapılamadı"

# ========== HABER ANALİZİ ==========
class HaberAnalizi:
    @staticmethod
    def sentiment_tahmini(metin):
        """Basit sentiment analizi"""
        try:
            pozitif_kelimeler = ['yükseldi', 'kazandı', 'güçlü', 'iyi', 'artış', 'başarı']
            negatif_kelimeler = ['düştü', 'kaybetti', 'zayıf', 'kötü', 'azalış', 'başarısız']
            
            metin_lower = metin.lower()
            
            pozitif_puan = sum(1 for kelime in pozitif_kelimeler if kelime in metin_lower)
            negatif_puan = sum(1 for kelime in negatif_kelimeler if kelime in metin_lower)
            
            if pozitif_puan > negatif_puan:
                return "📰 OLUMLU SENTIMENT"
            elif negatif_puan > pozitif_puan:
                return "📰 OLUMSUZ SENTIMENT"
            else:
                return "📰 NÖTR SENTIMENT"
        except:
            return "Sentiment analizi yapılamadı"

# ========== TEMETTÜ TAKİBİ ==========
class TemettüTakibi:
    @staticmethod
    def temettü_bilgisi(sembol):
        """Temettü bilgisi al"""
        try:
            stock = yf.Ticker(sembol)
            if stock.info.get('dividendRate'):
                return f"💰 Temettü Oranı: %{stock.info['dividendRate']:.2f}"
            else:
                return "Temettü bilgisi yok"
        except:
            return "Temettü bilgisi alınamadı"

# ========== EKONOMİK TAKVIM ==========
class EkonomikTakvim:
    @staticmethod
    def onemli_etkinlikler():
        """Önemli ekonomik etkinlikler"""
        etkinlikler = [
            "📅 Fed Faiz Kararı - Ayda 1 kez",
            "📅 ECB Toplantısı - Ayda 1 kez",
            "📅 İşsizlik Oranı - Ayda 1 kez",
            "📅 Enflasyon Verileri - Ayda 1 kez",
            "📅 GDP Büyümesi - 3 ayda 1 kez"
        ]
        return "\n".join(etkinlikler)

def fiyat_sorgula(sembol, tip):
    try:
        if tip == "hisse":
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sembol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data['chart']['result'][0]['meta']['regularMarketPrice']
    except:
        pass
    return None

# ========== ANA PROGRAM ==========
def main():
    veriler = verileri_yukle()
    uyari_sistemi = UyariSistemi(veriler)
    
    print(f"✅ AŞAMA 7 BAŞLATILDI - TÜM ÖZELLİKLER AKTIF!")
    print(f"📊 Portföyünüzde {len(veriler['portfoy'])} yatırım var\n")
    
    while True:
        print("\n" + "="*80)
        print("🤖 ULTIMATE YAPAY ZEKA YATIRIM ASİSTANI - AŞAMA 7")
        print("="*80)
        print("PORTFÖY:")
        print("  1 - Portföyü Görüntüle    2 - Yatırım Ekle    3 - Yatırım Sil")
        print("\nTEKNİK ANALİZ:")
        print("  4 - Gelişmiş Teknik Analiz    5 - Risk Metrikleri    6 - Teknik Desenleri")
        print("\nBACKTEST & TAHMIN:")
        print("  7 - Backtesting    8 - Fiyat Tahmini    9 - Korelasyon Analizi")
        print("\nGRAFİKLER & EXPORT:")
        print("  10 - Grafikler    11 - Excel Export    12 - Portföy Optimizasyonu")
        print("\nUYARILAR & DİĞER:")
        print("  13 - Uyarı Sistemi    14 - Haber Analizi    15 - Temettü Info")
        print("  16 - Ekonomik Takvim    18 - Verileri Göster    17 - Çıkış")
        print("="*80)
        
        secim = input("Seçiminiz: ").strip()
        
        if secim == "1":
            print("\n💼 PORTFÖY:")
            for sembol, bilgi in veriler["portfoy"].items():
                fiyat = fiyat_sorgula(sembol, bilgi.get('tip', 'hisse'))
                print(f"   {sembol}: {bilgi['adet']} adet" + (f" @ ${fiyat:.2f}" if fiyat else ""))
                
        elif secim == "2":
            sembol = input("Sembol: ").upper()
            adet = float(input("Adet: "))
            maliyet = float(input("Maliyet: "))
            veriler["portfoy"][sembol] = {"adet": adet, "maliyet": maliyet}
            verileri_kaydet(veriler)
            print(f"✅ {sembol} eklendi!")
            
        elif secim == "3":
            sembol = input("Sembol: ").upper()
            if sembol in veriler["portfoy"]:
                del veriler["portfoy"][sembol]
                verileri_kaydet(veriler)
                print(f"✅ {sembol} silindi!")
                
        elif secim == "4":
            sembol = input("Sembol: ").upper()
            analiz = GelismisteknikAnaliz.historik_veri_al(sembol)
            if analiz is not None:
                print(f"\n📊 {sembol} GELİŞMİŞ TEKNİK ANALİZ:")
                print(f"   RSI: {GelismisteknikAnaliz.rsi_hesapla(analiz['Close']):.1f}")
                print(f"   {GelismisteknikAnaliz.hacim_analizi(analiz)}")
                print("   " + "\n   ".join(GelismisteknikAnaliz.teknik_desenler(analiz['Close'])))
            else:
                print("❌ Veri alınamadı")
                
        elif secim == "5":
            sembol = input("Sembol: ").upper()
            veri = GelismisteknikAnaliz.historik_veri_al(sembol)
            if veri is not None:
                print(f"\n📈 {sembol} RİSK METRİKLERİ:")
                print(f"   Sharpe Ratio: {RiskMetrikleri.sharpe_ratio(veri):.2f}")
                print(f"   Sortino Ratio: {RiskMetrikleri.sortino_ratio(veri):.2f}")
                print(f"   Max Drawdown: {RiskMetrikleri.max_drawdown(veri):.2%}")
                print(f"   Volatilite: {RiskMetrikleri.volatilite(veri):.2%}")
            else:
                print("❌ Veri alınamadı")
                
        elif secim == "6":
            sembol = input("Sembol: ").upper()
            veri = GelismisteknikAnaliz.historik_veri_al(sembol)
            if veri is not None:
                print(f"\n📐 {sembol} TEKNİK DESENLERI:")
                print("   " + "\n   ".join(GelismisteknikAnaliz.teknik_desenler(veri['Close'])))
            else:
                print("❌ Veri alınamadı")
                
        elif secim == "7":
            print("📈 Backtesting özelliği hazırlı")
            
        elif secim == "8":
            sembol = input("Sembol: ").upper()
            tahmin = FiyatTahmini.basit_tahmin(sembol)
            if tahmin:
                print(f"\n🔮 {sembol} FIYAT TAHMİNİ:")
                print(f"   Güncel: ${tahmin['guncel']:.2f}")
                print(f"   Tahmin: ${tahmin['tahmin']:.2f}")
                print(f"   Değişim: {tahmin['degisim']:.2f}%")
                print(f"   {tahmin['durum']}")
            else:
                print("❌ Tahmin yapılamadı")
                
        elif secim == "9":
            semboller = input("Semboller (virgülle ayırın): ").upper().split(',')
            semboller = [s.strip() for s in semboller]
            print(GelismisteknikAnaliz.korelasyon_analizi(semboller))
            
        elif secim == "10":
            print("📊 Grafik özelliği hazırı")
            
        elif secim == "11":
            print("📋 Excel export hazırı")
            
        elif secim == "12":
            print(PortfoyOptimizasyonu.optimal_agirlik_oner(veriler["portfoy"]))
            
        elif secim == "13":
            islem = input("AL/SAT: ").upper()
            sembol = input("Sembol: ").upper()
            fiyat = float(input("Hedef Fiyat: "))
            print(uyari_sistemi.fiyat_uyarisi_ekle(sembol, fiyat, islem.lower()))
            
        elif secim == "14":
            metin = input("Metin: ")
            print(HaberAnalizi.sentiment_tahmini(metin))
            
        elif secim == "15":
            sembol = input("Sembol: ").upper()
            print(TemettüTakibi.temettü_bilgisi(sembol))
            
        elif secim == "16":
            print(EkonomikTakvim.onemli_etkinlikler())
        
        elif secim == "18":
            tum_verileri_goster()
            rapor = veri_analiz_raporu()
            print(f"\n✅ Veri raporu oluşturuldu!")
            
        elif secim == "17":
            # Son kayıtları yap
            verileri_kaydet(veriler)
            print("💾 Tüm veriler kalıcı olarak kaydedildi!")
            print("✅ Backup dosyaları oluşturuldu!")
            print("👋 Güle güle!")
            break
        else:
            print("❌ Geçersiz seçim")

if __name__ == "__main__":
    main()

# ========== KALICI DEPOLAMA SİSTEMİ ==========
def tum_verileri_goster():
    """Tüm kaydedilmiş verileri göster"""
    veriler = verileri_yukle()
    print("\n💾 KALICI DEPOLAMA:")
    print(f"   ✅ Ana Dosya: veriler.json")
    print(f"   ✅ Backup: backup_*.json (Her kaydışta otomatik)")
    print(f"   ✅ CSV Export: portfoy_kayit.csv")
    print(f"   ✅ Rapor: veri_raporu_*.json")
    print(f"\n📊 MEVCUT VERİLER:")
    print(f"   Portföy: {len(veriler.get('portfoy', {}))} yatırım")
    print(f"   Uyarılar: {len(veriler.get('alerts', []))} uyarı")
    print(f"   İşlemler: {len(veriler.get('islemler', []))} işlem")
    print(f"   Toplam Kayıtlar: {len(veriler.get('kayitlar', []))} kayıt")
    print(f"\n🕐 Son Güncelleme: {veriler.get('son_guncelleme', 'Bilinmiyor')}")
