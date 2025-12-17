"""
HİSSE HABER TOPLAYICI - BORSA İSTANBUL HABERLERİ
BigPara, BloombergHT, Mynet Finans, Dünya Gazetesi RSS
Ücretsiz haber kaynakları + Duygu Analizi
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from textblob import TextBlob
from typing import Dict, List, Optional
import time
import logging
import re

logger = logging.getLogger(__name__)

class StockNewsCollector:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 600  # 10 dakika
        
        # Türkiye finans haber kaynakları (RSS)
        self.rss_feeds = {
            'bigpara': 'https://www.bigpara.com/rss/tum-haberler.xml',
            'bloomberght': 'https://www.bloomberght.com/rss',
            'mynet_ekonomi': 'https://www.mynet.com/rss/ekonomi',
            'dunya': 'https://www.dunya.com/rss',
            'para_analiz': 'https://www.paraanaliz.com/feed/',
            'finans_gundem': 'https://www.finansgundem.com/rss/tum-haberler.xml',
        }
        
        # Hisse sembol eşleştirmeleri
        self.stock_keywords = {
            'GARAN': ['garanti', 'garan', 'garanti bankası', 'garanti bbva'],
            'THYAO': ['thy', 'türk hava yolları', 'turkish airlines', 'thyao'],
            'AKBNK': ['akbank', 'akbnk'],
            'ASELS': ['aselsan', 'asels', 'savunma'],
            'ISCTR': ['iş bankası', 'isbank', 'isctr'],
            'KCHOL': ['koç holding', 'koç', 'kchol'],
            'TUPRS': ['tüpraş', 'tupras', 'rafineri'],
            'ARCLK': ['arçelik', 'arcelik', 'beyaz eşya'],
            'SISE': ['şişecam', 'sisecam', 'cam'],
            'PETKM': ['petkim', 'petrokimya'],
            'HALKB': ['halkbank', 'halk bankası'],
            'ENKAI': ['enka', 'inşaat'],
            'VESTL': ['vestel', 'elektronik'],
            'TCELL': ['turkcell', 'gsm'],
            'BIST': ['bist', 'borsa istanbul', 'borsa', 'endeks', 'xu100', 'xu030']
        }
        
        # Türkçe duygu kelimeleri
        self.positive_words = [
            'artış', 'yükseliş', 'rekor', 'kar', 'kazanç', 'büyüme', 'pozitif',
            'olumlu', 'talep', 'güçlü', 'başarı', 'ihracat', 'yatırım', 'ivme',
            'toparlanma', 'beklentinin üzerinde', 'hedef yükseldi', 'al tavsiyesi'
        ]
        
        self.negative_words = [
            'düşüş', 'kayıp', 'zarar', 'kriz', 'risk', 'negatif', 'olumsuz',
            'daralma', 'gerileme', 'satış baskısı', 'endişe', 'belirsizlik',
            'beklentinin altında', 'hedef düşürüldü', 'sat tavsiyesi', 'iflas'
        ]
    
    def get_cached(self, key: str, fetch_func, duration: int = None):
        """Cache mekanizması"""
        duration = duration or self.cache_duration
        now = time.time()
        if key in self.cache:
            if now - self.cache[key]['time'] < duration:
                return self.cache[key]['data']
        data = fetch_func()
        self.cache[key] = {'data': data, 'time': now}
        return data
    
    def fetch_rss_news(self, feed_name: str, feed_url: str) -> List[Dict]:
        """RSS'den haber çek"""
        try:
            feed = feedparser.parse(feed_url)
            news_list = []
            
            for entry in feed.entries[:20]:
                title = entry.get('title', '') or ''
                summary = entry.get('summary', entry.get('description', '')) or ''
                link = entry.get('link', '') or ''
                published = entry.get('published', entry.get('updated', '')) or ''
                
                # Temizle
                summary = BeautifulSoup(summary, 'html.parser').get_text()[:500]
                
                news_list.append({
                    'source': feed_name,
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'published': published,
                    'timestamp': datetime.now().isoformat()
                })
            
            return news_list
        except Exception as e:
            logger.error(f"RSS çekme hatası ({feed_name}): {e}")
            return []
    
    def analyze_turkish_sentiment(self, text: str) -> Dict:
        """Türkçe duygu analizi"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        # TextBlob (İngilizce ama genel ton için)
        try:
            blob = TextBlob(text)
            textblob_score = blob.sentiment.polarity
        except:
            textblob_score = 0
        
        # Türkçe skor hesapla
        turkish_score = (positive_count - negative_count) / max(positive_count + negative_count, 1)
        
        # Kombine skor
        combined_score = (turkish_score * 0.7) + (textblob_score * 0.3)
        
        if combined_score > 0.2:
            sentiment = 'POZİTİF'
        elif combined_score < -0.2:
            sentiment = 'NEGATİF'
        else:
            sentiment = 'NÖTR'
        
        return {
            'sentiment': sentiment,
            'score': round(combined_score, 3),
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def get_stock_news(self, symbol: str) -> List[Dict]:
        """Belirli hisse için haberleri filtrele"""
        symbol = symbol.upper()
        keywords = self.stock_keywords.get(symbol, [symbol.lower()])
        
        def fetch():
            all_news = []
            
            for feed_name, feed_url in self.rss_feeds.items():
                try:
                    news = self.fetch_rss_news(feed_name, feed_url)
                    all_news.extend(news)
                except:
                    pass
            
            # Hisse ile ilgili haberleri filtrele
            relevant_news = []
            for news in all_news:
                text = (news['title'] + ' ' + news['summary']).lower()
                
                for keyword in keywords:
                    if keyword.lower() in text:
                        sentiment = self.analyze_turkish_sentiment(news['title'] + ' ' + news['summary'])
                        news['sentiment'] = sentiment
                        relevant_news.append(news)
                        break
            
            return relevant_news[:10]
        
        return self.get_cached(f'stock_news_{symbol}', fetch, 300)
    
    def get_market_news(self) -> List[Dict]:
        """Genel piyasa haberleri"""
        def fetch():
            all_news = []
            
            for feed_name, feed_url in self.rss_feeds.items():
                try:
                    news = self.fetch_rss_news(feed_name, feed_url)
                    for n in news[:5]:
                        sentiment = self.analyze_turkish_sentiment(n['title'] + ' ' + n['summary'])
                        n['sentiment'] = sentiment
                        all_news.append(n)
                except:
                    pass
            
            # Skora göre sırala
            return sorted(all_news, key=lambda x: abs(x.get('sentiment', {}).get('score', 0)), reverse=True)[:15]
        
        return self.get_cached('market_news', fetch, 300)
    
    def get_news_sentiment_summary(self, symbol: str = None) -> Dict:
        """Haber duygu özeti"""
        if symbol:
            news = self.get_stock_news(symbol)
        else:
            news = self.get_market_news()
        
        if not news:
            return {
                'overall_sentiment': 'NÖTR',
                'score': 0,
                'news_count': 0,
                'positive_count': 0,
                'negative_count': 0
            }
        
        scores = [n.get('sentiment', {}).get('score', 0) for n in news]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        positive = sum(1 for n in news if n.get('sentiment', {}).get('sentiment') == 'POZİTİF')
        negative = sum(1 for n in news if n.get('sentiment', {}).get('sentiment') == 'NEGATİF')
        
        if avg_score > 0.15:
            overall = 'POZİTİF'
        elif avg_score < -0.15:
            overall = 'NEGATİF'
        else:
            overall = 'NÖTR'
        
        return {
            'overall_sentiment': overall,
            'score': round(avg_score, 3),
            'news_count': len(news),
            'positive_count': positive,
            'negative_count': negative,
            'latest_news': news[:5]
        }
    
    def generate_news_report(self, symbol: str = None) -> str:
        """Telegram için haber raporu"""
        summary = self.get_news_sentiment_summary(symbol)
        
        if symbol:
            title = f"📰 <b>{symbol} HABER ANALİZİ</b>"
        else:
            title = "📰 <b>PİYASA HABERLERİ</b>"
        
        sentiment_emoji = "🟢" if summary['overall_sentiment'] == 'POZİTİF' else "🔴" if summary['overall_sentiment'] == 'NEGATİF' else "⚪"
        
        report = f"""{title}
━━━━━━━━━━━━━━━━━━━━━

{sentiment_emoji} <b>Genel Duygu:</b> {summary['overall_sentiment']}
📊 <b>Skor:</b> {summary['score']:+.2f}
📄 <b>Haber Sayısı:</b> {summary['news_count']}
✅ Pozitif: {summary['positive_count']} | ❌ Negatif: {summary['negative_count']}

"""
        
        if summary.get('latest_news'):
            report += "<b>Son Haberler:</b>\n\n"
            for i, news in enumerate(summary['latest_news'][:5], 1):
                s_emoji = "🟢" if news.get('sentiment', {}).get('sentiment') == 'POZİTİF' else "🔴" if news.get('sentiment', {}).get('sentiment') == 'NEGATİF' else "⚪"
                report += f"{s_emoji} {news['title'][:80]}...\n"
                report += f"   📎 {news['source']}\n\n"
        
        report += "━━━━━━━━━━━━━━━━━━━━━\n🤖 <i>Hisse Haber Analizi</i>"
        
        return report
