"""📰 Expert Sentiment Extractor - Yorumcuların analizleri"""
import requests
import re
from textblob import TextBlob
from datetime import datetime, timedelta
import os

class ExpertSentimentExtractor:
    """Haberlerden expert sentiment çıkart"""
    
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
    
    def extract_expert_opinions(self, query, days=7):
        """Expert yorumlarını topla"""
        try:
            if not self.newsapi_key:
                return {'error': 'NewsAPI key missing', 'opinions': []}
            
            url = "https://newsapi.org/v2/everything"
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            params = {
                'q': f"{query} analysis forecast recommendation",
                'sortBy': 'relevancy',
                'language': 'en',
                'from': from_date,
                'apiKey': self.newsapi_key,
                'pageSize': 15
            }
            
            response = requests.get(url, params=params, timeout=10)
            articles = response.json().get('articles', [])
            
            opinions = []
            for article in articles:
                text = f"{article.get('title', '')} {article.get('description', '')}"
                
                # Sentiment analizi
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                # Expert çıkart - author veya source'dan
                author = article.get('author', 'Unknown')
                source = article.get('source', {}).get('name', 'Unknown')
                
                # Recommendation çıkart
                recommendation = self._extract_recommendation(text, polarity)
                
                opinions.append({
                    'title': article.get('title', 'N/A'),
                    'source': source,
                    'author': author,
                    'url': article.get('url', '#'),
                    'published': article.get('publishedAt', 'N/A'),
                    'sentiment': 'POSITIVE' if polarity > 0.1 else ('NEGATIVE' if polarity < -0.1 else 'NEUTRAL'),
                    'polarity': polarity,
                    'recommendation': recommendation,
                    'emoji': self._sentiment_emoji(polarity)
                })
            
            return {
                'query': query,
                'total_articles': len(opinions),
                'opinions': opinions,
                'consensus': self._calculate_consensus(opinions)
            }
        
        except Exception as e:
            print(f"❌ Expert extraction error: {e}")
            return {'error': str(e), 'opinions': []}
    
    @staticmethod
    def _extract_recommendation(text, polarity):
        """Recommendation çıkart"""
        text_lower = text.lower()
        
        # Keywords
        if any(word in text_lower for word in ['buy', 'bullish', 'target', 'increase', 'outperform', 'accumulate']):
            return 'BUY'
        elif any(word in text_lower for word in ['sell', 'bearish', 'decline', 'reduce', 'underperform', 'dump']):
            return 'SELL'
        elif any(word in text_lower for word in ['hold', 'neutral', 'equal', 'maintain']):
            return 'HOLD'
        else:
            return 'BUY' if polarity > 0.2 else ('SELL' if polarity < -0.2 else 'HOLD')
    
    @staticmethod
    def _sentiment_emoji(polarity):
        """Sentiment emoji"""
        if polarity > 0.3:
            return "🟢🟢"
        elif polarity > 0.1:
            return "🟢"
        elif polarity < -0.3:
            return "🔴🔴"
        elif polarity < -0.1:
            return "🔴"
        else:
            return "🟡"
    
    @staticmethod
    def _calculate_consensus(opinions):
        """Consensus hesapla"""
        if not opinions:
            return 'NEUTRAL'
        
        buy_count = len([o for o in opinions if o['recommendation'] == 'BUY'])
        sell_count = len([o for o in opinions if o['recommendation'] == 'SELL'])
        hold_count = len([o for o in opinions if o['recommendation'] == 'HOLD'])
        
        if buy_count > sell_count and buy_count > hold_count:
            return 'STRONG_BUY'
        elif sell_count > buy_count and sell_count > hold_count:
            return 'STRONG_SELL'
        elif buy_count > sell_count:
            return 'BUY'
        elif sell_count > buy_count:
            return 'SELL'
        else:
            return 'HOLD'

if __name__ == "__main__":
    extractor = ExpertSentimentExtractor()
    result = extractor.extract_expert_opinions("Apple stock", days=7)
    print(f"Total opinions: {result.get('total_articles')}")
    print(f"Consensus: {result.get('consensus')}")
