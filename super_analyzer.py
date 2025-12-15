"""
🧠 SÜPER ANALİZ SİSTEMİ - ULTRA VERSİYON
Tüm kaynakları tarar, ML ile analiz eder, yüksek doğruluklu sinyaller üretir
"""

import requests
import logging
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)

class SuperAnalyzer:
    """
    Çoklu kaynaklı süper analiz sistemi
    - CoinGecko: Piyasa verileri, trending, sosyal metrikler
    - CryptoPanic: Haber akışı
    - Alternative.me: Fear & Greed Index
    - BTCTurk: Anlık fiyatlar
    - YFinance: Teknik veriler
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300
        self.predictions_file = "predictions_history.json"
        self.load_predictions()
    
    def load_predictions(self):
        try:
            if os.path.exists(self.predictions_file):
                with open(self.predictions_file, 'r') as f:
                    self.predictions_history = json.load(f)
            else:
                self.predictions_history = []
        except:
            self.predictions_history = []
    
    def save_prediction(self, prediction: Dict):
        self.predictions_history.append(prediction)
        if len(self.predictions_history) > 1000:
            self.predictions_history = self.predictions_history[-1000:]
        try:
            with open(self.predictions_file, 'w') as f:
                json.dump(self.predictions_history, f)
        except:
            pass
    
    def get_fear_greed_index(self) -> Dict:
        """Alternative.me Fear & Greed Index"""
        cache_key = "fear_greed"
        if cache_key in self.cache:
            if time.time() - self.cache[cache_key]['time'] < 3600:
                return self.cache[cache_key]['data']
        
        try:
            resp = requests.get("https://api.alternative.me/fng/?limit=7", timeout=10)
            if resp.status_code == 200:
                data = resp.json().get('data', [])
                if data:
                    current = data[0]
                    value = int(current.get('value', 50))
                    classification = current.get('value_classification', 'Neutral')
                    
                    trend = []
                    for d in data[:7]:
                        trend.append(int(d.get('value', 50)))
                    
                    avg_7d = sum(trend) / len(trend) if trend else 50
                    trend_direction = "YUKSELIYOR" if value > avg_7d else "DUSUYOR" if value < avg_7d else "YATAY"
                    
                    result = {
                        'value': value,
                        'classification': classification,
                        'trend_7d': trend,
                        'avg_7d': avg_7d,
                        'trend_direction': trend_direction,
                        'signal': self._interpret_fear_greed(value, trend_direction)
                    }
                    self.cache[cache_key] = {'data': result, 'time': time.time()}
                    return result
        except Exception as e:
            logger.error(f"Fear & Greed hatası: {e}")
        
        return {'value': 50, 'classification': 'Neutral', 'signal': 'NOTR'}
    
    def _interpret_fear_greed(self, value: int, trend: str) -> str:
        if value <= 20:
            return "AŞIRI_KORKU_AL" if trend == "YUKSELIYOR" else "AŞIRI_KORKU_BEKLE"
        elif value <= 40:
            return "KORKU_FIRSATI" if trend == "YUKSELIYOR" else "KORKU_DIKKAT"
        elif value <= 60:
            return "NOTR"
        elif value <= 80:
            return "AÇGÖZLÜLÜK_DIKKAT" if trend == "DUSUYOR" else "AÇGÖZLÜLÜK"
        else:
            return "AŞIRI_AÇGÖZLÜLÜK_SAT"
    
    def get_coingecko_trending(self) -> List[Dict]:
        """CoinGecko Trending Coins"""
        try:
            resp = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=15)
            if resp.status_code == 200:
                coins = resp.json().get('coins', [])
                trending = []
                for c in coins[:10]:
                    item = c.get('item', {})
                    trending.append({
                        'symbol': item.get('symbol', '').upper(),
                        'name': item.get('name', ''),
                        'market_cap_rank': item.get('market_cap_rank', 0),
                        'price_btc': item.get('price_btc', 0),
                        'score': item.get('score', 0)
                    })
                return trending
        except Exception as e:
            logger.error(f"CoinGecko trending hatası: {e}")
        return []
    
    def get_coingecko_global(self) -> Dict:
        """CoinGecko Global Market Data"""
        try:
            resp = requests.get("https://api.coingecko.com/api/v3/global", timeout=15)
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                return {
                    'total_market_cap_usd': data.get('total_market_cap', {}).get('usd', 0),
                    'total_volume_usd': data.get('total_volume', {}).get('usd', 0),
                    'btc_dominance': data.get('market_cap_percentage', {}).get('btc', 0),
                    'eth_dominance': data.get('market_cap_percentage', {}).get('eth', 0),
                    'market_cap_change_24h': data.get('market_cap_change_percentage_24h_usd', 0),
                    'active_cryptocurrencies': data.get('active_cryptocurrencies', 0)
                }
        except Exception as e:
            logger.error(f"CoinGecko global hatası: {e}")
        return {}
    
    def symbol_to_coingecko_id(self, symbol: str) -> str:
        """Symbol'u CoinGecko ID'ye çevir"""
        mapping = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'AVAX': 'avalanche-2',
            'XRP': 'ripple', 'DOGE': 'dogecoin', 'ADA': 'cardano', 'DOT': 'polkadot',
            'MATIC': 'polygon', 'LINK': 'chainlink', 'UNI': 'uniswap', 'ATOM': 'cosmos',
            'LTC': 'litecoin', 'BCH': 'bitcoin-cash', 'SHIB': 'shiba-inu', 'TRX': 'tron',
            'NEAR': 'near', 'APT': 'aptos', 'ARB': 'arbitrum', 'OP': 'optimism',
            'FIL': 'filecoin', 'ICP': 'internet-computer', 'HBAR': 'hedera-hashgraph',
            'VET': 'vechain', 'ALGO': 'algorand', 'FTM': 'fantom', 'SAND': 'the-sandbox',
            'MANA': 'decentraland', 'GALA': 'gala', 'APE': 'apecoin', 'CRO': 'crypto-com-chain',
            'EGLD': 'elrond-erd-2', 'THETA': 'theta-token', 'AAVE': 'aave', 'MKR': 'maker',
            'GRT': 'the-graph', 'SNX': 'synthetix-network-token', 'LDO': 'lido-dao',
            'RNDR': 'render-token', 'INJ': 'injective-protocol', 'SUI': 'sui', 'SEI': 'sei-network'
        }
        return mapping.get(symbol.upper(), symbol.lower())
    
    def get_coingecko_coin_data(self, symbol: str) -> Dict:
        """CoinGecko tek coin detayı"""
        try:
            coin_id = self.symbol_to_coingecko_id(symbol)
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'true'
            }
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                market = data.get('market_data', {})
                community = data.get('community_data', {})
                
                return {
                    'price_usd': market.get('current_price', {}).get('usd', 0),
                    'price_change_24h': market.get('price_change_percentage_24h', 0),
                    'price_change_7d': market.get('price_change_percentage_7d', 0),
                    'price_change_30d': market.get('price_change_percentage_30d', 0),
                    'market_cap': market.get('market_cap', {}).get('usd', 0),
                    'volume_24h': market.get('total_volume', {}).get('usd', 0),
                    'ath': market.get('ath', {}).get('usd', 0),
                    'ath_change': market.get('ath_change_percentage', {}).get('usd', 0),
                    'twitter_followers': community.get('twitter_followers', 0),
                    'reddit_subscribers': community.get('reddit_subscribers', 0),
                    'sentiment_up': data.get('sentiment_votes_up_percentage', 50),
                    'sentiment_down': data.get('sentiment_votes_down_percentage', 50)
                }
        except Exception as e:
            logger.error(f"CoinGecko coin hatası: {e}")
        return {}
    
    def get_crypto_news(self) -> List[Dict]:
        """Haber akışı - RSS kaynaklarından"""
        news = []
        try:
            import feedparser
            rss_feeds = [
                "https://cointelegraph.com/rss",
                "https://www.coindesk.com/arc/outboundfeeds/rss/"
            ]
            
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:10]:
                        title = entry.get('title', '')
                        summary = entry.get('summary', '')
                        
                        positive_words = ['surge', 'rally', 'bullish', 'gains', 'soar', 'rise', 'up', 'high', 'growth']
                        negative_words = ['crash', 'drop', 'bearish', 'fall', 'down', 'low', 'decline', 'loss', 'fear']
                        
                        text = (title + ' ' + summary).lower()
                        pos_count = sum(1 for w in positive_words if w in text)
                        neg_count = sum(1 for w in negative_words if w in text)
                        
                        if pos_count > neg_count:
                            sentiment = 'POZITIF'
                        elif neg_count > pos_count:
                            sentiment = 'NEGATIF'
                        else:
                            sentiment = 'NOTR'
                        
                        currencies = []
                        crypto_names = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'AVAX': 'avalanche', 'XRP': 'ripple'}
                        for sym, name in crypto_names.items():
                            if sym.lower() in text or name in text:
                                currencies.append(sym)
                        
                        news.append({
                            'title': title,
                            'source': feed_url.split('/')[2],
                            'currencies': currencies,
                            'sentiment': sentiment,
                            'votes_positive': pos_count,
                            'votes_negative': neg_count
                        })
                except:
                    continue
        except Exception as e:
            logger.error(f"Haber RSS hatası: {e}")
        return news
    
    def get_btcturk_data(self) -> List[Dict]:
        """BTCTurk anlık veriler"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=15)
            if resp.status_code == 200:
                return resp.json().get('data', [])
        except:
            pass
        return []
    
    def calculate_technical_score(self, symbol: str) -> Dict:
        """Teknik analiz skoru"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}-USD")
            hist = ticker.history(period="30d")
            
            if len(hist) < 14:
                return {'score': 50, 'signals': []}
            
            closes = hist['Close'].values
            volumes = hist['Volume'].values
            
            score = 50
            signals = []
            
            delta = np.diff(closes)
            gains = np.where(delta > 0, delta, 0)
            losses = np.where(delta < 0, -delta, 0)
            
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 100
            
            if rsi < 30:
                score += 20
                signals.append(f"RSI aşırı satım ({rsi:.0f})")
            elif rsi > 70:
                score -= 20
                signals.append(f"RSI aşırı alım ({rsi:.0f})")
            elif 40 <= rsi <= 60:
                score += 5
                signals.append(f"RSI nötr ({rsi:.0f})")
            
            sma_20 = np.mean(closes[-20:])
            sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else sma_20
            current = closes[-1]
            
            if current > sma_20 > sma_50:
                score += 15
                signals.append("Yükseliş trendi")
            elif current < sma_20 < sma_50:
                score -= 15
                signals.append("Düşüş trendi")
            
            avg_vol = np.mean(volumes[-20:])
            last_vol = volumes[-1]
            
            if last_vol > avg_vol * 1.5:
                score += 10
                signals.append("Yüksek hacim")
            
            ema_12_arr = self._ema_array(closes, 12)
            ema_26_arr = self._ema_array(closes, 26)
            macd_line = ema_12_arr - ema_26_arr
            signal_arr = self._ema_array(macd_line, 9)
            
            if len(macd_line) > 0 and len(signal_arr) > 0:
                macd_val = macd_line[-1]
                signal_val = signal_arr[-1]
                
                if macd_val > signal_val:
                    score += 10
                    signals.append("MACD pozitif")
                elif macd_val < signal_val:
                    score -= 5
                    signals.append("MACD negatif")
            else:
                signals.append("MACD hesaplanamadı")
            
            return {
                'score': min(100, max(0, score)),
                'rsi': rsi,
                'trend': 'UP' if current > sma_20 else 'DOWN',
                'signals': signals
            }
        except Exception as e:
            logger.error(f"Teknik analiz hatası: {e}")
            return {'score': 50, 'signals': ['Veri alınamadı']}
    
    def _ema(self, data, period):
        if len(data) < period:
            return np.mean(data)
        alpha = 2 / (period + 1)
        ema = [data[0]]
        for i in range(1, len(data)):
            ema.append(alpha * data[i] + (1 - alpha) * ema[-1])
        return ema[-1]
    
    def _ema_array(self, data, period):
        """EMA dizisi döndür"""
        if len(data) < period:
            return np.array([np.mean(data)])
        alpha = 2 / (period + 1)
        ema = [data[0]]
        for i in range(1, len(data)):
            ema.append(alpha * data[i] + (1 - alpha) * ema[-1])
        return np.array(ema)
    
    def analyze_news_sentiment(self, symbol: str) -> Dict:
        """Haber sentiment analizi"""
        news = self.get_crypto_news()
        
        relevant = [n for n in news if symbol.upper() in [c.upper() for c in n.get('currencies', [])]]
        
        if not relevant:
            return {'sentiment': 'NOTR', 'score': 50, 'news_count': 0}
        
        positive = sum(1 for n in relevant if n['sentiment'] == 'POZITIF')
        negative = sum(1 for n in relevant if n['sentiment'] == 'NEGATIF')
        
        if positive > negative:
            sentiment = 'POZITIF'
            score = 60 + min(30, positive * 5)
        elif negative > positive:
            sentiment = 'NEGATIF'
            score = 40 - min(30, negative * 5)
        else:
            sentiment = 'NOTR'
            score = 50
        
        return {
            'sentiment': sentiment,
            'score': score,
            'news_count': len(relevant),
            'positive': positive,
            'negative': negative,
            'headlines': [n['title'] for n in relevant[:3]]
        }
    
    def super_analyze(self, symbol: str) -> Dict:
        """
        SÜPER ANALİZ - Tüm kaynakları birleştir
        """
        logger.info(f"🧠 {symbol} için süper analiz başlıyor...")
        
        fear_greed = self.get_fear_greed_index()
        global_data = self.get_coingecko_global()
        trending = self.get_coingecko_trending()
        coin_data = self.get_coingecko_coin_data(symbol.lower())
        technical = self.calculate_technical_score(symbol)
        news_sentiment = self.analyze_news_sentiment(symbol)
        
        is_trending = symbol.upper() in [t['symbol'] for t in trending]
        
        weights = {
            'technical': 0.35,
            'sentiment': 0.25,
            'fear_greed': 0.15,
            'social': 0.15,
            'trend': 0.10
        }
        
        technical_score = technical.get('score', 50)
        sentiment_score = news_sentiment.get('score', 50)
        fg_score = self._fear_greed_to_score(fear_greed.get('value', 50))
        social_score = self._social_to_score(coin_data)
        trend_score = 70 if is_trending else 50
        
        final_score = (
            technical_score * weights['technical'] +
            sentiment_score * weights['sentiment'] +
            fg_score * weights['fear_greed'] +
            social_score * weights['social'] +
            trend_score * weights['trend']
        )
        
        if final_score >= 75:
            action = "GÜÇLÜ_AL"
            confidence = "YÜKSEK"
        elif final_score >= 60:
            action = "AL"
            confidence = "ORTA-YÜKSEK"
        elif final_score >= 45:
            action = "TUT"
            confidence = "ORTA"
        elif final_score >= 30:
            action = "DÜŞÜR"
            confidence = "ORTA"
        else:
            action = "SAT"
            confidence = "YÜKSEK"
        
        result = {
            'symbol': symbol.upper(),
            'timestamp': datetime.now().isoformat(),
            'final_score': round(final_score, 1),
            'action': action,
            'confidence': confidence,
            'components': {
                'technical': {
                    'score': technical_score,
                    'weight': weights['technical'],
                    'details': technical
                },
                'sentiment': {
                    'score': sentiment_score,
                    'weight': weights['sentiment'],
                    'details': news_sentiment
                },
                'fear_greed': {
                    'score': fg_score,
                    'weight': weights['fear_greed'],
                    'details': fear_greed
                },
                'social': {
                    'score': social_score,
                    'weight': weights['social'],
                    'details': coin_data
                },
                'trending': {
                    'is_trending': is_trending,
                    'score': trend_score,
                    'weight': weights['trend']
                }
            },
            'global_market': global_data,
            'signals': self._generate_signals(technical, news_sentiment, fear_greed, is_trending)
        }
        
        self.save_prediction({
            'symbol': symbol,
            'score': final_score,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    def _fear_greed_to_score(self, value: int) -> int:
        if value <= 25:
            return 80
        elif value <= 45:
            return 65
        elif value <= 55:
            return 50
        elif value <= 75:
            return 35
        else:
            return 20
    
    def _social_to_score(self, coin_data: Dict) -> int:
        if not coin_data:
            return 50
        
        sentiment_up = coin_data.get('sentiment_up', 50)
        twitter = coin_data.get('twitter_followers', 0)
        
        score = 50
        if sentiment_up > 60:
            score += 15
        elif sentiment_up < 40:
            score -= 15
        
        if twitter > 1000000:
            score += 10
        elif twitter > 100000:
            score += 5
        
        return min(100, max(0, score))
    
    def _generate_signals(self, technical: Dict, sentiment: Dict, fear_greed: Dict, trending: bool) -> List[str]:
        signals = []
        
        if technical.get('score', 50) >= 70:
            signals.append("✅ Teknik göstergeler pozitif")
        elif technical.get('score', 50) <= 30:
            signals.append("❌ Teknik göstergeler negatif")
        
        if sentiment.get('sentiment') == 'POZITIF':
            signals.append("📰 Haberler olumlu")
        elif sentiment.get('sentiment') == 'NEGATIF':
            signals.append("📰 Haberler olumsuz")
        
        fg_value = fear_greed.get('value', 50)
        if fg_value <= 25:
            signals.append("😱 Aşırı korku = Alım fırsatı olabilir")
        elif fg_value >= 75:
            signals.append("🤑 Aşırı açgözlülük = Dikkatli ol")
        
        if trending:
            signals.append("🔥 Trending listesinde")
        
        for s in technical.get('signals', [])[:3]:
            signals.append(f"📊 {s}")
        
        return signals
    
    def format_super_analysis(self, result: Dict) -> str:
        """Telegram için süper analiz mesajı"""
        
        action_emoji = {
            'GÜÇLÜ_AL': '🟢🟢🟢',
            'AL': '🟢🟢',
            'TUT': '🟡',
            'DÜŞÜR': '🟠',
            'SAT': '🔴🔴'
        }.get(result['action'], '⚪')
        
        fg = result['components']['fear_greed']['details']
        fg_emoji = "😱" if fg.get('value', 50) < 30 else "😨" if fg.get('value', 50) < 45 else "😐" if fg.get('value', 50) < 55 else "😊" if fg.get('value', 50) < 75 else "🤑"
        
        global_market = result.get('global_market', {})
        
        msg = f"""🧠 <b>SÜPER ANALİZ: {result['symbol']}</b>
