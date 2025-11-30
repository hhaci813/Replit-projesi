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

print("🤖 AKILLI YATIRIM ASİSTANI - AŞAMA 6")
print("⭐ KENDİNİ GELİŞTİREN YAPAY ZEKA + GERÇEK ANALİZ")
print("📊 Historik Veri, Backtesting, Grafik, Excel Export")
print("=" * 70)

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
                "optimization_params": {
                    "agresiflik_seviyesi": 0.5,
                    "strategi_tercih": "dengeli"
                }
            },
            "backtesting_sonuclari": []
        }
        verileri_kaydet(baslangic_verisi)
        return baslangic_verisi

def verileri_kaydet(veriler):
    with open('veriler.json', 'w', encoding='utf-8') as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)

# ========== GERÇEK TEKNİK ANALİZ ==========
class GercekTeknikAnaliz:
    @staticmethod
    def historik_veri_al(sembol, gun=30):
        """Historik veri yükle"""
        try:
            son_tarih = datetime.now()
            bas_tarih = son_tarih - timedelta(days=gun)
            
            veri = yf.download(sembol, start=bas_tarih, end=son_tarih, progress=False)
            return veri
        except:
            return None
    
    @staticmethod
    def rsi_hesapla(fiyatlar, period=14):
        """Gerçek RSI hesapla"""
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
        """MACD hesapla"""
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
        """Bollinger Bands hesapla"""
        try:
            orta = fiyatlar.rolling(window=period).mean()
            std = fiyatlar.rolling(window=period).std()
            
            ust = orta + (std * 2)
            alt = orta - (std * 2)
            
            return alt.iloc[-1], orta.iloc[-1], ust.iloc[-1]
        except:
            return 0, fiyatlar.iloc[-1], 0
    
    @staticmethod
    def trend_gucunun_hesapla(fiyatlar):
        """Trend gücü hesapla"""
        try:
            hareketli_ort_10 = fiyatlar.rolling(window=10).mean()
            hareketli_ort_50 = fiyatlar.rolling(window=50).mean()
            
            if hareketli_ort_10.iloc[-1] > hareketli_ort_50.iloc[-1]:
                return "YUKARI TREND", 75
            elif hareketli_ort_10.iloc[-1] < hareketli_ort_50.iloc[-1]:
                return "AŞAĞI TREND", 25
            else:
                return "YATAY TREND", 50
        except:
            return "NÖTR", 50
    
    @staticmethod
    def tam_analiz(sembol):
        """Tam teknik analiz raporu"""
        veri = GercekTeknikAnaliz.historik_veri_al(sembol)
        if veri is None or len(veri) < 20:
            return None
        
        fiyatlar = veri['Close']
        guncel_fiyat = fiyatlar.iloc[-1]
        
        # Tüm göstergeleri hesapla
        rsi = GercekTeknikAnaliz.rsi_hesapla(fiyatlar)
        macd, signal = GercekTeknikAnaliz.macd_hesapla(fiyatlar)
        alt, orta, ust = GercekTeknikAnaliz.bollinger_bands_hesapla(fiyatlar)
        trend, trend_gucu = GercekTeknikAnaliz.trend_gucunun_hesapla(fiyatlar)
        
        # Sinyaller
        sinyaller = []
        
        if rsi < 30:
            sinyaller.append("🟢 RSI AŞIRı SATILMIŞ - GÜÇLÜ AL")
        elif rsi > 70:
            sinyaller.append("🔴 RSI AŞIRı ALILMIŞ - GÜÇLÜ SAT")
        
        if macd > signal:
            sinyaller.append("📈 MACD POZİTİF - AL İŞARETİ")
        else:
            sinyaller.append("📉 MACD NEGATİF - SAT İŞARETİ")
        
        if guncel_fiyat < alt:
            sinyaller.append("🎯 Fiyat Bollinger Alt Bandının Altında - AL FIRSATI")
        elif guncel_fiyat > ust:
            sinyaller.append("🎯 Fiyat Bollinger Üst Bandının Üstünde - SAT FIRSATI")
        
        return {
            "guncel_fiyat": guncel_fiyat,
            "rsi": rsi,
            "macd": macd,
            "signal": signal,
            "bollinger_alt": alt,
            "bollinger_orta": orta,
            "bollinger_ust": ust,
            "trend": trend,
            "trend_gucu": trend_gucu,
            "sinyaller": sinyaller,
            "veri": veri
        }

