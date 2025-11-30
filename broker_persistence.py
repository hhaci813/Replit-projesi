"""Broker İşlemleri - Kalıcı Depolama Sistemi"""
import json
import os
from datetime import datetime

class BrokerPersistence:
    def __init__(self):
        self.broker_data_file = "broker_islemler.json"
        self.users_file = "broker_kullanicilar.json"
        self.load_or_create_data()
    
    def load_or_create_data(self):
        """Verileri yükle veya oluştur"""
        if not os.path.exists(self.broker_data_file):
            self.create_initial_data()
        if not os.path.exists(self.users_file):
            self.create_users()
    
    def create_initial_data(self):
        """İlk veriyi oluştur"""
        data = {
            "islemler": [],
            "bakiye": {"alpaca": 100000, "binance": 10},
            "pozisyonlar": {"alpaca": {}, "binance": {}},
            "son_guncelleme": datetime.now().isoformat()
        }
        with open(self.broker_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_users(self):
        """Kullanıcı sistemi oluştur"""
        users = {
            "default": {
                "username": "default",
                "password": "1234",
                "alpaca_key": "DEMO",
                "binance_key": "DEMO",
                "portfoy": {},
                "islemler": [],
                "created": datetime.now().isoformat()
            }
        }
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def kullanici_giris(self, username, password):
        """Kullanıcı girişi"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            if username in users and users[username]['password'] == password:
                return True, f"✅ Hoşgeldin {username}!"
            else:
                return False, "❌ Kullanıcı adı veya şifre yanlış"
        except:
            return False, "❌ Giriş sistemi hatası"
    
    def islem_kaydet(self, broker, islem_tipi, sembol, miktar, fiyat=0):
        """İşlemi kaydet"""
        try:
            with open(self.broker_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            islem = {
                "id": len(data["islemler"]) + 1,
                "broker": broker,
                "tipi": islem_tipi,
                "sembol": sembol,
                "miktar": miktar,
                "fiyat": fiyat,
                "zaman": datetime.now().isoformat(),
                "status": "tamam"
            }
            
            data["islemler"].append(islem)
            data["son_guncelleme"] = datetime.now().isoformat()
            
            with open(self.broker_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True, f"✅ İşlem #{islem['id']} kaydedildi"
        except Exception as e:
            return False, f"❌ Kayıt hatası: {str(e)}"
    
    def pozisyon_kaydet(self, broker, sembol, miktar, ort_fiyat):
        """Pozisyonu kaydet"""
        try:
            with open(self.broker_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data["pozisyonlar"][broker][sembol] = {
                "miktar": miktar,
                "ort_fiyat": ort_fiyat,
                "zaman": datetime.now().isoformat()
            }
            
            with open(self.broker_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except:
            return False
    
    def islem_gecmisi_goster(self):
        """İşlem geçmişini göster"""
        try:
            with open(self.broker_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            islemler = data.get("islemler", [])
            if not islemler:
                return "📋 İşlem geçmişi boş"
            
            sonuc = "📋 İŞLEM GEÇMİŞİ:\n\n"
            for islem in islemler[-10:]:  # Son 10 işlem
                sonuc += f"#{islem['id']} - {islem['zaman'][:10]}\n"
                sonuc += f"   {islem['broker'].upper()}: {islem['tipi']} {islem['sembol']} x{islem['miktar']}\n"
                sonuc += f"   Status: {islem['status']}\n\n"
            
            return sonuc
        except:
            return "❌ Geçmiş alınamadı"
    
    def pozisyon_goster(self):
        """Mevcut pozisyonları göster"""
        try:
            with open(self.broker_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sonuc = "📊 MEVCUT POZİSYONLAR:\n\n"
            
            for broker in ["alpaca", "binance"]:
                pozisyonlar = data["pozisyonlar"].get(broker, {})
                if pozisyonlar:
                    sonuc += f"🔹 {broker.upper()}:\n"
                    for sembol, pos in pozisyonlar.items():
                        sonuc += f"   • {sembol}: {pos['miktar']} @ ${pos['ort_fiyat']}\n"
                    sonuc += "\n"
            
            return sonuc if "MEVCUT" in sonuc else "Hiç pozisyon yok"
        except:
            return "❌ Pozisyon alınamadı"
    
    def bakiye_goster(self):
        """Bakiye göster"""
        try:
            with open(self.broker_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            bakiye = data.get("bakiye", {})
            sonuc = "💰 BROKER BAKİYESİ:\n\n"
            sonuc += f"Alpaca (Hisse): ${bakiye.get('alpaca', 0):,.0f}\n"
            sonuc += f"Binance (Kripto): ₿{bakiye.get('binance', 0)}\n"
            return sonuc
        except:
            return "❌ Bakiye alınamadı"

if __name__ == "__main__":
    persistence = BrokerPersistence()
    print("✅ Broker Persistence Sistemi Hazır")
