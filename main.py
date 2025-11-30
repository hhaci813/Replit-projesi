import json
import pickle
import numpy as np
from datetime import datetime
from collections import Counter
import os


class OgrenenSistem:
    def __init__(self):
        self.veri_dosyasi = "ogrenme_verileri.json"
        self.model_dosyasi = "ogrenme_modeli.pkl"
        self.veriler = self.verileri_yukle()
        self.model = self.modeli_yukle()
        
    def verileri_yukle(self):
        """Kayıtlı verileri yükle"""
        try:
            with open(self.veri_dosyasi, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "ogrenme_verileri": [],
                "son_guncelleme": datetime.now().isoformat(),
                "toplam_ogrenme": 0
            }
    
    def modeli_yukle(self):
        """Kayıtlı modeli yükle"""
        try:
            with open(self.model_dosyasi, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {"ogrenilen_bilgiler": {}, "istatistikler": {}}
    
    def verileri_kaydet(self):
        """Verileri dosyaya kaydet"""
        with open(self.veri_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(self.veriler, f, ensure_ascii=False, indent=2)
    
    def modeli_kaydet(self):
        """Modeli dosyaya kaydet"""
        with open(self.model_dosyasi, 'wb') as f:
            pickle.dump(self.model, f)

    def bilgi_ekle(self, anahtar, deger):
        """Yeni bilgi ekle"""
        self.model["ogrenilen_bilgiler"][anahtar] = deger
        self.veriler["ogrenme_verileri"].append({
            "anahtar": anahtar,
            "deger": deger,
            "tarih": datetime.now().isoformat()
        })
        self.veriler["toplam_ogrenme"] += 1
        self.veriler["son_guncelleme"] = datetime.now().isoformat()
        print(f"Bilgi eklendi: {anahtar} = {deger}")

    def bilgi_getir(self, anahtar):
        """Kayıtlı bilgiyi getir"""
        return self.model["ogrenilen_bilgiler"].get(anahtar, None)

    def durum_goster(self):
        """Sistemin durumunu göster"""
        print("\n=== Öğrenen Sistem Durumu ===")
        print(f"Toplam öğrenme sayısı: {self.veriler['toplam_ogrenme']}")
        print(f"Son güncelleme: {self.veriler['son_guncelleme']}")
        print(f"Kayıtlı bilgi sayısı: {len(self.model['ogrenilen_bilgiler'])}")
        if self.model["ogrenilen_bilgiler"]:
            print("\nÖğrenilen Bilgiler:")
            for anahtar, deger in self.model["ogrenilen_bilgiler"].items():
                print(f"  - {anahtar}: {deger}")
        print("============================\n")


class AkilliOgrenenSistem(OgrenenSistem):
    def __init__(self):
        super().__init__()
    
    def yeni_veri_ekle(self, soru, cevap, kategori="genel"):
        """Sisteme yeni veri ekle"""
        yeni_veri = {
            "soru": soru,
            "cevap": cevap,
            "kategori": kategori,
            "zaman": datetime.now().isoformat(),
            "kullanım_sayisi": 0
        }
        
        self.veriler["ogrenme_verileri"].append(yeni_veri)
        self.veriler["toplam_ogrenme"] += 1
        self.veriler["son_guncelleme"] = datetime.now().isoformat()
        
        self.model_guncelle(soru, cevap, kategori)
        
        self.verileri_kaydet()
        self.modeli_kaydet()
        
        print(f"Yeni bilgi ogrenildi: {soru} -> {cevap}")
    
    def model_guncelle(self, soru, cevap, kategori):
        """Öğrenme modelini güncelle"""
        if kategori not in self.model["ogrenilen_bilgiler"]:
            self.model["ogrenilen_bilgiler"][kategori] = {}
        
        anahtar_kelimeler = soru.lower().split()
        for kelime in anahtar_kelimeler:
            if len(kelime) > 2:
                if kelime not in self.model["ogrenilen_bilgiler"][kategori]:
                    self.model["ogrenilen_bilgiler"][kategori][kelime] = []
                
                if cevap not in self.model["ogrenilen_bilgiler"][kategori][kelime]:
                    self.model["ogrenilen_bilgiler"][kategori][kelime].append(cevap)
    
    def cevap_ver(self, soru):
        """Soruyu değerlendir ve cevap ver"""
        soru_lower = soru.lower()
        bulunan_cevaplar = []
        
        for kategori, bilgiler in self.model["ogrenilen_bilgiler"].items():
            if isinstance(bilgiler, dict):
                for kelime, cevaplar in bilgiler.items():
                    if isinstance(cevaplar, list) and kelime in soru_lower:
                        bulunan_cevaplar.extend(cevaplar)
        
        if bulunan_cevaplar:
            cevap_sayilari = Counter(bulunan_cevaplar)
            en_iyi_cevap = cevap_sayilari.most_common(1)[0][0]
            
            self.kullanim_istatistigi_guncelle(soru_lower, en_iyi_cevap)
            
            return en_iyi_cevap
        else:
            return "Bu konuyu henuz ogrenmedim. Bana ogretmek ister misin?"
    
    def kullanim_istatistigi_guncelle(self, soru, cevap):
        """Kullanım istatistiklerini güncelle"""
        for veri in self.veriler["ogrenme_verileri"]:
            if "soru" in veri and veri["soru"].lower() == soru and veri.get("cevap") == cevap:
                veri["kullanım_sayisi"] = veri.get("kullanım_sayisi", 0) + 1
                break
        
        self.verileri_kaydet()
    
    def durum_goster(self):
        """Akıllı sistemin durumunu göster"""
        print("\n=== Akilli Ogrenen Sistem Durumu ===")
        print(f"Toplam ogrenme sayisi: {self.veriler['toplam_ogrenme']}")
        print(f"Son guncelleme: {self.veriler['son_guncelleme']}")
        
        kategori_sayisi = sum(1 for k, v in self.model["ogrenilen_bilgiler"].items() if isinstance(v, dict))
        print(f"Kategori sayisi: {kategori_sayisi}")
        
        if self.model["ogrenilen_bilgiler"]:
            print("\nKategoriler ve Bilgiler:")
            for kategori, bilgiler in self.model["ogrenilen_bilgiler"].items():
                if isinstance(bilgiler, dict):
                    print(f"\n  [{kategori.upper()}]")
                    for kelime, cevaplar in bilgiler.items():
                        if isinstance(cevaplar, list):
                            for cevap in cevaplar:
                                print(f"    - {kelime}: {cevap}")
        print("=====================================\n")


class GelismisOgrenenSistem(AkilliOgrenenSistem):
    def __init__(self):
        super().__init__()
        self.otomatik_yedekleme()
    
    def otomatik_yedekleme(self):
        """Otomatik yedekleme oluştur"""
        import shutil
        import time
        
        try:
            son_yedekleme = self.veriler.get("son_yedekleme", 0)
            simdiki_zaman = time.time()
            
            if simdiki_zaman - son_yedekleme > 604800:  # 7 gun
                if os.path.exists(self.veri_dosyasi):
                    yedek_dosya = f"yedek_{int(simdiki_zaman)}.json"
                    shutil.copy2(self.veri_dosyasi, yedek_dosya)
                    self.veriler["son_yedekleme"] = simdiki_zaman
                    self.verileri_kaydet()
                    print("Otomatik yedekleme tamamlandi")
                
        except Exception as e:
            print(f"Yedekleme hatasi: {e}")
    
    def bilgi_sil(self, soru):
        """Öğrenilmiş bilgiyi sil"""
        onceki_sayi = len(self.veriler["ogrenme_verileri"])
        self.veriler["ogrenme_verileri"] = [
            v for v in self.veriler["ogrenme_verileri"] 
            if not ("soru" in v and v["soru"].lower() == soru.lower())
        ]
        
        silinen = onceki_sayi - len(self.veriler["ogrenme_verileri"])
        if silinen > 0:
            self.veriler["toplam_ogrenme"] -= silinen
            self.verileri_kaydet()
            self.modeli_yeniden_olustur()
            print(f"'{soru}' bilgisi silindi")
        else:
            print(f"'{soru}' bulunamadi")
    
    def modeli_yeniden_olustur(self):
        """Modeli sıfırdan oluştur"""
        self.model = {"ogrenilen_bilgiler": {}, "istatistikler": {}}
        
        for veri in self.veriler["ogrenme_verileri"]:
            if "soru" in veri:
                self.model_guncelle(veri["soru"], veri["cevap"], veri.get("kategori", "genel"))
        
        self.modeli_kaydet()


def main():
    print("Akilli Ogrenen Sisteme Hos Geldiniz!")
    print("=" * 50)
    
    sistem = AkilliOgrenenSistem()
    
    print(f"Sistem durumu: {len(sistem.veriler['ogrenme_verileri'])} bilgi yuklendi")
    print("Komutlar: 'cikis', 'durum', 'liste', 'ogret <soru> -> <cevap>'")
    print("=" * 50)
    
    while True:
        try:
            kullanici_girdisi = input("\nSen: ").strip()
            
            if not kullanici_girdisi:
                continue
            
            if kullanici_girdisi.lower() in ['cikis', 'çıkış', 'exit', 'quit']:
                print("Gorusmek uzere! Ogrendiklerim kaydedildi.")
                break
            
            elif kullanici_girdisi.lower() == 'durum':
                print(f"Ogrenme Durumu:")
                print(f"   - Toplam bilgi: {sistem.veriler['toplam_ogrenme']}")
                print(f"   - Son guncelleme: {sistem.veriler['son_guncelleme']}")
                kategoriler = [k for k, v in sistem.model['ogrenilen_bilgiler'].items() if isinstance(v, dict)]
                print(f"   - Kategoriler: {kategoriler}")
            
            elif kullanici_girdisi.lower() == 'liste':
                print("Ogrenilen Bilgiler (son 10):")
                son_veriler = [v for v in sistem.veriler["ogrenme_verileri"] if "soru" in v][-10:]
                if son_veriler:
                    for i, veri in enumerate(son_veriler, 1):
                        kullanim = veri.get('kullanım_sayisi', 0)
                        print(f"   {i}. {veri['soru']} -> {veri['cevap']} (Kullanim: {kullanim})")
                else:
                    print("   Henuz soru-cevap verisi yok.")
            
            elif kullanici_girdisi.lower().startswith('ogret ') or kullanici_girdisi.lower().startswith('öğret '):
                try:
                    _, ogretme_verisi = kullanici_girdisi.split(' ', 1)
                    if '->' in ogretme_verisi:
                        soru, cevap = ogretme_verisi.split('->', 1)
                        sistem.yeni_veri_ekle(soru.strip(), cevap.strip())
                    else:
                        print("Hatali format! Dogru kullanim: ogret <soru> -> <cevap>")
                except ValueError:
                    print("Hatali format! Dogru kullanim: ogret <soru> -> <cevap>")
            
            else:
                cevap = sistem.cevap_ver(kullanici_girdisi)
                print(f"Bot: {cevap}")
                
        except KeyboardInterrupt:
            print("\nGorusmek uzere! Veriler kaydedildi.")
            break
        except EOFError:
            print("\nOturum sonlandirildi.")
            break
        except Exception as e:
            print(f"Bir hata olustu: {e}")


if __name__ == "__main__":
    print("Replit kalici depolama kullaniliyor...")
    main()