# ========== BACKTESTING ==========
class Backtesting:
    @staticmethod
    def basit_backtest(sembol, strategi="ma_cross", gun=90):
        """Basit backtesting"""
        try:
            veri = GercekTeknikAnaliz.historik_veri_al(sembol, gun)
            if veri is None or len(veri) < 50:
                return None
            
            fiyatlar = veri['Close']
            ma10 = fiyatlar.rolling(window=10).mean()
            ma50 = fiyatlar.rolling(window=50).mean()
            
            # İşlemleri simüle et
            kaputal = 10000
            hisse_sayisi = 0
            toplam_kar_zarar = 0
            islemler = []
            
            for i in range(50, len(fiyatlar)):
                if ma10.iloc[i] > ma50.iloc[i] and hisse_sayisi == 0:
                    # AL
                    hisse_sayisi = kaputal / fiyatlar.iloc[i]
                    islemler.append(f"AL: {fiyatlar.iloc[i]:.2f}")
                elif ma10.iloc[i] < ma50.iloc[i] and hisse_sayisi > 0:
                    # SAT
                    kar_zarar = (fiyatlar.iloc[i] * hisse_sayisi) - kaputal
                    toplam_kar_zarar += kar_zarar
                    islemler.append(f"SAT: {fiyatlar.iloc[i]:.2f} | Kar/Zarar: ${kar_zarar:.2f}")
                    hisse_sayisi = 0
            
            # Son hisse varsa, hesapla
            if hisse_sayisi > 0:
                kar_zarar = (fiyatlar.iloc[-1] * hisse_sayisi) - kaputal
                toplam_kar_zarar += kar_zarar
            
            getiri_yuzde = (toplam_kar_zarar / kaputal) * 100
            
            return {
                "basari": toplam_kar_zarar > 0,
                "kar_zarar": toplam_kar_zarar,
                "getiri_yuzde": getiri_yuzde,
                "islemler": islemler
            }
        except:
            return None

# ========== OTOMATİK TRADING SİSTEMİ ==========
class OtomatikTradingListesi:
    def __init__(self):
        self.siparisler = []
    
    def al_emri_ekle(self, sembol, hedef_fiyat, maliyet):
        """AL emri ekle"""
        if fiyat_sorgula(sembol, "hisse") <= hedef_fiyat:
            self.siparisler.append({
                "tip": "AL",
                "sembol": sembol,
                "fiyat": hedef_fiyat,
                "durum": "ONAYLANABILIR"
            })
            return True
        else:
            self.siparisler.append({
                "tip": "AL",
                "sembol": sembol,
                "fiyat": hedef_fiyat,
                "durum": "BEKLEME"
            })
            return False
    
    def sat_emri_ekle(self, sembol, hedef_fiyat):
        """SAT emri ekle"""
        if fiyat_sorgula(sembol, "hisse") >= hedef_fiyat:
            self.siparisler.append({
                "tip": "SAT",
                "sembol": sembol,
                "fiyat": hedef_fiyat,
                "durum": "ONAYLANABILIR"
            })
            return True
        else:
            self.siparisler.append({
                "tip": "SAT",
                "sembol": sembol,
                "fiyat": hedef_fiyat,
                "durum": "BEKLEME"
            })
            return False

def fiyat_sorgula(sembol, tip):
    """Fiyat sorgula"""
    try:
        if tip == "hisse":
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sembol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data['chart']['result'][0]['meta']['regularMarketPrice']
        elif tip == "kripto":
            kripto_eslestirme = {
                "BTC": "bitcoin", "ETH": "ethereum", "ADA": "cardano",
                "DOT": "polkadot", "DOGE": "dogecoin"
            }
            kripto_id = kripto_eslestirme.get(sembol, sembol.lower())
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={kripto_id}&vs_currencies=usd"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data[kripto_id]['usd']
    except:
        pass
    return None

