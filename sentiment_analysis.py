"""Sosyal Medya Sentiment Analizi - Twitter, Reddit, News"""
from textblob import TextBlob
import json
from datetime import datetime

class SocialSentiment:
    @staticmethod
    def metni_analiz_et(metin):
        """Metni duygusal analiz et"""
        try:
            blob = TextBlob(metin)
            polarity = blob.sentiment.polarity  # -1 (negatif) ile +1 (pozitif) arası
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                duygu = "🟢 POZİTİF"
            elif polarity < -0.1:
                duygu = "🔴 NEGATİF"
            else:
                duygu = "🟡 NÖTR"
            
            return {
                "metin": metin,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "duygu": duygu,
                "kuvvet": "Kuvvetli" if abs(polarity) > 0.7 else "Orta" if abs(polarity) > 0.3 else "Zayıf"
            }
        except:
            return {"duygu": "❌ Hata", "polarity": 0}
    
    @staticmethod
    def finansal_haberler_analiz(haberler):
        """Finansal haberleri analiz et"""
        print("\n📰 FİNANSAL HABERLER SENTIMENT ANALIZI\n")
        
        sample_haberler = [
            ("AAPL hisse fiyatı yükselişe geçti, yatırımcılar iyimser", "AAPL"),
            ("Tesla satışları düşüş gösteriyor, endişeli pazar", "TSLA"),
            ("Microsoft yeni AI ürünü duyurdu, olumlu tepki", "MSFT"),
            ("Crypto piyasası çöküş yaşıyor, kaçış başladı", "BTC"),
        ]
        
        analiz_sonuclari = []
        for haber, sembol in sample_haberler:
            result = SocialSentiment.metni_analiz_et(haber)
            analiz_sonuclari.append({
                "sembol": sembol,
                "haber": haber,
                "sentiment": result["duygu"],
                "güç": result["kuvvet"],
                "skor": f"{result['polarity']:.2f}"
            })
            print(f"📊 {sembol}: {result['duygu']} (Güç: {result['kuvvet']}, Skor: {result['polarity']:.2f})")
            print(f"   📰 {haber}\n")
        
        # CSV'ye kaydet
        with open('sentiment_analizi.json', 'w', encoding='utf-8') as f:
            json.dump({
                "tarih": datetime.now().isoformat(),
                "haberler": analiz_sonuclari
            }, f, ensure_ascii=False)
        
        return analiz_sonuclari
    
    @staticmethod
    def trend_analizi():
        """Market trend sentiment'i"""
        print("\n📈 PAZAR TREND SENTIMENT SKORU\n")
        
        trend_skorlari = {
            "Hisse Senetleri": 0.65,      # Pozitif
            "Kripto": -0.45,              # Negatif
            "Teknoloji": 0.72,            # Çok Pozitif
            "Enerji": 0.15,               # Nötr eğilimli pozitif
            "İmalat": -0.20               # Nötr eğilimli negatif
        }
        
        for sektor, skor in trend_skorlari.items():
            if skor > 0.5:
                emoji = "🟢"
                durum = "GÜÇLÜ POZİTİF"
            elif skor > 0:
                emoji = "🟢"
                durum = "POZİTİF"
            elif skor > -0.3:
                emoji = "🟡"
                durum = "NÖTR"
            else:
                emoji = "🔴"
                durum = "NEGATİF"
            
            print(f"{emoji} {sektor:20} | {durum:15} | Skor: {skor:+.2f}")
        
        return trend_skorlari
    
    @staticmethod
    def sembol_duygu_skoru(sembol):
        """Sembol için market duygusunu hesapla"""
        sample_data = {
            "AAPL": 0.78,
            "MSFT": 0.72,
            "GOOGL": 0.65,
            "TSLA": -0.15,
            "AMZN": 0.55,
            "BTC-USD": -0.20,
            "ETH-USD": 0.10,
        }
        
        skor = sample_data.get(sembol, 0.0)
        
        if skor > 0.6:
            tavsiye = "🟢 AL - Pazar çok iyimser"
        elif skor > 0.2:
            tavsiye = "🟢 AL - Hafif pozitif hava"
        elif skor > -0.2:
            tavsiye = "🟡 TUT - Nötr pazar hissiyatı"
        else:
            tavsiye = "🔴 SAT - Pazar endişeli"
        
        return {
            "sembol": sembol,
            "duygu_skoru": skor,
            "tavsiye": tavsiye,
            "tarih": datetime.now().isoformat()
        }

if __name__ == "__main__":
    SocialSentiment.finansal_haberler_analiz([])
    SocialSentiment.trend_analizi()
    print("\n" + "="*50)
    print("✅ AAPL Sentiment:", SocialSentiment.sembol_duygu_skoru("AAPL")["tavsiye"])


class SentimentAnalyzer:
    """Sentiment Analysis - Market Emotion"""
    
    def __init__(self):
        self.sentiment_history = {}
    
    def analyze_sentiment(self, text):
        """Metni analiz et"""
        try:
            blob = TextBlob(text)
            polarity = float(blob.sentiment.polarity) if hasattr(blob.sentiment, 'polarity') else 0
            subjectivity = float(blob.sentiment.subjectivity) if hasattr(blob.sentiment, 'subjectivity') else 0
            
            if polarity > 0.1:
                sentiment = "🟢 POZITIF"
            elif polarity < -0.1:
                sentiment = "🔴 NEGATİF"
            else:
                sentiment = "⚪ NÖTR"
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'score': polarity * 100
            }
        except:
            return {'sentiment': '⚪ NÖTR', 'polarity': 0, 'subjectivity': 0, 'score': 0}
    
    def get_market_emotion(self):
        """Pazar duygusu"""
        return {
            'market_emotion': {'Fear': 25, 'Greed': 65, 'Neutral': 10},
            'dominant': 'Greed',
            'recommendation': '⚠️ Dikkat - Çok Greed'
        }
