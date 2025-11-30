"""Sosyal Duygu Analizi"""
from textblob import TextBlob
import requests

class SocialSentiment:
    @staticmethod
    def analyze_sentiment(text):
        """Metin duygusunu analiz et"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        
        if polarity > 0.1:
            sentiment = "🟢 Pozitif"
        elif polarity < -0.1:
            sentiment = "🔴 Negatif"
        else:
            sentiment = "🟡 Nötr"
        
        return {
            "polarity": polarity,
            "sentiment": sentiment,
            "confidence": abs(polarity)
        }
    
    @staticmethod
    def get_market_sentiment(symbol):
        """Pazar duygusu simüle et"""
        sentiments = {
            "AAPL": "🟢 Pozitif (Yeni ürün beklentisi)",
            "MSFT": "🟢 Pozitif (AI yatırımı)",
            "TSLA": "🟡 Nötr (Karışık göstergeler)",
            "BTC": "🟢 Pozitif (Kurumsal ilgi)",
            "ETH": "🟡 Nötr (Düzeltme beklentisi)"
        }
        return sentiments.get(symbol, "Veri yok")
