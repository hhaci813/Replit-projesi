"""
SOSYAL MEDYA SENTIMENT ANALİZİ
Twitter, Reddit, Crypto News Sentiment
"""

import requests
import feedparser
from datetime import datetime, timedelta
from textblob import TextBlob
from typing import Dict, List, Optional
import re

class SocialSentiment:
    def __init__(self):
        self.rss_feeds = {
            'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'cointelegraph': 'https://cointelegraph.com/rss',
            'bitcoinist': 'https://bitcoinist.com/feed/',
        }
        self.keywords = {
            'bullish': ['bull', 'bullish', 'moon', 'pump', 'buy', 'long', 'breakout', 'rally', 'surge', 'soar'],
            'bearish': ['bear', 'bearish', 'dump', 'crash', 'sell', 'short', 'breakdown', 'plunge', 'drop', 'fall']
        }
        
    def analyze_text_sentiment(self, text: str) -> Dict:
        """Metin sentiment analizi"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            text_lower = text.lower()
            bullish_count = sum(1 for word in self.keywords['bullish'] if word in text_lower)
            bearish_count = sum(1 for word in self.keywords['bearish'] if word in text_lower)
            
            keyword_score = (bullish_count - bearish_count) / max(bullish_count + bearish_count, 1)
            combined_score = (polarity * 0.6) + (keyword_score * 0.4)
            
            if combined_score > 0.2:
                sentiment = 'BULLISH'
            elif combined_score < -0.2:
                sentiment = 'BEARISH'
            else:
                sentiment = 'NEUTRAL'
            
            return {
                'polarity': round(polarity, 3),
                'combined_score': round(combined_score, 3),
                'sentiment': sentiment
            }
        except:
            return {'sentiment': 'NEUTRAL', 'combined_score': 0}
    
    def get_crypto_news_sentiment(self, keyword: str = 'bitcoin') -> Dict:
        """Kripto haber sentiment analizi"""
        try:
            articles = []
            sentiments = []
            
            for source, url in self.rss_feeds.items():
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:10]:
                        title = entry.get('title', '')
                        summary = entry.get('summary', '')[:300]
                        
                        if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                            text = f"{title} {summary}"
                            sentiment = self.analyze_text_sentiment(text)
                            
                            articles.append({
                                'source': source,
                                'title': title[:80],
                                'sentiment': sentiment['sentiment'],
                                'score': sentiment['combined_score']
                            })
                            sentiments.append(sentiment['combined_score'])
                except:
                    continue
            
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                bullish_count = sum(1 for s in sentiments if s > 0.1)
                bearish_count = sum(1 for s in sentiments if s < -0.1)
                
                if avg_sentiment > 0.15:
                    overall, signal = 'BULLISH', 'BUY'
                elif avg_sentiment < -0.15:
                    overall, signal = 'BEARISH', 'SELL'
                else:
                    overall, signal = 'NEUTRAL', 'HOLD'
            else:
                avg_sentiment = 0
                bullish_count = bearish_count = 0
                overall, signal = 'NEUTRAL', 'HOLD'
            
            return {
                'keyword': keyword,
                'total_articles': len(articles),
                'average_sentiment': round(avg_sentiment, 3),
                'overall': overall,
                'signal': signal,
                'bullish_articles': bullish_count,
                'bearish_articles': bearish_count,
                'top_articles': articles[:5],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'keyword': keyword, 'overall': 'NEUTRAL', 'signal': 'HOLD'}
    
    def get_reddit_sentiment(self, subreddit: str = 'cryptocurrency') -> Dict:
        """Reddit sentiment analizi"""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=20"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                posts = data.get('data', {}).get('children', [])
                
                sentiments = []
                hot_topics = []
                
                for post in posts:
                    post_data = post.get('data', {})
                    title = post_data.get('title', '')
                    score = post_data.get('score', 0)
                    
                    sentiment = self.analyze_text_sentiment(title)
                    sentiments.append(sentiment['combined_score'])
                    
                    if score > 50:
                        hot_topics.append({
                            'title': title[:60],
                            'score': score,
                            'sentiment': sentiment['sentiment']
                        })
                
                avg = sum(sentiments) / len(sentiments) if sentiments else 0
                overall = 'BULLISH' if avg > 0.1 else ('BEARISH' if avg < -0.1 else 'NEUTRAL')
                
                return {
                    'subreddit': subreddit,
                    'posts_analyzed': len(posts),
                    'average_sentiment': round(avg, 3),
                    'overall': overall,
                    'hot_topics': hot_topics[:5]
                }
        except:
            pass
        
        return {'subreddit': subreddit, 'overall': 'NEUTRAL'}
    
    def generate_report(self) -> str:
        """Telegram için rapor"""
        news = self.get_crypto_news_sentiment('bitcoin')
        reddit = self.get_reddit_sentiment('cryptocurrency')
        
        msg = "📱 <b>SOSYAL MEDYA SENTIMENT</b>\n\n"
        
        emoji = '📈' if news['overall'] == 'BULLISH' else ('📉' if news['overall'] == 'BEARISH' else '➡️')
        msg += f"""📰 <b>KRİPTO HABERLER</b>
{emoji} Genel: {news['overall']}
📊 Skor: {news.get('average_sentiment', 0)}
📝 Makale: {news.get('total_articles', 0)}
🔮 Sinyal: {news.get('signal', 'HOLD')}

"""
        
        if news.get('top_articles'):
            msg += "<b>Haberler:</b>\n"
            for a in news['top_articles'][:3]:
                e = '🟢' if a['sentiment'] == 'BULLISH' else ('🔴' if a['sentiment'] == 'BEARISH' else '⚪')
                msg += f"{e} {a['title'][:45]}...\n"
            msg += "\n"
        
        emoji = '📈' if reddit['overall'] == 'BULLISH' else ('📉' if reddit['overall'] == 'BEARISH' else '➡️')
        msg += f"""🔴 <b>REDDIT</b>
{emoji} Genel: {reddit['overall']}
"""
        
        if reddit.get('hot_topics'):
            msg += "\n<b>Trend:</b>\n"
            for t in reddit['hot_topics'][:3]:
                e = '🟢' if t['sentiment'] == 'BULLISH' else ('🔴' if t['sentiment'] == 'BEARISH' else '⚪')
                msg += f"{e} {t['title'][:35]}...\n"
        
        return msg