# ========== EXCEL EXPORT ==========
def portfoy_excel_export(veriler, dosya_adi="portfoy.xlsx"):
    """Portföyü Excel'e aktar"""
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Portföy"
        
        # Başlık
        baslıklar = ["Sembol", "Tip", "Adet", "Maliyet", "Güncel Fiyat", "Değer", "Kar/Zarar", "Kar/Zarar %"]
        ws.append(baslıklar)
        
        # Stil
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        
        # Veriler
        toplam_deger = 0
        toplam_kar_zarar = 0
        
        for sembol, bilgi in veriler["portfoy"].items():
            tip = bilgi.get('tip', 'hisse')
            adet = bilgi['adet']
            maliyet = bilgi['maliyet']
            
            guncel_fiyat = fiyat_sorgula(sembol, tip)
            if guncel_fiyat:
                guncel_deger = guncel_fiyat * adet
                yatirim_degeri = maliyet * adet
                kar_zarar = guncel_deger - yatirim_degeri
                kar_zarar_yuzde = (kar_zarar / yatirim_degeri * 100) if yatirim_degeri > 0 else 0
                
                toplam_deger += guncel_deger
                toplam_kar_zarar += kar_zarar
                
                ws.append([sembol, tip, adet, f"${maliyet:.2f}", f"${guncel_fiyat:.2f}", 
                          f"${guncel_deger:.2f}", f"${kar_zarar:.2f}", f"%{kar_zarar_yuzde:.2f}"])
        
        # Toplam satırı
        ws.append(["", "", "", "", "TOPLAM", f"${toplam_deger:.2f}", f"${toplam_kar_zarar:.2f}", 
                  f"%{(toplam_kar_zarar/toplam_deger*100) if toplam_deger > 0 else 0:.2f}"])
        
        wb.save(dosya_adi)
        return f"✅ Excel dosyası kaydedildi: {dosya_adi}"
    except Exception as e:
        return f"❌ Hata: {e}"

