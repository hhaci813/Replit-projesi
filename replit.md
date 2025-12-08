# Akıllı Yatırım Asistanı

## Overview
Akıllı Yatırım Asistanı (Smart Investment Assistant) is an AI-powered platform providing real-time investment analysis, forecasting, and actionable recommendations for cryptocurrencies, stocks, and global market indices. It integrates machine learning, technical analysis, and sentiment analysis to offer data-driven insights for informed investment decisions. The system operates in a "demo mode" with paper trading and aims to be a leading tool for investors seeking advanced analytical capabilities and automated market monitoring.

## User Preferences
- **Language:** Turkish
- **Data Quality:** Maximum - No garbage data
- **Trading Style:** Technical Analysis Based
- **Risk Tolerance:** Medium
- **Monitoring:** Real-time + Daily reports
- **Focus:** Actionable signals, not speculation

## System Architecture
The Akıllı Yatırım Asistanı is built on a modular and robust architecture combining various analytical engines, data sources, and user interaction layers, with all monetary values displayed in Turkish Lira (₺).

### UI/UX Decisions
- **Dashboard:** A web-based dashboard (http://localhost:5000/) offers a comprehensive overview with portfolio distribution, trend analysis, risk vs. return charts, live price updates, and investor guidelines.
  - Visualizations use colorful Plotly graphs.
  - Responsive design for mobile compatibility.
  - Automatic updates every 30 seconds.
  - Turkish interface.
- **Telegram Interface:** Provides real-time alerts, portfolio tracking, forecasts, and daily recommendations via dedicated commands.

### Technical Implementations
- **Real-Time Data & Analysis:** Integrates BTCTurk for cryptocurrencies and YFinance for stock market data.
- **ML Forecasting:** Utilizes LSTM and an ensemble of models (Random Forest, Gradient Boosting, Neural Networks) for price prediction.
- **Technical Signals:** Calculates and interprets RSI, MACD, Moving Averages, Fibonacci, Ichimoku Cloud, and Volume Profile.
- **Backtesting Engine:** Supports historical strategy analysis.
- **Pump Detection:** Identifies volume and price spikes.
- **Sentiment Analysis:** Employs TextBlob with NewsAPI for news sentiment and deep research analyzing social media (Twitter, Reddit) for market consensus and expert opinions. Includes Fear & Greed Index and Funding Rates.
- **Global Markets Analyzer:** Monitors major world indices and sectors with real-time technical analysis.
- **Recommendation Engine:** Generates investment action signals (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL) based on profit/loss potential, risk assessment, and composite scores (Technical 40% + Sentiment 30% + Momentum 30%).
- **Deep Research Analyzer:** A 5-layer system for advanced insights including news sentiment, social signals, technical confluence, whale activity, and market correlation.
- **Enhanced Auto System:** Orchestrates all automated features, managing schedules and reporting status.
- **PRO Analysis System:** Combines 8 advanced modules for a comprehensive score (0-10) considering RSI, MACD, Bollinger Bands, Volume Spike, Fear & Greed, BTC Correlation, Whale Tracking, and Social Sentiment.
- **User Management:** Includes features for portfolio tracking, watchlist management, risk profiling, and trade history.

### Feature Specifications
- **Data Sources:** Supports 169+ cryptocurrencies, 50+ stocks, 10+ global indices, and 10 market sectors.
- **Analysis:** Offers technical analysis, ML forecasting, ensemble learning, backtesting, pattern recognition, pump detection, and multi-layered sentiment analysis.
- **Recommendations:** Provides profit/loss predictions, risk assessment, composite scoring, and expert consensus.
- **Automation:** 24/7 automated analysis, including daily backtesting, hourly Discord alerts, and daily email digests.

### System Design Choices
- **Modularity:** Composed of numerous Python modules (16+ active modules) for distinct functionalities.
- **Scalability:** Designed to handle multiple data sources and analytical tasks concurrently.
- **Robustness:** Includes error handling and a data validation layer.

## External Dependencies
- **BTCTurk:** Real-time cryptocurrency data.
- **YFinance:** Real-time stock market data.
- **Telegram Bot API:** For real-time alerts, portfolio tracking, forecasts, and daily recommendations.
- **NewsAPI:** For fetching news articles for sentiment and expert opinion analysis.
- **Gmail SMTP:** For sending daily market summary email digests.
- **Discord Bot API:** For real-time alerts and notifications.
- **Plotly:** For interactive data visualization in the web dashboard.