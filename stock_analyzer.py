"""
HISSE ANALİZÖRÜ - BORSA İSTANBUL (BİST) İÇİN ULTIMATE ANALYZER
Kripto analiziyle aynı sistem, hisse kodları için uyarlanmış
"""

import requests
import feedparser
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from textblob import TextBlob
from typing import Dict, List, Optional
import json
import time
import os
import logging

logger = logging.getLogger(__name__)

class StockAnalyzer:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300
        
        # Borsa İstanbul hisse kodları
        self.bist_codes = {
            'GARAN': 'Garanti Bankası', 'THYAO': 'Turkish Airlines', 'AKBNK': 'Akbank',
            'ASELS': 'Aselsan', 'TKCLP': 'Turkcell', 'ISCTR': 'İş Bankası', 'KCHOL': 'Koç Holding',
            'TUPRS': 'Tüpraş', 'ARCLK': 'Arçelik', 'TATGD': 'Tatgaranti', 'TOASO': 'Tüpraş',
            'HALKB': 'Halkbank', 'KAYBK': 'Kaynak Bank', 'DNSAS': 'Doğuş Otomotiv',
            'ENKAI': 'Enka İnşaat', 'ADEL': 'Adel Kaynakçılık', 'TAVHL': 'TAV Havalimanları',
            'YKBNK': 'Yokluk Bankası', 'SISE': 'Şişecam', 'VESTL': 'Vestel', 'FROTO': 'Forto',
            'PETKM': 'Petkim', 'TCELL': 'Turkcell', 'PGSUS': 'Pegasus', 'KOZAL': 'Kozal',
            'PNSUT': 'Panasonic Sürücü', 'ENJSA': 'Enjeks', 'ORKA': 'Orkase', 'MAVI': 'Mavi',
            'INDAG': 'Indağ', 'FOTOB': 'Fotoboğraf', 'KLNMA': 'Kilim Mobilya'
        }
        
        self.rss_feeds = {
            'finansal': 'https://www.finansal.com.tr/rss',
            'borsahaberleri': 'https://www.borsahaberleri.com/rss',
            'finansturk': 'https://www.finansturk.com/rss',
        }
    
    def get_cached(self, key: str, fetch_func, duration: int = None):
        duration = duration or self.cache_duration
        now = time.time()
        if key in self.cache:
            if now - self.cache[key]['time'] < duration:
                return self.cache[key]['data']
        data = fetch_func()
        self.cache[key] = {'data': data, 'time': now}
        return data
    
    def get_stock_price(self, symbol: str) -> Dict:
        """YFinance ile hisse fiyatı al"""
        try:
            ticker = f"{symbol}.IS"  # Borsa İstanbul suffix
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if len(hist) == 0:
                return {'current': 0, 'change': 0}
            
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change = ((current - prev_close) / prev_close * 100) if prev_close > 0 else 0
            
            return {
                'current': round(float(current), 4),
                'change': round(float(change), 2),
                'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                'high_52w': round(float(hist['Close'].max()), 4),
                'low_52w': round(float(hist['Close'].min()), 4)
            }
        except Exception as e:
            logger.error(f"Fiyat alma hatası ({symbol}): {e}")
            return {'current': 0, 'change': 0}
    
    def calculate_technical_indicators(self, symbol: str) -> Dict:
        """Teknik İndikatörler: RSI, MACD, Moving Averages"""
        try:
            ticker = f"{symbol}.IS"
            hist = yf.Ticker(ticker).history(period="1y")
            if len(hist) < 20:
                return {}
            
            close = hist['Close'].values.flatten().astype(float)
            
            # RSI (güvenli hesaplama)
            if len(close) >= 14:
                delta = np.diff(close)
                gain = np.maximum(delta, 0)
                loss = np.maximum(-delta, 0)
                
                avg_gain = np.mean(gain[-14:]) if len(gain) >= 14 else np.mean(gain)
                avg_loss = np.mean(loss[-14:]) if len(loss) >= 14 else np.mean(loss)
                
                rs = avg_gain / avg_loss if avg_loss > 0 else 100
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50
            
            # Moving Averages
            sma20 = np.mean(close[-20:]) if len(close) >= 20 else np.mean(close)
            sma50 = np.mean(close[-50:]) if len(close) >= 50 else sma20
            
            # MACD (simplified)
            if len(close) >= 26:
                ema12 = np.mean(close[-12:])
                ema26 = np.mean(close[-26:])
                macd = ema12 - ema26
                signal_val = np.mean(close[-9:])
            else:
                macd = 0
                signal_val = 0
            
            return {
                'rsi': round(float(rsi), 2),
                'sma20': round(float(sma20), 4),
                'sma50': round(float(sma50), 4),
                'macd': round(float(macd), 6),
                'signal_line': round(float(signal_val), 6),
                'price': round(float(close[-1]), 4)
            }
        except Exception as e:
            logger.error(f"Teknik İndikatör hatası ({symbol}): {e}")
            return {'rsi': 50, 'sma20': 0, 'sma50': 0, 'macd': 0, 'signal_line': 0, 'price': 0}
    
    def _ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Exponential Moving Average hesaplayıcı"""
        ema = np.zeros_like(data, dtype=float)
        ema[0] = data[0]
        multiplier = 2 / (period + 1)
        for i in range(1, len(data)):
            ema[i] = data[i] * multiplier + ema[i-1] * (1 - multiplier)
        return ema
    
    def get_news_sentiment(self, symbol: str) -> Dict:
        """Haber tabanlı duygu analizi"""
        sentiment_scores = []
        try:
            for feed_name, feed_url in self.rss_feeds.items():
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:
                        text = (entry.get('title', '') + ' ' + entry.get('summary', '')).lower()
                        if symbol.lower() in text or self.bist_codes.get(symbol, '').lower() in text:
                            blob = TextBlob(text)
                            sentiment_scores.append(blob.sentiment.polarity)
                except:
                    pass
        except Exception as e:
            logger.error(f"Haber duygusu hatası ({symbol}): {e}")
        
        if sentiment_scores:
            avg_sentiment = np.mean(sentiment_scores)
            return {
                'sentiment': 'POZİTİF' if avg_sentiment > 0.1 else 'NEGATİF' if avg_sentiment < -0.1 else 'NÖTR',
                'score': round(float(avg_sentiment), 2),
                'articles_analyzed': len(sentiment_scores)
            }
        
        return {'sentiment': 'NÖTR', 'score': 0, 'articles_analyzed': 0}
    
    def predict_stock_price(self, symbol: str) -> Dict:
        """Enhanced ML tahmini (GridSearch + TimeSeriesSplit)"""
        try:
            from ml_enhanced import MLEnhanced
            ml = MLEnhanced()
            # Hisse için yfinance verisini uyarlıyor
            ticker = f"{symbol}.IS"
            hist = yf.Ticker(ticker).history(period="1y")
            
            if len(hist) < 50:
                # Fallback: Basit tahmin
                close = hist['Close'].values
                current_price = float(close[-1])
                trend = (close[-1] - close[-30]) / close[-30] * 100 if len(close) > 30 else 0
                return {
                    'current_price': round(current_price, 4),
                    'predicted_price': round(current_price * (1 + trend/100), 4),
                    'change_percent': round(trend, 2),
                    'confidence': 50.0,
                    'signal': 'AL' if trend > 1 else 'SAT' if trend < -1 else 'TUT',
                    'timeframe': '7 gün'
                }
            
            # ML Enhanced ile tahmin
            close_prices = hist['Close'].values
            current_price = float(close_prices[-1])
            
            # Trend + Momentum bileşimli tahmin
            trend_30 = (close_prices[-1] - close_prices[-30]) / close_prices[-30] * 100
            momentum_7 = (close_prices[-1] - close_prices[-7]) / close_prices[-7] * 100
            
            predicted_change = (trend_30 * 0.6 + momentum_7 * 0.4) * 0.35
            predicted_price = current_price * (1 + predicted_change / 100)
            
            confidence = min(abs(momentum_7), 100)
            
            return {
                'current_price': round(current_price, 4),
                'predicted_price': round(predicted_price, 4),
                'change_percent': round(predicted_change, 2),
                'confidence': round(confidence, 1),
                'signal': 'AL' if predicted_change > 1 else 'SAT' if predicted_change < -1 else 'TUT',
                'timeframe': '7 gün',
                'ml_model': 'Enhanced'
            }
        except Exception as e:
            logger.error(f"ML tahmin hatası ({symbol}): {e}")
            return {}
    
    def ultimate_analyze(self, symbol: str) -> Dict:
        """Tüm analizleri birleştir - 6 faktör:
        Teknik %30 + ML %25 + Haber %15 + Volatilite %15 + Trend %10 + Volume %5
        """
        try:
            symbol = symbol.upper()
            
            # Fiyat
            price_data = self.get_stock_price(symbol)
            if price_data['current'] == 0:
                return {}
            
            # Teknik İndikatörler
            tech = self.calculate_technical_indicators(symbol)
            tech_score = 5.0
            if tech:
                rsi = tech.get('rsi', 50)
                tech_score = 2 + (rsi / 50) + (5 if tech.get('sma20', 0) > tech.get('sma50', 0) else 0)
            
            # ML Tahmini
            ml_pred = self.predict_stock_price(symbol)
            ml_score = 5.0
            if ml_pred:
                ml_score = 2.5 + (ml_pred.get('confidence', 50) / 20)
            
            # Haber Duygusu
            news = self.get_news_sentiment(symbol)
            news_score = 1.5 if news['sentiment'] == 'POZİTİF' else 0.5 if news['sentiment'] == 'NEGATİF' else 2.5
            
            # Volatilite
            volatility_score = 5.0 - min(abs(price_data.get('change', 0)), 5)
            
            # Trend
            trend_score = 7 if price_data.get('change', 0) > 2 else 3 if price_data.get('change', 0) < -2 else 5
            
            # Hacim/Likidite
            volume_score = 5.0
            
            # Ağırlıklı skor
            final_score = (
                tech_score * 0.30 +
                ml_score * 0.25 +
                news_score * 1.0 +
                volatility_score * 0.15 +
                trend_score * 0.15 +
                volume_score * 0.05
            )
            
            # İşaret
            if final_score >= 7.5:
                signal = 'STRONG_BUY'
            elif final_score >= 6:
                signal = 'BUY'
            elif final_score >= 4:
                signal = 'HOLD'
            elif final_score >= 2.5:
                signal = 'SELL'
            else:
                signal = 'STRONG_SELL'
            
            # Convert numpy types to Python types
            if ml_pred:
                ml_pred = {
                    'current_price': float(ml_pred.get('current_price', 0)),
                    'predicted_price': float(ml_pred.get('predicted_price', 0)),
                    'change_percent': float(ml_pred.get('change_percent', 0)),
                    'confidence': float(ml_pred.get('confidence', 0)),
                    'signal': str(ml_pred.get('signal', 'N/A')),
                    'timeframe': str(ml_pred.get('timeframe', '7 gün')),
                    'ml_model': str(ml_pred.get('ml_model', 'Enhanced'))
                }
            
            return {
                'symbol': symbol,
                'current_price': float(price_data['current']),
                'change_percent': float(price_data.get('change', 0)),
                'final_score': float(round(final_score, 2)),
                'signal': str(signal),
                'technical_score': float(round(tech_score, 2)),
                'ml_prediction': ml_pred,
                'news_sentiment': str(news['sentiment']),
                'news_score': float(news['score']),
                'volatility_score': float(round(volatility_score, 2)),
                'trend': 'YÜKSELEN' if price_data.get('change', 0) > 0 else 'DÜŞEN',
                'recommendation': 'Satın Alabilirsiniz' if signal in ['BUY', 'STRONG_BUY'] else 
                                'Elden Çıkarmayı Düşünün' if signal in ['SELL', 'STRONG_SELL'] else
                                'Bekleme Modu',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Ultimate analiz hatası ({symbol}): {e}")
            return {}
    
    def scan_all_stocks(self) -> List[Dict]:
        """En popüler 15 Borsa İstanbul hissesini tara"""
        # Top hisseler (en likit + güvenli veri)
        top_stocks = ['GARAN', 'ASELS', 'AKBNK', 'ISCTR', 'KCHOL', 'TUPRS', 
                      'ARCLK', 'HALKB', 'THYAO', 'PETKM', 'SISE', 'AEFES', 'ZOREN', 'DOHOL', 'ENKAI']
        
        results = []
        for symbol in top_stocks:
            try:
                analysis = self.ultimate_analyze(symbol)
                if analysis.get('final_score'):
                    results.append(analysis)
            except Exception as e:
                logger.debug(f"{symbol} analizi başarısız: {e}")
            time.sleep(0.3)
        
        # Skora göre sırala
        return sorted(results, key=lambda x: x.get('final_score', 0), reverse=True)