# ========== GRAFIK ÇIZME ==========
def grafik_ciz(sembol):
    """Fiyat grafiği çiz"""
    try:
        veri = GercekTeknikAnaliz.historik_veri_al(sembol, 60)
        if veri is None:
            return False
        
        plt.figure(figsize=(12, 6))
        
        # Fiyat grafiği
        plt.plot(veri.index, veri['Close'], label='Kapanış Fiyatı', color='blue', linewidth=2)
        
        # Hareketli ortalamalar
        ma10 = veri['Close'].rolling(window=10).mean()
        ma50 = veri['Close'].rolling(window=50).mean()
        
        plt.plot(veri.index, ma10, label='10-Günlük MA', color='orange', alpha=0.7)
        plt.plot(veri.index, ma50, label='50-Günlük MA', color='red', alpha=0.7)
        
        plt.title(f'{sembol} - Fiyat Analizi (Son 60 Gün)', fontsize=14, fontweight='bold')
        plt.xlabel('Tarih')
        plt.ylabel('Fiyat ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        dosya_adi = f"grafik_{sembol}.png"
        plt.savefig(dosya_adi, dpi=100)
        plt.close()
        
        return True
    except:
        return False

def portfoy_dagılım_grafigi(veriler):
    """Portföy dağılım grafiği"""
    try:
        semboller = []
        degerler = []
        
        for sembol, bilgi in veriler["portfoy"].items():
            tip = bilgi.get('tip', 'hisse')
            adet = bilgi['adet']
            maliyet = bilgi['maliyet']
            
            guncel_fiyat = fiyat_sorgula(sembol, tip)
            if guncel_fiyat:
                deger = guncel_fiyat * adet
                semboller.append(sembol)
                degerler.append(deger)
        
        if semboller:
            plt.figure(figsize=(10, 8))
            plt.pie(degerler, labels=semboller, autopct='%1.1f%%', startangle=90)
            plt.title('Portföy Dağılımı', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            plt.savefig("portfoy_dagilim.png", dpi=100)
            plt.close()
            
            return True
    except:
        pass
    return False

# ========== ANA PROGRAM ==========
def main():
    veriler = verileri_yukle()
    trading_listesi = OtomatikTradingListesi()
    
    print(f"✅ AŞAMA 6 SİSTEMİ BAŞLATILDI!")
    print(f"📊 Portföyünüzde {len(veriler['portfoy'])} yatırım var\n")
    
    while True:
        print("\n" + "="*70)
        print("🤖 AŞAMA 6: TAM YAŞAYAN YAPAY ZEKA YATIRIM ASİSTANI")
        print("="*70)
        print("1 - Portföyü Görüntüle")
        print("2 - Yatırım Ekle")
        print("3 - Yatırım Sil")
        print("4 - GERÇEK TEKNİK ANALİZ (RSI, MACD, Bollinger)")
        print("5 - BACKTESTING (Geçmiş Performans)")
        print("6 - Fiyat Grafiği Çiz")
        print("7 - Portföy Dağılımı Grafiği")
        print("8 - Excel'e Aktar")
        print("9 - Otomatik Trading Siparişleri")
        print("10 - Çıkış")
        print("="*70)
        
        secim = input("Seçiminiz (1-10): ").strip()
        
        if secim == "1":
            print("\n💼 PORTFÖYÜNÜZ:")
            if not veriler["portfoy"]:
                print("Portföyünüz boş")
            else:
                for sembol, bilgi in veriler["portfoy"].items():
                    fiyat = fiyat_sorgula(sembol, bilgi.get('tip', 'hisse'))
                    if fiyat:
                        deger = fiyat * bilgi['adet']
                        maliyet = bilgi['maliyet'] * bilgi['adet']
                        kar_zarar = deger - maliyet
                        print(f"  {sembol}: {bilgi['adet']} adet @ ${fiyat:.2f} = ${deger:.2f} ({kar_zarar:+.2f})")
                        
        elif secim == "2":
            sembol = input("Sembol: ").upper()
            tip = input("Tip (hisse/kripto): ").lower()
            adet = float(input("Adet: "))
            maliyet = float(input("Maliyet: "))
            
            veriler["portfoy"][sembol] = {"tip": tip, "adet": adet, "maliyet": maliyet}
            verileri_kaydet(veriler)
            print(f"✅ {sembol} eklendi!")
            
        elif secim == "3":
            sembol = input("Silinecek sembol: ").upper()
            if sembol in veriler["portfoy"]:
                del veriler["portfoy"][sembol]
                verileri_kaydet(veriler)
                print(f"✅ {sembol} silindi!")
            else:
                print("❌ Bulunamadı")
                
        elif secim == "4":
            sembol = input("Sembol: ").upper()
            analiz = GercekTeknikAnaliz.tam_analiz(sembol)
            
            if analiz:
                print(f"\n📊 {sembol} GERÇEK TEKNİK ANALİZ:")
                print(f"   Güncel Fiyat: ${analiz['guncel_fiyat']:.2f}")
                print(f"   RSI: {analiz['rsi']:.1f}")
                print(f"   MACD: {analiz['macd']:.4f} | Signal: {analiz['signal']:.4f}")
                print(f"   Bollinger: ${analiz['bollinger_alt']:.2f} - ${analiz['bollinger_ust']:.2f}")
                print(f"   Trend: {analiz['trend']} ({analiz['trend_gucu']:.0f}%)")
                print("\n🎯 SİNYALLER:")
                for sinyal in analiz['sinyaller']:
                    print(f"   {sinyal}")
            else:
                print("❌ Veri alınamadı")
                
        elif secim == "5":
            sembol = input("Sembol: ").upper()
            backtest = Backtesting.basit_backtest(sembol)
            
            if backtest:
                print(f"\n📈 {sembol} BACKTESTİNG SONUÇLARI (90 Gün):")
                print(f"   Kar/Zarar: ${backtest['kar_zarar']:.2f}")
                print(f"   Getiri: {backtest['getiri_yuzde']:.2f}%")
                print(f"   Başarı: {'✅ KÂRLı' if backtest['basari'] else '❌ Zararlı'}")
            else:
                print("❌ Backtest yapılamadı")
                
        elif secim == "6":
            sembol = input("Sembol: ").upper()
            if grafik_ciz(sembol):
                print(f"✅ Grafik kaydedildi: grafik_{sembol}.png")
            else:
                print("❌ Grafik çizilemedi")
                
        elif secim == "7":
            if portfoy_dagılım_grafigi(veriler):
                print("✅ Portföy grafiği kaydedildi: portfoy_dagilim.png")
            else:
                print("❌ Grafik çizilemedi")
                
        elif secim == "8":
            msg = portfoy_excel_export(veriler)
            print(msg)
            
        elif secim == "9":
            sembol = input("Sembol: ").upper()
            islem = input("AL/SAT: ").upper()
            fiyat = float(input("Hedef Fiyat: "))
            
            if islem == "AL":
                if trading_listesi.al_emri_ekle(sembol, fiyat, 1000):
                    print("✅ AL EMRİ HAZIR!")
                else:
                    print("⏳ AL EMRİ BEKLEMEYE ALINDI")
            elif islem == "SAT":
                if trading_listesi.sat_emri_ekle(sembol, fiyat):
                    print("✅ SAT EMRİ HAZIR!")
                else:
                    print("⏳ SAT EMRİ BEKLEMEYE ALINDI")
                    
        elif secim == "10":
            print("👋 Güle güle!")
            break
        else:
            print("❌ Geçersiz seçim")

if __name__ == "__main__":
    main()