━━━━━━━━━━━━━━━━━━━━━━━━

{action_emoji} <b>KARAR:</b> {result['action']}
📊 <b>Skor:</b> {result['final_score']}/100
🎯 <b>Güven:</b> {result['confidence']}

<b>📈 DETAYLAR:</b>
• Teknik: {result['components']['technical']['score']}/100
• Sentiment: {result['components']['sentiment']['score']}/100
• Fear&Greed: {fg.get('value', 50)} {fg_emoji}
• Sosyal: {result['components']['social']['score']}/100
• Trending: {'✅' if result['components']['trending']['is_trending'] else '❌'}

<b>🌍 GLOBAL PİYASA:</b>
• BTC Dominance: %{global_market.get('btc_dominance', 0):.1f}
• 24s Değişim: %{global_market.get('market_cap_change_24h', 0):.2f}

<b>📊 SİNYALLER:</b>
"""
        for signal in result['signals'][:6]:
            msg += f"• {signal}\n"
        
        news = result['components']['sentiment']['details']
        if news.get('headlines'):
            msg += f"\n<b>📰 SON HABERLER:</b>\n"
            for h in news['headlines'][:2]:
                msg += f"• {h[:50]}...\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ <i>Bu yatırım tavsiyesi değildir.
Kendi araştırmanızı yapın.</i>"""
        
        return msg

super_analyzer = SuperAnalyzer()
