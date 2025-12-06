"""📰 NEWS SENTIMENT ANALYZER - HABER DUYGU ANALİZİ
Kripto haberlerinden sentiment analizi
"""
import requests
from datetime import datetime
from textblob import TextBlob
import feedparser

class NewsSentimentAnalyzer:
    """Haber sentiment analizi"""
    
    def __init__(self):
        self.rss_feeds = [
            'https://cointelegraph.com/rss',
            'https://bitcoinmagazine.com/.rss/full/',
            'https://cryptonews.com/news/feed/',
        ]
    
    def fetch_crypto_news(self, keyword='bitcoin', limit=20):
        """RSS'den kripto haberleri çek"""
        all_news = []
        
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:limit]:
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    
                    if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                        all_news.append({
                            'title': title,
                            'summary': summary[:200],
                            'source': feed_url.split('/')[2],
                            'published': entry.get('published', '')
                        })
            except:
                continue
        
        return all_news[:limit]
    
    def analyze_sentiment(self, text):
        """TextBlob ile sentiment analizi"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            if polarity > 0.2:
                sentiment = 'POSITIVE'
            elif polarity < -0.2:
                sentiment = 'NEGATIVE'
            else:
                sentiment = 'NEUTRAL'
            
            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'sentiment': sentiment
            }
        except:
            return {'polarity': 0, 'subjectivity': 0, 'sentiment': 'NEUTRAL'}
    
    def get_market_sentiment(self, keyword='crypto'):
        """Genel piyasa sentiment'i al"""
        news = self.fetch_crypto_news(keyword, limit=15)
        
        if not news:
            return {
                'sentiment': 'NEUTRAL',
                'score': 50,
                'news_count': 0,
                'message': 'Haber bulunamadı'
            }
        
        total_polarity = 0
        sentiments = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
        analyzed_news = []
        
        for article in news:
            text = f"{article['title']} {article['summary']}"
            analysis = self.analyze_sentiment(text)
            
            total_polarity += analysis['polarity']
            sentiments[analysis['sentiment']] += 1
            
            analyzed_news.append({
                'title': article['title'][:80],
                'sentiment': analysis['sentiment'],
                'polarity': analysis['polarity']
            })
        
        avg_polarity = total_polarity / len(news)
        
        # Skor hesapla (0-100)
        score = int((avg_polarity + 1) * 50)  # -1,1 -> 0,100
        
        # Genel sentiment
        if avg_polarity > 0.15:
            overall = 'BULLISH'
        elif avg_polarity < -0.15:
            overall = 'BEARISH'
        else:
            overall = 'NEUTRAL'
        
        return {
            'sentiment': overall,
            'score': score,
            'avg_polarity': round(avg_polarity, 3),
            'news_count': len(news),
            'breakdown': sentiments,
            'top_news': analyzed_news[:5]
        }
    
    def get_crypto_sentiment(self, symbol='BTC'):
        """Belirli kripto için sentiment"""
        keywords = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'XRP': 'ripple',
            'DOGE': 'dogecoin',
            'ADA': 'cardano',
            'AVAX': 'avalanche',
            'DOT': 'polkadot'
        }
        
        keyword = keywords.get(symbol.upper(), symbol.lower())
        return self.get_market_sentiment(keyword)


if __name__ == '__main__':
    analyzer = NewsSentimentAnalyzer()
    
    print("📰 HABER SENTIMENT ANALİZİ\n")
    
    result = analyzer.get_market_sentiment('bitcoin')
    
    print(f"Genel Sentiment: {result['sentiment']}")
    print(f"Skor: {result['score']}/100")
    print(f"Analiz edilen haber: {result['news_count']}")
    print(f"Dağılım: {result.get('breakdown', {})}")
    
    if result.get('top_news'):
        print("\nÖne çıkan haberler:")
        for news in result['top_news'][:3]:
            print(f"  • [{news['sentiment']}] {news['title']}")
