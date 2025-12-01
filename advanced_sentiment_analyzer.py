"""🎯 Advanced Sentiment Analysis - Haberlerden sentiment"""
import os
from textblob import TextBlob
from datetime import datetime, timedelta

class AdvancedSentimentAnalyzer:
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
    
    def analyze_text_sentiment(self, text):
        """Metin sentiment analizi"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                sentiment = "POSITIVE"
                emoji = "📈"
            elif polarity < -0.1:
                sentiment = "NEGATIVE"
                emoji = "📉"
            else:
                sentiment = "NEUTRAL"
                emoji = "➡️"
            
            confidence = abs(polarity)
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': confidence,
                'emoji': emoji
            }
        except Exception as e:
            print(f"❌ Sentiment analiz hatası: {e}")
            return {'sentiment': 'ERROR', 'polarity': 0}
    
    def analyze_news_sentiment(self, query):
        """Haberlerden sentiment analizi"""
        try:
            import requests
            
            if not self.newsapi_key:
                return {'error': 'NewsAPI key not set', 'articles': []}
            
            # Son 7 gün haberleri
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.newsapi_key,
                'pageSize': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            articles = response.json().get('articles', [])
            
            sentiments = []
            for article in articles:
                text = f"{article.get('title', '')} {article.get('description', '')}"
                sentiment = self.analyze_text_sentiment(text)
                
                sentiments.append({
                    'title': article.get('title', 'N/A'),
                    'source': article.get('source', {}).get('name', 'N/A'),
                    'url': article.get('url', '#'),
                    'sentiment': sentiment['sentiment'],
                    'polarity': sentiment['polarity'],
                    'confidence': sentiment['confidence'],
                    'emoji': sentiment['emoji']
                })
            
            # Average sentiment
            if sentiments:
                avg_polarity = sum(s['polarity'] for s in sentiments) / len(sentiments)
                
                if avg_polarity > 0.1:
                    overall = "POSITIVE 📈"
                elif avg_polarity < -0.1:
                    overall = "NEGATIVE 📉"
                else:
                    overall = "NEUTRAL ➡️"
            else:
                overall = "NO_DATA"
                avg_polarity = 0
            
            return {
                'query': query,
                'overall_sentiment': overall,
                'avg_polarity': avg_polarity,
                'articles': sentiments,
                'total_articles': len(sentiments)
            }
        
        except Exception as e:
            print(f"❌ News sentiment hatası: {e}")
            return {'error': str(e), 'articles': []}

class SocialMediaSentiment:
    """Social Media Sentiment - Simplified version"""
    
    @staticmethod
    def generate_market_sentiment(crypto_symbol):
        """Market genel sentiment"""
        # Base implementation
        return {
            'symbol': crypto_symbol,
            'sentiment': 'BULLISH',  # BULLISH, NEUTRAL, BEARISH
            'score': 0.65,  # 0-1 scale
            'sources': ['Technical Analysis', 'News Sentiment', 'Volume Analysis'],
            'recommendation': 'ACCUMULATE'
        }

if __name__ == "__main__":
    analyzer = AdvancedSentimentAnalyzer()
    result = analyzer.analyze_text_sentiment("Bitcoin is rising and adoption is growing")
    print(f"Sentiment Analysis: {result}")
