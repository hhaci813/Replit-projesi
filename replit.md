# Akıllı Yatırım Asistanı

## Overview
Akıllı Yatırım Asistanı (Smart Investment Assistant) is a comprehensive, AI-powered platform designed to provide real-time investment analysis, forecasting, and actionable recommendations for cryptocurrencies, stocks, and global market indices. The system integrates machine learning, technical analysis, and sentiment analysis from various data sources to offer a holistic view of market opportunities and risks. Its primary purpose is to empower users with data-driven insights for making informed investment decisions, operating in a "demo mode" with paper trading to mitigate real financial risk. The project aims to become a leading tool for investors seeking advanced analytical capabilities and automated market monitoring.

## User Preferences
- **Language:** Turkish
- **Data Quality:** Maximum - No garbage data
- **Trading Style:** Technical Analysis Based
- **Risk Tolerance:** Medium
- **Monitoring:** Real-time + Daily reports
- **Focus:** Actionable signals, not speculation

## System Architecture
The Akıllı Yatırım Asistanı is built upon a robust architecture that combines several analytical engines, data sources, and user interaction layers.

### UI/UX Decisions
- **Dashboard:** A web-based dashboard (accessible via `http://localhost:5000/`) provides a comprehensive overview.
  - Features include portfolio distribution graphs, 6-month trend analysis, risk vs. return charts, live price updates for top risers/fallers, and a "5 Rules Box" for new investors.
  - Visualizations leverage colorful Plotly graphs.
  - Responsive design ensures mobile compatibility.
  - Automatic updates every 30 seconds.
  - Turkish interface.

### Technical Implementations
- **Real-Time Analysis:** Integrates BTCTurk and YFinance for live cryptocurrency and stock data.
- **ML Forecasting:** Utilizes LSTM and an ensemble of models (Random Forest, Gradient Boosting, Neural Networks) for price prediction every 4 hours.
- **Technical Signals:** Calculates and interprets RSI, MACD, and Moving Averages.
- **Backtesting Engine:** Allows for historical analysis of strategies.
- **Performance Dashboard:** Tracks metrics like Sharpe ratio and ROI.
- **Pump Detection:** Identifies volume spikes (150%+) and significant price movements (2%+) every 15 minutes, calculating risk levels and trends.
- **Advanced Sentiment Analyzer:** Uses TextBlob for sentiment analysis on news articles, integrated with NewsAPI, running daily at 08:00.
- **Global Markets Analyzer:** Monitors 10+ major world indices and 10 sectors, providing real-time technical analysis and trend detection.
- **Expert Sentiment Extractor:** Extracts expert opinions and recommendations (BUY/SELL/HOLD) from news using NewsAPI and TextBlob.
- **Recommendation Engine:** Calculates profit/loss potential, risk assessment (1-10 scale), and composite scores (Technical 40% + Sentiment 30% + Momentum 30%) to generate detailed investment action signals (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL).
- **Enhanced Auto System:** Orchestrates all automated features, managing schedules and reporting status.

### Feature Specifications
- **Data Sources:** Supports 169+ cryptocurrencies, 50+ stocks, 10+ global indices, and 10 market sectors.
- **Analysis:** Offers technical analysis, ML forecasting, ensemble learning, backtesting, pattern recognition, pump detection, and sentiment analysis.
- **Recommendations:** Provides profit/loss predictions, risk assessment, composite scoring, and expert consensus.
- **Automation:** 24/7 automated analysis, including daily backtesting, hourly Discord alerts, and daily email digests.

### System Design Choices
- **Modularity:** The system is composed of numerous Python modules (35+) for different functionalities.
- **Scalability:** Designed to handle multiple data sources and analytical tasks concurrently.
- **Robustness:** Includes error handling and a data validation layer.

## External Dependencies
- **BTCTurk:** For real-time cryptocurrency data.
- **YFinance:** For real-time stock market data.
- **Telegram Bot API:** For real-time alerts, portfolio tracking, forecasts, and daily global recommendations.
- **NewsAPI:** For fetching news articles for sentiment and expert opinion analysis.
- **Gmail SMTP:** For sending daily market summary email digests (requires Gmail App Password setup).
- **Discord Bot API:** For real-time alerts and notifications (requires Discord bot token).
- **Plotly:** For interactive data visualization in the web dashboard.
---

