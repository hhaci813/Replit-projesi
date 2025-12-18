# Akıllı Yatırım Asistanı

## Overview
Akıllı Yatırım Asistanı (Smart Investment Assistant) is an AI-powered platform providing real-time investment analysis, forecasting, and actionable recommendations for cryptocurrencies, stocks, and global market indices. It integrates machine learning, technical analysis, and sentiment analysis to offer data-driven insights for informed investment decisions. The system operates in a "demo mode" with paper trading and aims to be a leading tool for investors seeking advanced analytical capabilities and automated market monitoring.

## User Preferences
- **Language:** Turkish
- **Data Quality:** Maximum - No garbage data
- **Trading Style:** Technical Analysis Based
- **Risk Tolerance:** Medium
- **Monitoring:** Real-time + Daily reports + Chart Analysis
- **Focus:** Actionable signals, not speculation

## System Architecture
The Akıllı Yatırım Asistanı is built on a modular and robust architecture combining various analytical engines, data sources, and user interaction layers, with all monetary values displayed in Turkish Lira (₺).

### UI/UX Decisions
- **Dashboard:** A web-based dashboard (http://localhost:5000/) offers a comprehensive overview with portfolio distribution, trend analysis, risk vs. return charts, live price updates, and investor guidelines.
  - Visualizations use colorful Plotly graphs.
  - Responsive design for mobile compatibility.
  - Automatic updates every 30 seconds.
  - Turkish interface.
- **Telegram Interface:** Provides real-time alerts, portfolio tracking, forecasts, chart analysis, and daily recommendations via dedicated commands and photo uploads.

### Technical Implementations
- **Real-Time Data & Analysis:** Integrates BTCTurk for cryptocurrencies and YFinance for stock market data.
- **ML Forecasting:** Utilizes LSTM and an ensemble of models (Random Forest, Gradient Boosting, Neural Networks) for price prediction.
- **Technical Signals:** Calculates and interprets RSI, MACD, Moving Averages, Fibonacci, Ichimoku Cloud, and Volume Profile.
- **Backtesting Engine:** Supports historical strategy analysis with RSI, MA Crossover, and Bollinger strategies.
- **Pump Detection:** Identifies volume and price spikes.
- **Sentiment Analysis:** Employs TextBlob with NewsAPI for news sentiment and deep research analyzing social media (Twitter, Reddit) for market consensus and expert opinions. Includes Fear & Greed Index and Funding Rates.
- **Global Markets Analyzer:** Monitors major world indices and sectors with real-time technical analysis.
- **Recommendation Engine:** Generates investment action signals (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL) based on profit/loss potential, risk assessment, and composite scores (Technical 40% + Sentiment 30% + Momentum 30%).
- **Deep Research Analyzer:** A 5-layer system for advanced insights including news sentiment, social signals, technical confluence, whale activity, and market correlation.
- **Enhanced Auto System:** Orchestrates all automated features, managing schedules and reporting status.
- **PRO Analysis System:** Combines 8 advanced modules for a comprehensive score (0-10) considering RSI, MACD, Bollinger Bands, Volume Spike, Fear & Greed, BTC Correlation, Whale Tracking, and Social Sentiment.
- **User Management:** Includes features for portfolio tracking, watchlist management, risk profiling, and trade history.
- **Chart Analysis System (NEW):** Automated analysis of price chart images via Telegram. Detects trends, support/resistance levels, volume signals, and momentum from uploaded images.

### Stock Market Modules (New - December 2024)
- **Stock News Collector (stock_news_collector.py):** RSS-based news collection from BigPara, BloombergHT, Mynet Finans, Dünya Gazetesi with Turkish sentiment analysis.
- **Macro Economic Data (stock_macro_data.py):** USD/TRY, EUR/TRY, GBP/TRY exchange rates, gold prices (ons/gram), BIST indices (XU100, XU030, XBANK, XUSIN), TCMB policy rates.
- **Stock Portfolio Simulator (stock_portfolio.py):** Virtual trading with 100,000 TL starting capital, buy/sell stocks, stop-loss/take-profit, trade history, P&L tracking.
- **Stock Backtesting Engine (stock_backtest.py):** Historical strategy testing with RSI, MA Crossover, Bollinger Bands strategies. Calculates win rate, Sharpe ratio, max drawdown, profit factor.
- **Turkish Currency Parser:** Robust parsing for Turkish number formats (5.000 = 5000, 5,50 = 5.5, 10.000,50 = 10000.5).
- **Chart Analyzer (chart_analyzer.py):** Computer vision-based analysis of price charts detecting:
  - Trend direction (📈 Yükseliş / 📉 Düşüş / ➡️ Yatay)
  - Support and resistance levels
  - Volume trends and momentum strength
  - Generate buy/sell signals based on visual patterns

### Multi-Interval Automated Analysis (NEW - December 2024)
- **5-Minute Quick Check:** Monitors BTC, ETH, XRP, SOL, AVAX for >3% movements
- **15-Minute Analysis:** Generates buy/sell signals for 7 major cryptocurrencies
- **30-Minute Detailed Report:** Top 5 coins with scores, RSI levels, and 24h trends
- **10-Minute Pump Alerts:** Volume and price spike detection
- **2-Hour Crypto Analysis:** Full technical and ML analysis
- **3-Hour Stock Analysis:** Comprehensive stock market updates

### Feature Specifications
- **Data Sources:** Supports 169+ cryptocurrencies, 50+ stocks, 10+ global indices, and 10 market sectors.
- **Analysis:** Offers technical analysis, ML forecasting, ensemble learning, backtesting, pattern recognition, pump detection, multi-layered sentiment analysis, and chart image analysis.
- **Recommendations:** Provides profit/loss predictions, risk assessment, composite scoring, expert consensus, and visual pattern-based signals.
- **Automation:** 24/7 automated analysis with 7 concurrent schedulers for different intervals, hourly Telegram alerts, and daily email digests.

### System Design Choices
- **Modularity:** Composed of numerous Python modules (18+ active modules) for distinct functionalities.
- **Scalability:** Designed to handle multiple data sources and analytical tasks concurrently with 7 parallel schedulers.
- **Robustness:** Includes error handling, data validation layer, and fallback systems.

### Stock Market Telegram Commands
- `/ultimate-hisse [SYMBOL]` - Full technical analysis for a stock
- `/tarama-hisse` - Scan top 15 BIST stocks
- `/hisse-haber [SYMBOL]` - News sentiment analysis for stock/market
- `/makro` - Macro economic data (FX, gold, BIST indices, rates)
- `/hisse-portfoy` - Virtual portfolio status
- `/hisse-al [SYMBOL] [TL]` - Buy stock (virtual) - supports Turkish formats
- `/hisse-sat [SYMBOL] [%]` - Sell stock (virtual)
- `/hisse-backtest [SYMBOL]` - Run backtesting strategies
- `/hisse-sifirla` - Reset virtual portfolio

### Telegram Automation Features
- **Photo Upload Analysis:** Send a price chart image and bot will analyze trend, support/resistance, momentum, and provide buy/sell signals
- **5/15/30 Minute Auto Reports:** Automatic Telegram messages with market analysis at different intervals
- **Real-Time Alerts:** 5-minute alert checks and pump detection notifications
- **Custom Commands:** `/btc`, `/analiz [SEMBOL]`, `/tahmin [SEMBOL]`, `/piyasa` and more

## External Dependencies
- **BTCTurk:** Real-time cryptocurrency data.
- **YFinance:** Real-time stock market data and BIST stocks.
- **Telegram Bot API:** For real-time alerts, portfolio tracking, forecasts, chart analysis, and daily recommendations.
- **NewsAPI:** For fetching news articles for sentiment and expert opinion analysis.
- **RSS Feeds:** BigPara, BloombergHT, Mynet Finans, Dünya Gazetesi for stock news.
- **Gmail SMTP:** For sending daily market summary email digests.
- **Discord Bot API:** For real-time alerts and notifications.
- **Plotly:** For interactive data visualization in the web dashboard.
- **OpenCV & PIL:** For chart image analysis and pattern detection.

## Recent Changes (December 2024)
- Added automated 5/15/30 minute cryptocurrency analysis with Telegram notifications
- Implemented chart_analyzer.py for visual price chart analysis via computer vision
- Enhanced telegram_bot.py with photo upload capability for automatic chart analysis
- Integrated multi-interval scheduler system (7 concurrent jobs)
- Added trend detection, support/resistance level finding, volume analysis, and momentum detection from images
- System now provides visual signals: 🟢 GÜÇLÜ AL, 🟢 AL, ⚪ TUT, 🔴 SAT, 🔴 GÜÇLÜ SAT based on image analysis
