"""
AI HABERCİ - Kripto Haberlerini Otomatik Tarama ve Analiz
Haber kaynaklarından otomatik veri toplama, sentiment analizi, fiyat etkisi tahmini
"""

import os
import re
import requests
import feedparser
from datetime import datetime, timedelta
from textblob import TextBlob
from typing import Dict, List

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "8268294938:AAFIdr7FfJdtq__FueMOdsvym19H8IBWdNs"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "8391537149"

class AINewsAnalyzer:
    def __init__(self):
        self.rss_feeds = [
            "https://cointelegraph.com/rss",
            "https://coindesk.com/arc/outboundfeeds/rss/",
            "https://cryptonews.com/news/feed/",
            "https://bitcoinmagazine.com/feed",
            "https://decrypt.co/feed",
        ]
        self.keywords = {
            "bullish": ["bull", "surge", "soar", "rally", "breakout", "moon", "pump", "gain", 
                       "rise", "growth", "adoption", "partnership", "institutional", "etf approved"],
            "bearish": ["bear", "crash", "dump", "fall", "drop", "plunge", "decline", "sell-off",
                       "regulation", "ban", "hack", "scam", "lawsuit", "sec", "fraud"],
            "neutral": ["update", "announce", "launch", "release", "introduce", "develop"]
        }
        self.crypto_mentions = {
            "BTC": ["bitcoin", "btc", "₿"],
            "ETH": ["ethereum", "eth", "ether"],
            "SOL": ["solana", "sol"],
            "XRP": ["ripple", "xrp"],
            "DOGE": ["dogecoin", "doge", "shib"],
            "ADA": ["cardano", "ada"],
            "AVAX": ["avalanche", "avax"],
            "DOT": ["polkadot", "dot"],
            "LINK": ["chainlink", "link"],
            "MATIC": ["polygon", "matic"]
        }
        self.important_people = {
            "elon musk": {"influence": "HIGH", "coins": ["DOGE", "BTC"]},
            "vitalik": {"influence": "HIGH", "coins": ["ETH"]},
            "michael saylor": {"influence": "MEDIUM", "coins": ["BTC"]},
            "cz": {"influence": "MEDIUM", "coins": ["BNB"]},
            "gary gensler": {"influence": "HIGH", "coins": ["XRP", "ETH"]},
            "trump": {"influence": "MEDIUM", "coins": ["BTC", "CRYPTO"]},
        }
    
    def fetch_news(self, limit: int = 50) -> list:
        """Haber kaynaklarından veri topla"""
        all_news = []
        
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:limit // len(self.rss_feeds)]:
                    news_item = {
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", "")[:500],
                        "link": entry.get("link", ""),
                        "published": entry.get("published", datetime.now().isoformat()),
                        "source": feed.feed.get("title", "Unknown")
                    }
                    all_news.append(news_item)
            except Exception as e:
                continue
        
        return all_news
    
    def analyze_sentiment(self, text: str) -> dict:
        """Sentiment analizi yap"""
        blob = TextBlob(text.lower())
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Keyword bazlı analiz
        bullish_count = sum(1 for word in self.keywords["bullish"] if word in text.lower())
        bearish_count = sum(1 for word in self.keywords["bearish"] if word in text.lower())
        
        # Combine scores
        keyword_score = (bullish_count - bearish_count) * 0.1
        final_score = (polarity + keyword_score) / 2
        
        if final_score > 0.15:
            sentiment = "BULLISH"
            emoji = "🟢"
        elif final_score < -0.15:
            sentiment = "BEARISH"
            emoji = "🔴"
        else:
            sentiment = "NEUTRAL"
            emoji = "⚪"
        
        return {
            "sentiment": sentiment,
            "score": final_score,
            "emoji": emoji,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "bullish_keywords": bullish_count,
            "bearish_keywords": bearish_count
        }
    
    def detect_crypto_mentions(self, text: str) -> list:
        """Hangi kriptoların bahsedildiğini bul"""
        mentioned = []
        text_lower = text.lower()
        
        for symbol, keywords in self.crypto_mentions.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if symbol not in mentioned:
                        mentioned.append(symbol)
                    break
        
        return mentioned
    
    def detect_important_mentions(self, text: str) -> list:
        """Önemli kişilerin bahsedilmesini tespit et"""
        mentions = []
        text_lower = text.lower()
        
        for person, data in self.important_people.items():
            if person in text_lower:
                mentions.append({
                    "person": person.title(),
                    "influence": data["influence"],
                    "related_coins": data["coins"]
                })
        
        return mentions
    
    def estimate_price_impact(self, sentiment: dict, mentions: list, people: list) -> dict:
        """Fiyat etkisi tahmini"""
        base_impact = sentiment["score"] * 5  # -5 to +5 range
        
        # Önemli kişi etkisi
        for person in people:
            if person["influence"] == "HIGH":
                base_impact *= 1.5
            elif person["influence"] == "MEDIUM":
                base_impact *= 1.2
        
        # Etkilenecek coinler
        affected_coins = set(mentions)
        for person in people:
            affected_coins.update(person["related_coins"])
        
        if base_impact > 3:
            impact_level = "YÜKSEK POZİTİF"
            recommendation = "BUY sinyali güçleniyor"
        elif base_impact > 1:
            impact_level = "ORTA POZİTİF"
            recommendation = "İzlemeye al"
        elif base_impact < -3:
            impact_level = "YÜKSEK NEGATİF"
            recommendation = "Dikkatli ol / SELL düşün"
        elif base_impact < -1:
            impact_level = "ORTA NEGATİF"
            recommendation = "Risk artıyor"
        else:
            impact_level = "NÖTR"
            recommendation = "Bekle"
        
        return {
            "impact_score": base_impact,
            "impact_level": impact_level,
            "recommendation": recommendation,
            "affected_coins": list(affected_coins)
        }
    
    def analyze_all_news(self) -> dict:
        """Tüm haberleri analiz et"""
        news = self.fetch_news(50)
        
        analyzed = []
        coin_sentiment = {}
        important_news = []
        
        for item in news:
            text = f"{item['title']} {item['summary']}"
            
            sentiment = self.analyze_sentiment(text)
            cryptos = self.detect_crypto_mentions(text)
            people = self.detect_important_mentions(text)
            impact = self.estimate_price_impact(sentiment, cryptos, people)
            
            analysis = {
                **item,
                "sentiment": sentiment,
                "cryptos_mentioned": cryptos,
                "important_people": people,
                "price_impact": impact
            }
            analyzed.append(analysis)
            
            # Coin bazlı sentiment topla
            for coin in cryptos:
                if coin not in coin_sentiment:
                    coin_sentiment[coin] = {"scores": [], "count": 0}
                coin_sentiment[coin]["scores"].append(sentiment["score"])
                coin_sentiment[coin]["count"] += 1
            
            # Önemli haberleri ayır
            if abs(impact["impact_score"]) > 2 or people:
                important_news.append(analysis)
        
        # Coin sentiment ortalamaları
        for coin, data in coin_sentiment.items():
            data["avg_sentiment"] = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            if data["avg_sentiment"] > 0.1:
                data["outlook"] = "BULLISH"
            elif data["avg_sentiment"] < -0.1:
                data["outlook"] = "BEARISH"
            else:
                data["outlook"] = "NEUTRAL"
        
        return {
            "total_news": len(news),
            "analyzed": analyzed,
            "coin_sentiment": coin_sentiment,
            "important_news": important_news[:10],
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_report(self) -> str:
        """Haber analiz raporu"""
        analysis = self.analyze_all_news()
        
        report = f"""
📰 <b>AI HABERCİ RAPORU</b>
━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>HABER ÖZETİ</b>
• Taranan Haber: {analysis['total_news']}
• Önemli Haber: {len(analysis['important_news'])}

"""
        # Coin sentiment
        if analysis["coin_sentiment"]:
            report += "🪙 <b>KRİPTO SENTIMENT</b>\n"
            for coin, data in sorted(analysis["coin_sentiment"].items(), 
                                    key=lambda x: x[1]["count"], reverse=True)[:8]:
                if data["outlook"] == "BULLISH":
                    emoji = "🟢"
                elif data["outlook"] == "BEARISH":
                    emoji = "🔴"
                else:
                    emoji = "⚪"
                report += f"{emoji} {coin}: {data['outlook']} ({data['count']} haber)\n"
        
        # Önemli haberler
        if analysis["important_news"]:
            report += "\n🔥 <b>ÖNEMLİ HABERLER</b>\n"
            for news in analysis["important_news"][:5]:
                sentiment_emoji = news["sentiment"]["emoji"]
                title = news["title"][:60] + "..." if len(news["title"]) > 60 else news["title"]
                
                report += f"\n{sentiment_emoji} <b>{title}</b>\n"
                
                if news["cryptos_mentioned"]:
                    report += f"   🪙 {', '.join(news['cryptos_mentioned'])}\n"
                
                if news["important_people"]:
                    people = [p["person"] for p in news["important_people"]]
                    report += f"   👤 {', '.join(people)}\n"
                
                impact = news["price_impact"]
                report += f"   📈 {impact['impact_level']}: {impact['recommendation']}\n"
        
        report += """
━━━━━━━━━━━━━━━━━━━━━━━
🤖 <i>AI Haberci - Akıllı Yatırım Asistanı</i>
"""
        return report
    
    def send_telegram_report(self):
        """Raporu Telegram'a gönder"""
        report = self.generate_report()
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': report,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            return True
        except:
            return False
    
    def check_breaking_news(self) -> list:
        """Son dakika haberleri kontrol et"""
        analysis = self.analyze_all_news()
        breaking = []
        
        for news in analysis["important_news"]:
            impact = news["price_impact"]
            if abs(impact["impact_score"]) > 3:
                breaking.append({
                    "title": news["title"],
                    "sentiment": news["sentiment"]["sentiment"],
                    "impact": impact["impact_level"],
                    "coins": impact["affected_coins"],
                    "recommendation": impact["recommendation"]
                })
        
        return breaking


if __name__ == "__main__":
    analyzer = AINewsAnalyzer()
    print(analyzer.generate_report())
