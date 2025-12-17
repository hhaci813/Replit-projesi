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
    
    def _get_default_prediction(self, current_price: float, no_data: bool = False) -> Dict:
        """Veri yoksa varsayılan tahmin döndür - no_data her zaman işaretlenmeli"""
        price = current_price if current_price > 0 else 0
        return {
            'current_price': price,
            'prediction_7d': {
                'price': price,
                'change_percent': 0.0,
                'target': 0,
                'stop': 0,
                'signal': 'VERİ YOK',
                'no_data': True
            },
            'prediction_30d': {
                'price': price,
                'change_percent': 0.0,
                'target': 0,
                'stop': 0,
                'signal': 'VERİ YOK',
                'no_data': True
            },
            'confidence': 0.0,
            'volatility': 0.0,
            'rsi': 50.0,
            'volume_ratio': 1.0,
            'momentum_5d': 0.0,
            'trend_30d': 0.0,
            'no_data': True
        }
    
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
        """Gelişmiş ML tahmini - 7 gün ve 30 gün hedefler"""
        try:
            ticker = f"{symbol}.IS"
            hist = yf.Ticker(ticker).history(period="1y")
            
            # Fallback için minimum veri - her zaman no_data olarak işaretle
            if len(hist) < 10:
                short_hist = yf.Ticker(ticker).history(period="5d")
                if len(short_hist) > 0:
                    current_price = float(short_hist['Close'].iloc[-1])
                    return self._get_default_prediction(current_price, no_data=True)
                return self._get_default_prediction(0, no_data=True)
            
            # Kısa veri için basit tahmin
            if len(hist) < 50:
                close = hist['Close'].values.astype(float)
                current_price = float(close[-1])
                simple_change = ((close[-1] - close[0]) / close[0] * 100) / len(close) * 7
                return {
                    'current_price': round(current_price, 4),
                    'prediction_7d': {
                        'price': round(current_price * (1 + simple_change / 100), 4),
                        'change_percent': round(simple_change, 2),
                        'target': round(current_price * 1.05, 4),
                        'stop': round(current_price * 0.95, 4),
                        'signal': 'AL' if simple_change > 1 else 'SAT' if simple_change < -1 else 'TUT'
                    },
                    'prediction_30d': {
                        'price': round(current_price * (1 + simple_change * 4 / 100), 4),
                        'change_percent': round(simple_change * 4, 2),
                        'target': round(current_price * 1.10, 4),
                        'stop': round(current_price * 0.92, 4),
                        'signal': 'AL' if simple_change > 0.5 else 'SAT' if simple_change < -0.5 else 'TUT'
                    },
                    'confidence': 40.0,
                    'volatility': 5.0,
                    'rsi': 50.0,
                    'volume_ratio': 1.0,
                    'momentum_5d': 0.0,
                    'trend_30d': round(simple_change * 4, 2)
                }
            
            close = hist['Close'].values.astype(float)
            volume = hist['Volume'].values.astype(float)
            current_price = float(close[-1])
            
            # Trend analizi
            trend_7 = (close[-1] - close[-7]) / close[-7] * 100 if len(close) >= 7 else 0
            trend_30 = (close[-1] - close[-30]) / close[-30] * 100 if len(close) >= 30 else 0
            trend_90 = (close[-1] - close[-90]) / close[-90] * 100 if len(close) >= 90 else 0
            
            # Momentum hesapla
            momentum_5 = (close[-1] - close[-5]) / close[-5] * 100 if len(close) >= 5 else 0
            momentum_20 = (close[-1] - close[-20]) / close[-20] * 100 if len(close) >= 20 else 0
            
            # RSI hesapla
            delta = np.diff(close[-15:])
            gains = np.where(delta > 0, delta, 0)
            losses = np.where(delta < 0, -delta, 0)
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            rsi = 100 - (100 / (1 + rs))
            
            # Volatilite (20 günlük standart sapma)
            volatility = np.std(close[-20:]) / np.mean(close[-20:]) * 100 if len(close) >= 20 else 5
            
            # Hacim trendi
            avg_vol_20 = np.mean(volume[-20:]) if len(volume) >= 20 else 1
            vol_ratio = volume[-1] / avg_vol_20 if avg_vol_20 > 0 else 1
            
            # 7 günlük tahmin
            pred_7_change = (momentum_5 * 0.4 + trend_7 * 0.3 + (50 - rsi) * 0.03) * 0.8
            pred_7_price = current_price * (1 + pred_7_change / 100)
            
            # 30 günlük tahmin
            pred_30_change = (trend_30 * 0.4 + momentum_20 * 0.3 + trend_90 * 0.1 + (50 - rsi) * 0.05) * 0.6
            pred_30_price = current_price * (1 + pred_30_change / 100)
            
            # Güven seviyesi
            confidence = 50
            if abs(momentum_5) < 3 and abs(trend_7) < 5:
                confidence += 20  # Stabil trend = yüksek güven
            if vol_ratio > 1.5:
                confidence += 10  # Yüksek hacim = güvenilir hareket
            if rsi > 30 and rsi < 70:
                confidence += 15  # Normal RSI bölgesi
            confidence = min(confidence, 85)
            
            # Hedef ve stop seviyeler
            target_7 = current_price * (1 + max(pred_7_change, volatility) / 100)
            stop_7 = current_price * (1 - volatility / 100)
            target_30 = current_price * (1 + max(pred_30_change, volatility * 1.5) / 100)
            stop_30 = current_price * (1 - volatility * 1.2 / 100)
            
            # Sinyal belirleme
            if pred_7_change > 3 and rsi < 60:
                signal_7 = 'GÜÇLÜ AL'
            elif pred_7_change > 1:
                signal_7 = 'AL'
            elif pred_7_change < -3 and rsi > 40:
                signal_7 = 'GÜÇLÜ SAT'
            elif pred_7_change < -1:
                signal_7 = 'SAT'
            else:
                signal_7 = 'TUT'
            
            if pred_30_change > 5:
                signal_30 = 'GÜÇLÜ AL'
            elif pred_30_change > 2:
                signal_30 = 'AL'
            elif pred_30_change < -5:
                signal_30 = 'GÜÇLÜ SAT'
            elif pred_30_change < -2:
                signal_30 = 'SAT'
            else:
                signal_30 = 'TUT'
            
            return {
                'current_price': round(current_price, 4),
                'prediction_7d': {
                    'price': round(pred_7_price, 4),
                    'change_percent': round(pred_7_change, 2),
                    'target': round(target_7, 4),
                    'stop': round(stop_7, 4),
                    'signal': signal_7
                },
                'prediction_30d': {
                    'price': round(pred_30_price, 4),
                    'change_percent': round(pred_30_change, 2),
                    'target': round(target_30, 4),
                    'stop': round(stop_30, 4),
                    'signal': signal_30
                },
                'confidence': round(confidence, 1),
                'volatility': round(volatility, 2),
                'rsi': round(rsi, 1),
                'volume_ratio': round(vol_ratio, 2),
                'momentum_5d': round(momentum_5, 2),
                'trend_30d': round(trend_30, 2)
            }
        except Exception as e:
            logger.error(f"ML tahmin hatası ({symbol}): {e}")
            # Hata durumunda fiyat almayı dene - her zaman no_data işaretle
            try:
                ticker = f"{symbol}.IS"
                short_hist = yf.Ticker(ticker).history(period="5d")
                if len(short_hist) > 0:
                    current_price = float(short_hist['Close'].iloc[-1])
                    return self._get_default_prediction(current_price, no_data=True)
            except:
                pass
            return self._get_default_prediction(0, no_data=True)
    
    def ultimate_analyze(self, symbol: str) -> Dict:
        """Kripto kalitesinde detaylı hisse analizi:
        Teknik %30 + ML %25 + Haber %15 + Volatilite %15 + Trend %10 + Volume %5
        """
        try:
            symbol = symbol.upper()
            company_name = self.bist_codes.get(symbol, symbol)
            
            # Fiyat verisi
            price_data = self.get_stock_price(symbol)
            if price_data['current'] == 0:
                return {}
            
            current_price = float(price_data['current'])
            daily_change = float(price_data.get('change', 0))
            high_52w = float(price_data.get('high_52w', current_price))
            low_52w = float(price_data.get('low_52w', current_price))
            volume = int(price_data.get('volume', 0))
            
            # 52 haftalık pozisyon
            range_52w = high_52w - low_52w
            position_52w = ((current_price - low_52w) / range_52w * 100) if range_52w > 0 else 50
            
            # Teknik İndikatörler
            tech = self.calculate_technical_indicators(symbol)
            rsi = tech.get('rsi', 50) if tech else 50
            sma20 = tech.get('sma20', current_price) if tech else current_price
            sma50 = tech.get('sma50', current_price) if tech else current_price
            macd = tech.get('macd', 0) if tech else 0
            
            # Teknik skor
            tech_score = 5.0
            if rsi < 30:
                tech_score = 8.0  # Aşırı satım = AL fırsatı
            elif rsi > 70:
                tech_score = 2.0  # Aşırı alım = SAT
            else:
                tech_score = 5 + (50 - rsi) * 0.05
            
            if current_price > sma20 > sma50:
                tech_score += 1.5  # Yükseliş trendi
            elif current_price < sma20 < sma50:
                tech_score -= 1.5  # Düşüş trendi
            
            # ML Tahmini (7 gün ve 30 gün)
            ml_pred = self.predict_stock_price(symbol)
            
            # ml_pred her zaman bir değer döndürür (fallback ile)
            pred_7d = ml_pred.get('prediction_7d', self._get_default_prediction(current_price).get('prediction_7d'))
            pred_30d = ml_pred.get('prediction_30d', self._get_default_prediction(current_price).get('prediction_30d'))
            confidence = ml_pred.get('confidence', 50)
            
            # ML skor: tahmin yönüne göre
            ml_score = 5.0
            change_7 = pred_7d.get('change_percent', 0) if pred_7d else 0
            if change_7 > 3:
                ml_score = 8.0
            elif change_7 > 1:
                ml_score = 6.5
            elif change_7 < -3:
                ml_score = 2.0
            elif change_7 < -1:
                ml_score = 3.5
            
            # Haber Duygusu
            news = self.get_news_sentiment(symbol)
            news_sentiment = news.get('sentiment', 'NÖTR')
            news_article_count = news.get('articles_analyzed', 0)
            if news_sentiment == 'POZİTİF':
                news_score = 7.5
            elif news_sentiment == 'NEGATİF':
                news_score = 2.5
            else:
                news_score = 5.0
            
            # Volatilite skoru (düşük volatilite = yüksek skor)
            volatility = ml_pred.get('volatility', 5) if ml_pred else 5
            volatility_score = max(2, 8 - volatility * 0.5)
            
            # Trend skoru
            if daily_change > 3:
                trend_score = 8.0
            elif daily_change > 1:
                trend_score = 6.5
            elif daily_change < -3:
                trend_score = 2.0
            elif daily_change < -1:
                trend_score = 3.5
            else:
                trend_score = 5.0
            
            # Hacim skoru
            vol_ratio = ml_pred.get('volume_ratio', 1) if ml_pred else 1
            volume_score = min(8, 5 + vol_ratio)
            
            # Ağırlıklı final skor
            final_score = (
                tech_score * 0.30 +
                ml_score * 0.25 +
                news_score * 0.15 +
                volatility_score * 0.15 +
                trend_score * 0.10 +
                volume_score * 0.05
            )
            
            # Sinyal belirleme
            if final_score >= 7.5:
                signal = 'GÜÇLÜ AL'
                signal_emoji = '🟢🟢'
            elif final_score >= 6.0:
                signal = 'AL'
                signal_emoji = '🟢'
            elif final_score >= 4.5:
                signal = 'TUT'
                signal_emoji = '🟡'
            elif final_score >= 3.0:
                signal = 'SAT'
                signal_emoji = '🔴'
            else:
                signal = 'GÜÇLÜ SAT'
                signal_emoji = '🔴🔴'
            
            # Hedef ve stop hesapla
            target_7 = pred_7d.get('target', current_price * 1.05) if pred_7d else current_price * 1.05
            stop_7 = pred_7d.get('stop', current_price * 0.95) if pred_7d else current_price * 0.95
            target_30 = pred_30d.get('target', current_price * 1.10) if pred_30d else current_price * 1.10
            stop_30 = pred_30d.get('stop', current_price * 0.92) if pred_30d else current_price * 0.92
            
            # Öneri metni
            if signal in ['GÜÇLÜ AL', 'AL']:
                recommendation = f"Alım fırsatı! 7 günlük hedef: ₺{target_7:.2f}"
            elif signal in ['GÜÇLÜ SAT', 'SAT']:
                recommendation = f"Satış düşünün. Stop: ₺{stop_7:.2f}"
            else:
                recommendation = "Beklemede kalın, net sinyal yok"
            
            return {
                'symbol': symbol,
                'company_name': company_name,
                'current_price': current_price,
                'daily_change': daily_change,
                'volume': volume,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'position_52w': round(position_52w, 1),
                'final_score': round(final_score, 2),
                'signal': signal,
                'signal_emoji': signal_emoji,
                'technical': {
                    'rsi': round(rsi, 1),
                    'sma20': round(sma20, 4),
                    'sma50': round(sma50, 4),
                    'macd': round(macd, 6),
                    'score': round(tech_score, 2)
                },
                'prediction_7d': {
                    'price': round(pred_7d.get('price', current_price), 4),
                    'change': round(pred_7d.get('change_percent', 0), 2),
                    'target': round(target_7, 4),
                    'stop': round(stop_7, 4),
                    'signal': pred_7d.get('signal', 'TUT')
                },
                'prediction_30d': {
                    'price': round(pred_30d.get('price', current_price), 4),
                    'change': round(pred_30d.get('change_percent', 0), 2),
                    'target': round(target_30, 4),
                    'stop': round(stop_30, 4),
                    'signal': pred_30d.get('signal', 'TUT')
                },
                'confidence': confidence,
                'volatility': round(volatility, 2),
                'news': {
                    'sentiment': news_sentiment,
                    'score': round(news.get('score', 0), 3),
                    'articles': news_article_count
                },
                'recommendation': recommendation,
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
