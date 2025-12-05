# 🌐 Deep Research Web Scraper Guide

## Sistem Yapısı

```
Input: Keyword (e.g., "bitcoin")
  ↓
Advanced Web Scraper:
  • News from RSS feeds
  • Social media signals
  • Technical indicators
  • Whale transactions
  ↓
Deep Research Analyzer:
  • Layer 1: News Sentiment
  • Layer 2: Social Signals
  • Layer 3: Technical
  • Layer 4: Whales
  • Layer 5: Correlation
  ↓
Output: 5-Layer Report + Recommendation
```

## API Usage

```python
# Deep BTC Analysis
GET http://localhost:5000/api/deep-research/BTC

# Scrape specific news
GET http://localhost:5000/api/scrape-news/bitcoin

# Whale activity
GET http://localhost:5000/api/whale-activity

# Social signals
GET http://localhost:5000/api/social-signals
```

## Example Response

```json
{
  "timestamp": "2025-12-04T...",
  "asset": "BTC",
  "layers": {
    "news": {
      "avg_sentiment": "POSITIVE",
      "polarity_score": 0.45,
      "total_articles": 20
    },
    "social": {
      "twitter_trending": ["Bitcoin pump", "BTC momentum"],
      "sentiment": "BULLISH"
    },
    "technical": {
      "confluence_score": 7,
      "insights": ["RSI Normal", "MAs aligned"]
    },
    "whales": {
      "accumulation_pattern": "Net Positive",
      "insights": ["Whales buying"]
    },
    "correlation": {
      "btc_sp500": 0.7,
      "macro_trend": "Risk-on"
    }
  },
  "verdict": {
    "recommendation": "STRONG_BUY",
    "overall_score": 7.4,
    "confidence": 0.74,
    "final_message": "BTC yükseliş sinyalleri güçlü"
  }
}
```

---

**System is now crawling the internet + generating deep insights + finding information humans can't!** 🌐🚀
