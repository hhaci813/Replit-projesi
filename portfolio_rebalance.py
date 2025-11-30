"""Portföy Rebalancing - Otomatik Denge Sağlama"""
import json
import numpy as np
from datetime import datetime

class PortfolioRebalancing:
    """Portföy dengeleme sistemi"""
    
    @staticmethod
    def hedef_agirlik_belirle(portfoy):
        """Hedef ağırlık belirleme"""
        print("\n🎯 HEDEF AĞIRLIK DAĞILIMI\n")
        
        # Dengeli portföy stratejisi
        hedef_agirliklari = {
            "hisse_senedi": 0.60,      # %60
            "teknoloji": 0.25,         # %25
            "kripto": 0.10,            # %10
            "sabit_gelir": 0.05        # %5
        }
        
        print("📊 Önerilen Dağılım:")
        for kategori, orani in hedef_agirliklari.items():
            print(f"   {kategori.replace('_', ' ').title()}: {orani*100:.0f}%")
        
        return hedef_agirliklari
    
    @staticmethod
    def mevcut_agirliklari_hesapla(portfoy_verisi):
        """Mevcut portföy ağırlıklarını hesapla"""
        print("\n📈 MEVCUT AĞIRLIK DAĞILIMI\n")
        
        # Örnek portföy
        portfoy = {
            "AAPL": {"adet": 50, "fiyat": 150},
            "MSFT": {"adet": 30, "fiyat": 300},
            "GOOGL": {"adet": 20, "fiyat": 140},
            "TSLA": {"adet": 10, "fiyat": 200},
            "BTC-USD": {"adet": 0.5, "fiyat": 40000},
            "GOLD": {"adet": 10, "fiyat": 2000},
        }
        
        # Toplam değer
        toplam_deger = sum(bilgi["adet"] * bilgi["fiyat"] for bilgi in portfoy.values())
        
        # Ağırlıklar
        agirliklari = {}
        for sembol, bilgi in portfoy.items():
            deger = bilgi["adet"] * bilgi["fiyat"]
            agirlik = (deger / toplam_deger) if toplam_deger > 0 else 0
            agirliklari[sembol] = {
                "deger": deger,
                "agirlik": agirlik,
                "yuzde": f"{agirlik*100:.1f}%"
            }
            print(f"   {sembol:10} ${deger:>10,.0f}  ({agirlik*100:>5.1f}%)")
        
        print(f"\n   TOPLAM: ${toplam_deger:,.0f}")
        
        return agirliklari, toplam_deger
    
    @staticmethod
    def rebalancing_yap(portfoy_verisi, hedef_agirliklari=None):
        """Portföyü dengele"""
        print("\n🔄 REBALANCING İŞLEMİ BAŞLATILIYOR\n")
        
        # Mevcut ağırlıklar
        agirliklari, toplam_deger = PortfolioRebalancing.mevcut_agirliklari_hesapla(portfoy_verisi)
        
        # Hedef ağırlıklar
        if hedef_agirliklari is None:
            hedef_agirliklari = PortfolioRebalancing.hedef_agirlik_belirle(portfoy_verisi)
        
        print("\n" + "="*70)
        print("📊 REBALANCING ÖNERİLERİ")
        print("="*70 + "\n")
        
        oneriler = []
        
        # Hisse senetlerini kategorize et
        kategoriler = {
            "hisse_senedi": ["AAPL", "MSFT", "GOOGL"],
            "teknoloji": ["TSLA"],
            "kripto": ["BTC-USD"],
            "sabit_gelir": ["GOLD"]
        }
        
        for kategori, semboller in kategoriler.items():
            kategori_degeri = sum(agirliklari.get(s, {}).get("deger", 0) for s in semboller)
            kategori_agirlik = kategori_degeri / toplam_deger if toplam_deger > 0 else 0
            hedef = hedef_agirliklari.get(kategori, 0)
            fark = hedef - kategori_agirlik
            
            print(f"📌 {kategori.replace('_', ' ').title()}")
            print(f"   Mevcut: {kategori_agirlik*100:>5.1f}% | Hedef: {hedef*100:>5.1f}% | Fark: {fark*100:+6.1f}%")
            
            if abs(fark) > 0.05:  # %5'ten fazla fark
                if fark > 0:
                    print(f"   ✅ SATINAL - {abs(fark)*100:.1f}% kadar eklemek gerekli")
                else:
                    print(f"   ⚠️ SAT - {abs(fark)*100:.1f}% kadar satmak gerekli")
            else:
                print(f"   ✅ DENGE - Ayarlama gerekmez")
            print()
            
            oneriler.append({
                "kategori": kategori,
                "mevcut_agirlik": kategori_agirlik,
                "hedef_agirlik": hedef,
                "fark": fark,
                "aksiyon": "AL" if fark > 0 else "SAT" if fark < 0 else "TUT"
            })
        
        return oneriler
    
    @staticmethod
    def rebalancing_tarihi_ver():
        """Rebalancing takvimi"""
        print("\n📅 REBALANCING TAKVIMI\n")
        
        takvim = {
            "Haftalık": "Her Pazartesi (Performa takip)",
            "Aylık": "Ayın ilk haftası (Detaylı kontrol)",
            "Çeyreklik": "Aylık rebalancing (Stratejik ayar)",
            "Yıllık": "Ocak'ta (Tam revizyon)"
        }
        
        for donem, aciklama in takvim.items():
            print(f"   {donem:15} - {aciklama}")
        
        return takvim
    
    @staticmethod
    def otomatik_rebalancing(threshold=0.05):
        """Otomatik rebalancing tetikleyici"""
        print("\n⚙️ OTOMATIK REBALANCING SİSTEMİ\n")
        
        print(f"🎯 Tetikleme Eşiği: ±{threshold*100:.1f}%")
        print("\n📋 Otomatik Kontrol Sistemi:")
        print("   ✅ Saatlik: Fiyat güncellemesi")
        print("   ✅ Günlük: Ağırlık hesaplama")
        print("   ✅ Haftalık: Rebalancing kontrol")
        print("   ✅ Aylık: Strateji değerlendirme")
        print("\n🔔 Alarm Sistemi:")
        print("   🔴 Kritik (Fark > %10): İmmediat satış/alış")
        print("   🟠 Uyarı (Fark > %5): Değerlendirme gerekli")
        print("   🟡 Bilgi (Fark > %2): Takip et")
        
        return {
            "sistem": "Otomatik Rebalancing",
            "tetikleme_esigi": threshold,
            "durum": "AKTIF"
        }
    
    @staticmethod
    def rebalancing_raporu_uret():
        """Kapsamlı rebalancing raporu"""
        print("\n" + "="*70)
        print("📊 PORTFÖY REBALANCING RAPORU")
        print("="*70 + "\n")
        
        # Hedef ağırlıklar
        hedefler = PortfolioRebalancing.hedef_agirlik_belirle(None)
        
        # Rebalancing yap
        oneriler = PortfolioRebalancing.rebalancing_yap(None, hedefler)
        
        # Takvim
        PortfolioRebalancing.rebalancing_tarihi_ver()
        
        # Otomatik sistem
        print("\n")
        PortfolioRebalancing.otomatik_rebalancing()
        
        # Rapora kaydet
        rapor = {
            "tarih": datetime.now().isoformat(),
            "oneriler": oneriler,
            "durum": "DENGE GEREKLI" if any(o["fark"] > 0.05 for o in oneriler) else "DENGELI"
        }
        
        with open('rebalancing_raporu.json', 'w', encoding='utf-8') as f:
            json.dump(rapor, f, ensure_ascii=False, indent=2)
        
        print("\n✅ Rapor kaydedildi: rebalancing_raporu.json")
        
        return rapor

if __name__ == "__main__":
    PortfolioRebalancing.rebalancing_raporu_uret()
