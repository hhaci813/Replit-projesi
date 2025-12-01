# 🌍 GLOBAL MARKETS + EXPERT ANALYSIS + RECOMMENDATIONS

**Tarih:** 01 Aralık 2025

---

## ✅ YENİ ÖZELLİKLER

### 1️⃣ **Global Markets Analyzer** - `global_markets_analyzer.py`
- **10+ Global Indices:** S&P 500, NASDAQ, DAX, CAC 40, FTSE 100, NIKKEI, Hang Seng, Shanghai, STOXX 600
- **Real-time Data:** yfinance'dan canlı veriler
- **Technical Analysis:** RSI, Moving Averages (MA5, MA20)
- **Trend Detection:** STRONG_UP, UP, DOWN, STRONG_DOWN, SIDEWAYS
- **Sector Analysis:** 10 sektor (Technology, Healthcare, Finance, Energy, vb)
- **Performance Tracking:** 1-year vs monthly changes

**Kullanım:**
```python
from global_markets_analyzer import GlobalMarketsAnalyzer
analyzer = GlobalMarketsAnalyzer()
summary = analyzer.get_market_summary()
# Returns: overall trend, rising/falling count, detailed indices
```

### 2️⃣ **Expert Sentiment Extractor** - `expert_sentiment_extractor.py`
- **Expert Opinions:** Haberlerden yorumcuların analizleri
- **NewsAPI Integration:** Latest financial news
- **Sentiment Analysis:** TextBlob + polarity scoring
- **Recommendation Extraction:** BUY/SELL/HOLD otomatik çıkart
- **Consensus Calculation:** STRONG_BUY → STRONG_SELL
- **Source Tracking:** Author ve news source

**Kullanım:**
```python
from expert_sentiment_extractor import ExpertSentimentExtractor
extractor = ExpertSentimentExtractor()
result = extractor.extract_expert_opinions("Apple", days=7)
# Returns: 15 latest expert opinions with sentiment & recommendations
```

### 3️⃣ **Recommendation Engine** - `recommendation_engine.py`
- **Kar/Zarar Tahmini:** 
  - STRONG_BUY → +10% to +60% profit potential
  - BUY → +5% to +40% profit potential
  - SELL → -5% to -40% loss risk
  - STRONG_SELL → -10% to -60% loss risk

- **Risk Assessment:** 1-10 risk scale
- **Confidence Scoring:** 0-1 (how sure is the signal)
- **Composite Scoring:** Technical (40%) + Sentiment (30%) + Momentum (30%)
- **Detailed Reasoning:** "Why" behind each recommendation

**Kullanım:**
```python
from recommendation_engine import RecommendationEngine
engine = RecommendationEngine()
rec = engine.generate_recommendation('BTC', 0.6, 0.4, 0.7)
# Returns: action, confidence, profit_potential, risk, reasoning
```

---

## 📊 WEB API ENDPOINTS

### Global Markets
```
GET /api/global-markets
→ Returns: overall trend, indices data, rising/falling count
Example: http://localhost:5000/api/global-markets
```

### Sectors
```
GET /api/sectors
→ Returns: sector performance, ratings, 1-year changes
Example: http://localhost:5000/api/sectors
```

### Expert Opinions
```
GET /api/expert-opinions/<query>
→ Returns: expert opinions, sentiment, recommendations, consensus
Example: http://localhost:5000/api/expert-opinions/Apple
```

### Recommendations
```
GET /api/recommendation/<asset>/<technical>/<sentiment>/<momentum>
→ Returns: BUY/SELL/HOLD with reasoning and profit/loss potential
Example: http://localhost:5000/api/recommendation/BTC/0.6/0.4/0.7
```

---

## 🎯 RECOMMENDATION FORMAT

```json
{
  "asset": "BTC",
  "action": "STRONG_BUY",
  "confidence": 0.75,
  "profit_potential": 25.5,
  "risk_potential": 5.2,
  "reasoning": "📈 Strong uptrend momentum • 🟢 Positive expert sentiment • 💪 Technical indicators bullish",
  "emoji": "🟢🟢🚀"
}
```

---

## 💰 PROFIT/LOSS SIGNALS

| Signal | Action | Potential Profit | Risk Level | When |
|--------|--------|-----------------|------------|------|
| 🟢🟢🚀 STRONG_BUY | BUY NOW | +10% to +60% | 2-4/10 | All signals aligned positive |
| 🟢📈 BUY | BUY | +5% to +40% | 4-5/10 | 2 of 3 signals positive |
| 🟡⏸️ HOLD | WAIT | -2% to +3% | 3-4/10 | Mixed signals |
| 🔴📉 SELL | SELL | -5% to -40% | 5-7/10 | 2 of 3 signals negative |
| 🔴🔴🌪️ STRONG_SELL | SELL NOW | -10% to -60% | 7-9/10 | All signals aligned negative |

---

## 📱 TELEGRAM INTEGRATION

**Daily Global Recommendations:**
- Saat: Günlük 08:00
- İçerik:
  - Global Market Status
  - Major Indices
  - Sector Performance
  - Expert Consensus
  - Investment Recommendations
  - Risk Management Tips
  - Profit/Loss Potential

---

## 🔧 SETUP

### Gereken API Keys
1. **NewsAPI** (Expert opinions için)
   - https://newsapi.org/
   - ENV: `NEWSAPI_KEY`

### Otomatik Schedule
- Email Digest: Günlük 09:00
- Pump Detection: Her 15 dakika
- Sentiment Analysis: Günlük 08:00
- **Global Recommendations: Günlük 08:00** ← YENİ

---

## 📊 DURUM

- ✅ 10+ global indices
- ✅ 10 sektor analizi
- ✅ Expert sentiment extraction
- ✅ Kar/Zarar tahmini
- ✅ Telegram integration
- ✅ Web API endpoints
- ✅ Production ready

---

## 🚀 NEXTSteps

1. Telegram'da daily recommendations al
2. Web dashboard'da global markets gör
3. Expert opinions okuyarak consensus takip et
4. Recommendation engine'den kar/zarar tahminlerini al
5. Risk management kurallarına uy

**Artık sadece kripto değil, global markets + expert analysis + kar/zarar tahmini alıyorsun!** 🌍💰