## 🌐 DEEP RESEARCH WEB SCRAPER (04.12.2025 - Final)

### ✅ YENİ ÖZELLIK: Internet Tarayıcısı + Derinlemesine Analiz

#### 1. **Advanced Web Scraper** - `advanced_web_scraper.py`
- **News Scraping:** BTCTurk'le ilgili haberleri RSS/Web'den otomatik topla
- **Social Media Tracking:** Twitter trending, Reddit discussions
- **Technical Data:** RSI, MACD, Volume, Whale transactions
- **Multi-Source:** Coindesk, Bloomberg, Cryptonews, vb.

```python
scraper = AdvancedWebScraper()
news = scraper.scrape_crypto_news("bitcoin", limit=20)
whales = scraper.scrape_technical_data("BTC")
```

#### 2. **Deep Research Analyzer** - `deep_research_analyzer.py`
5-Layer İnsan Bulamadığı Bilgi Sistemi:

| Layer | İçerik | Açıklama |
|-------|--------|----------|
| **1. News Sentiment** | 20+ makale | Haberlerden sentiment analiz |
| **2. Social Signals** | Twitter + Reddit | Sosyal medya consensus |
| **3. Technical Confluence** | RSI, MACD, MA | 7/10 confluence score |
| **4. Whale Activity** | Blockchain | Büyük oyuncu hareketleri |
| **5. Market Correlation** | S&P 500, Yields | Makro ekonomi etkileri |

```python
analyzer = DeepResearchAnalyzer()
research = analyzer.analyze_btc_deep()
# Returns: 5 layers + final verdict + confidence
```

#### 3. **Integrated API Endpoints**

```
GET /api/deep-research/BTC              → 5-layer complete analysis
GET /api/scrape-news/<keyword>          → News scraping + sentiment
GET /api/whale-activity                 → Blockchain tracking
GET /api/social-signals                 → Twitter + Reddit consensus
```

### 📊 Örnek Output:

```
🔬 DEEP BTC RESEARCH REPORT

📰 News Sentiment: POSITIVE (+0.45 polarity)
   • 20 makale analiz edildi
   • Bullish haberler başında
   
💬 Social Signals: BULLISH
   • Twitter: Bitcoin momentum trending
   • Reddit: Bulls r fuk memes 🚀
   
📊 Technical: 7/10 Confluence
   • RSI Normal (not overbought)
   • MAs perfectly aligned
   • Volume confirmed
   
🐋 Whales: NET BULLISH
   • 5 büyük transfer (accumulation)
   • Long-term holders buying
   
🔗 Market Correlation: POSITIVE
   • S&P 500 ↑ BTC ↑ (0.7 corr)
   • Treasury yields ↓ → BTC favorable
   • Risk appetite: ↑

🎯 FINAL VERDICT: STRONG_BUY
   Score: 7.4/10
   Confidence: 74%
   Message: "BTC yükseliş sinyalleri güçlü"
```

### 🚀 CAPABILITIES:

- ✅ Internet tarama (otomatik haber toplama)
- ✅ Sosyal medya sentiment (Twitter, Reddit)
- ✅ Whale tracking (blockchain analizi)
- ✅ Technical confluence (5 indicator combo)
- ✅ Market correlation (makro etki)
- ✅ Automated insights generation
- ✅ Integrated with recommendation engine

### 📱 KULLANIM:

1. **Telegram:** Deep report günlük otomatik
2. **Dashboard:** `/api/deep-research/BTC` endpoint
3. **News:** Keyword'e göre otomatik scrape
4. **Whale:** Blockchain hareketlerini takip et

### 🎊 SONUÇ:

Sistem artık **interneti taratıyor** + **derinlemesine analiz yapıyor** + **insan bulamadığı bilgileri buluyor** = **Sağlam investment recommendations**

