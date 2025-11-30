import json
import pickle
import numpy as np
from datetime import datetime
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


if __name__ == "__main__":
    print("Öğrenen Sistem başlatılıyor...")
    sistem = OgrenenSistem()
    
    sistem.bilgi_ekle("merhaba", "Türkçe selamlama")
    sistem.bilgi_ekle("numpy_versiyon", np.__version__)
    sistem.bilgi_ekle("python_bilgisi", "Programlama dili")
    
    sistem.durum_goster()
    
    sistem.verileri_kaydet()
    sistem.modeli_kaydet()
    
    print("Veriler ve model kaydedildi!")
