"""
ULTIMATE ANALYZER - TÜM SİSTEMLER BİR ARADA
ML + Whale + Sosyal + Teknik + Haber + Pattern = %100 Kapsam
"""

import requests
import feedparser
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob
from typing import Dict, List, Optional
import json
import time
import os
import logging

logger = logging.getLogger(__name__)

class UltimateAnalyzer:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300
        self.prediction_history = {}
        self.accuracy_log = []
        
        self.rss_feeds = {
            'cointelegraph': 'https://cointelegraph.com/rss',
            'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'bitcoinist': 'https://bitcoinist.com/feed/',
            'cryptonews': 'https://cryptonews.com/news/feed/',
            'newsbtc': 'https://www.newsbtc.com/feed/',
        }
        
        self.coingecko_map = self._load_coingecko_map()
        
    def _load_coingecko_map(self) -> Dict:
        return {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'XRP': 'ripple',
            'DOGE': 'dogecoin', 'ADA': 'cardano', 'AVAX': 'avalanche-2', 'DOT': 'polkadot',
            'LINK': 'chainlink', 'MATIC': 'polygon', 'UNI': 'uniswap', 'ATOM': 'cosmos',
            'LTC': 'litecoin', 'BCH': 'bitcoin-cash', 'SHIB': 'shiba-inu', 'TRX': 'tron',
            'NEAR': 'near', 'APT': 'aptos', 'ARB': 'arbitrum', 'OP': 'optimism',
            'FIL': 'filecoin', 'HBAR': 'hedera-hashgraph', 'VET': 'vechain', 'ALGO': 'algorand',
            'FTM': 'fantom', 'SAND': 'the-sandbox', 'MANA': 'decentraland', 'GALA': 'gala',
            'APE': 'apecoin', 'AAVE': 'aave', 'MKR': 'maker', 'GRT': 'the-graph',
            'RNDR': 'render-token', 'INJ': 'injective-protocol', 'SUI': 'sui', 'SEI': 'sei-network',
            'PEPE': 'pepe', 'WIF': 'dogwifcoin', 'BONK': 'bonk', 'FLOKI': 'floki',
            'XLM': 'stellar', 'EOS': 'eos', 'XMR': 'monero', 'ETC': 'ethereum-classic',
            'IMX': 'immutable-x', 'FLOW': 'flow', 'KAVA': 'kava', 'CAKE': 'pancakeswap-token',
            'CRV': 'curve-dao-token', 'YFI': 'yearn-finance', 'BAT': 'basic-attention-token',
            'CHZ': 'chiliz', 'ENJ': 'enjincoin', 'ZIL': 'zilliqa', 'IOTA': 'iota',
            'ZEC': 'zcash', 'DASH': 'dash', 'NEO': 'neo', 'WAVES': 'waves',
            'KSM': 'kusama', 'CELO': 'celo', 'ANKR': 'ankr', 'STORJ': 'storj',
            'OCEAN': 'ocean-protocol', 'FET': 'fetch-ai', 'AGIX': 'singularitynet',
            'WLD': 'worldcoin-wld', 'STX': 'blockstack', 'MINA': 'mina-protocol',
            'XTZ': 'tezos', 'THETA': 'theta-token', 'EGLD': 'elrond-erd-2',
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
    
    def symbol_to_cg(self, symbol: str) -> str:
        symbol = symbol.upper().replace('TRY', '').replace('USDT', '')
        if symbol in self.coingecko_map:
            return self.coingecko_map[symbol]
        return self._search_coingecko(symbol)
    
    def _search_coingecko(self, symbol: str) -> str:
        try:
            resp = requests.get(f"https://api.coingecko.com/api/v3/search?query={symbol}", timeout=10)
            if resp.status_code == 200:
                coins = resp.json().get('coins', [])
                for coin in coins:
                    if coin.get('symbol', '').upper() == symbol.upper():
                        cg_id = coin.get('id')
                        self.coingecko_map[symbol] = cg_id
                        return cg_id
        except:
            pass
        return symbol.lower()
    
    def get_fear_greed(self) -> Dict:
        def fetch():
            try:
                resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
                if resp.status_code == 200:
                    data = resp.json().get('data', [{}])[0]
                    return {
                        'value': int(data.get('value', 50)),
                        'classification': data.get('value_classification', 'Neutral'),
                        'signal': 'BUY' if int(data.get('value', 50)) < 30 else 
                                  'SELL' if int(data.get('value', 50)) > 70 else 'HOLD'
                    }
            except:
                pass
            return {'value': 50, 'classification': 'Neutral', 'signal': 'HOLD'}
        return self.get_cached('fear_greed', fetch, 600)
    
    def get_btc_dominance(self) -> Dict:
        def fetch():
            try:
                resp = requests.get("https://api.coingecko.com/api/v3/global", timeout=10)
                if resp.status_code == 200:
                    data = resp.json().get('data', {})
                    btc_dom = data.get('market_cap_percentage', {}).get('btc', 0)
                    eth_dom = data.get('market_cap_percentage', {}).get('eth', 0)
                    return {
                        'btc_dominance': round(btc_dom, 2),
                        'eth_dominance': round(eth_dom, 2),
                        'alt_season': btc_dom < 45,
                        'total_market_cap': data.get('total_market_cap', {}).get('usd', 0)
                    }
            except:
                pass
            return {'btc_dominance': 50, 'eth_dominance': 18, 'alt_season': False}
        return self.get_cached('btc_dom', fetch, 600)
    
    def get_trending_coins(self) -> List:
        def fetch():
            try:
                resp = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
                if resp.status_code == 200:
                    coins = resp.json().get('coins', [])
                    return [{'symbol': c['item']['symbol'].upper(), 
                             'name': c['item']['name'],
                             'rank': c['item'].get('market_cap_rank', 0)} 
                            for c in coins[:10]]
            except:
                pass
            return []
        return self.get_cached('trending', fetch, 600)
    
    def get_news_sentiment(self, keyword: str = 'bitcoin') -> Dict:
        def fetch():
            articles = []
            scores = []
            
            for source, url in self.rss_feeds.items():
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:15]:
                        title = entry.get('title', '')
                        summary = entry.get('summary', '')[:200]
                        
                        if keyword.lower() in (title + summary).lower():
                            text = f"{title} {summary}"
                            blob = TextBlob(text)
                            score = blob.sentiment.polarity
                            
                            bullish_words = ['bull', 'surge', 'rally', 'moon', 'breakout', 'soar', 'pump', 'buy']
                            bearish_words = ['bear', 'crash', 'dump', 'plunge', 'sell', 'drop', 'fall', 'fear']
                            
                            b_count = sum(1 for w in bullish_words if w in text.lower())
                            s_count = sum(1 for w in bearish_words if w in text.lower())
                            keyword_score = (b_count - s_count) * 0.1
                            final_score = score * 0.7 + keyword_score * 0.3
                            
                            articles.append({
                                'source': source,
                                'title': title[:60],
                                'score': round(final_score, 2),
                                'sentiment': 'BULLISH' if final_score > 0.1 else 'BEARISH' if final_score < -0.1 else 'NEUTRAL'
                            })
                            scores.append(final_score)
                except:
                    continue
            
            if scores:
                avg = sum(scores) / len(scores)
                return {
                    'count': len(articles),
                    'avg_score': round(avg, 3),
                    'sentiment': 'BULLISH' if avg > 0.1 else 'BEARISH' if avg < -0.1 else 'NEUTRAL',
                    'signal': 'BUY' if avg > 0.15 else 'SELL' if avg < -0.15 else 'HOLD',
                    'articles': articles[:5]
                }
            return {'count': 0, 'sentiment': 'NEUTRAL', 'signal': 'HOLD', 'articles': []}
        
        return self.get_cached(f'news_{keyword}', fetch, 600)
    
    def get_reddit_sentiment(self, subreddit: str = 'cryptocurrency') -> Dict:
        def fetch():
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                resp = requests.get(url, headers=headers, timeout=10)
                
                if resp.status_code == 200:
                    posts = resp.json().get('data', {}).get('children', [])
                    scores = []
                    hot_topics = []
                    
                    for post in posts:
                        data = post.get('data', {})
                        title = data.get('title', '')
                        ups = data.get('ups', 0)
                        
                        blob = TextBlob(title)
                        score = blob.sentiment.polarity
                        scores.append(score)
                        
                        if ups > 100:
                            hot_topics.append(title[:50])
                    
                    if scores:
                        avg = sum(scores) / len(scores)
                        return {
                            'post_count': len(posts),
                            'avg_sentiment': round(avg, 3),
                            'mood': 'BULLISH' if avg > 0.05 else 'BEARISH' if avg < -0.05 else 'NEUTRAL',
                            'hot_topics': hot_topics[:3]
                        }
            except:
                pass
            return {'mood': 'NEUTRAL', 'avg_sentiment': 0, 'hot_topics': []}
        
        return self.get_cached(f'reddit_{subreddit}', fetch, 600)
    
    def get_whale_activity(self) -> Dict:
        def fetch():
            try:
                resp = requests.get(
                    "https://blockchain.info/unconfirmed-transactions?format=json",
                    timeout=10
                )
                if resp.status_code == 200:
                    txs = resp.json().get('txs', [])
                    whale_txs = []
                    
                    for tx in txs:
                        total_btc = sum(out.get('value', 0) for out in tx.get('out', [])) / 100000000
                        if total_btc >= 10:
                            whale_txs.append({
                                'amount': round(total_btc, 2),
                                'hash': tx.get('hash', '')[:12] + '...'
                            })
                    
                    total = sum(t['amount'] for t in whale_txs)
                    return {
                        'count': len(whale_txs),
                        'total_btc': round(total, 2),
                        'activity': 'VERY_HIGH' if total > 1000 else 'HIGH' if total > 500 else 'MODERATE' if total > 100 else 'LOW',
                        'signal': 'WATCH' if total > 500 else 'NORMAL',
                        'recent': whale_txs[:5]
                    }
            except:
                pass
            return {'count': 0, 'activity': 'UNKNOWN', 'signal': 'NORMAL'}
        
        return self.get_cached('whale', fetch, 300)
    
    def get_exchange_flows(self) -> Dict:
        def fetch():
            try:
                resp = requests.get(
                    "https://api.blockchain.info/stats",
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        'btc_mined_24h': data.get('n_btc_mined', 0) / 100000000,
                        'blocks_24h': data.get('n_blocks_mined', 0),
                        'hash_rate': data.get('hash_rate', 0) / 1e18,
                        'difficulty': data.get('difficulty', 0) / 1e12
                    }
            except:
                pass
            return {}
        
        return self.get_cached('exchange_flows', fetch, 600)
    
    def get_technical_analysis(self, symbol: str) -> Dict:
        try:
            resp = requests.get(
                f"https://graph-api.btcturk.com/v1/klines/history",
                params={
                    "symbol": f"{symbol}USDT",
                    "resolution": "60",
                    "from": int((datetime.now() - timedelta(days=7)).timestamp()),
                    "to": int(datetime.now().timestamp())
                },
                timeout=15
            )
            
            if resp.status_code != 200:
                return self._fallback_technical(symbol)
            
            data = resp.json()
            if 'c' not in data or len(data['c']) < 20:
                return self._fallback_technical(symbol)
            
            closes = [float(x) for x in data['c']]
            highs = [float(x) for x in data.get('h', closes)]
            lows = [float(x) for x in data.get('l', closes)]
            volumes = [float(x) for x in data.get('v', [0]*len(closes))]
            
            current = closes[-1]
            
            sma_20 = sum(closes[-20:]) / 20
            sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20
            
            ema_12 = self._ema(closes, 12)
            ema_26 = self._ema(closes, 26)
            macd = ema_12 - ema_26
            signal_line = self._ema([macd], 9) if isinstance(macd, list) else macd
            
            rsi = self._calculate_rsi(closes, 14)
            
            bb_mid = sma_20
            bb_std = np.std(closes[-20:])
            bb_upper = bb_mid + 2 * bb_std
            bb_lower = bb_mid - 2 * bb_std
            
            avg_volume = sum(volumes[-20:]) / 20 if volumes else 0
            current_volume = volumes[-1] if volumes else 0
            volume_spike = current_volume > avg_volume * 2
            
            change_24h = ((current - closes[-24]) / closes[-24] * 100) if len(closes) >= 24 else 0
            change_7d = ((current - closes[0]) / closes[0] * 100)
            
            signals = []
            score = 50
            
            if rsi < 30:
                signals.append("RSI Aşırı Satım")
                score += 15
            elif rsi > 70:
                signals.append("RSI Aşırı Alım")
                score -= 15
            
            if current > sma_20:
                signals.append("SMA20 Üstünde")
                score += 10
            else:
                signals.append("SMA20 Altında")
                score -= 10
            
            if macd > 0:
                signals.append("MACD Pozitif")
                score += 10
            else:
                signals.append("MACD Negatif")
                score -= 10
            
            if current < bb_lower:
                signals.append("BB Alt Bandında")
                score += 10
            elif current > bb_upper:
                signals.append("BB Üst Bandında")
                score -= 10
            
            if volume_spike:
                signals.append("Hacim Spike")
            
            if score >= 70:
                recommendation = 'GÜÇLÜ_AL'
            elif score >= 55:
                recommendation = 'AL'
            elif score <= 30:
                recommendation = 'GÜÇLÜ_SAT'
            elif score <= 45:
                recommendation = 'SAT'
            else:
                recommendation = 'TUT'
            
            return {
                'price': current,
                'change_24h': round(change_24h, 2),
                'change_7d': round(change_7d, 2),
                'rsi': round(rsi, 1),
                'macd': round(macd, 6),
                'sma_20': round(sma_20, 6),
                'bb_upper': round(bb_upper, 6),
                'bb_lower': round(bb_lower, 6),
                'volume_spike': volume_spike,
                'signals': signals,
                'score': score,
                'recommendation': recommendation
            }
            
        except Exception as e:
            logger.error(f"Teknik analiz hatası {symbol}: {e}")
            return self._fallback_technical(symbol)
    
    def _fallback_technical(self, symbol: str) -> Dict:
        return {
            'price': 0, 'change_24h': 0, 'rsi': 50, 'macd': 0,
            'score': 50, 'recommendation': 'TUT', 'signals': ['Veri yok']
        }
    
    def _ema(self, data: List, period: int) -> float:
        if len(data) < period:
            return sum(data) / len(data) if data else 0
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema
    
    def _calculate_rsi(self, closes: List, period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def detect_patterns(self, symbol: str) -> Dict:
        try:
            resp = requests.get(
                f"https://graph-api.btcturk.com/v1/klines/history",
                params={
                    "symbol": f"{symbol}USDT",
                    "resolution": "D",
                    "from": int((datetime.now() - timedelta(days=30)).timestamp()),
                    "to": int(datetime.now().timestamp())
                },
                timeout=15
            )
            
            if resp.status_code != 200:
                return {'patterns': []}
            
            data = resp.json()
            if 'c' not in data or len(data['c']) < 10:
                return {'patterns': []}
            
            closes = [float(x) for x in data['c']]
            highs = [float(x) for x in data.get('h', closes)]
            lows = [float(x) for x in data.get('l', closes)]
            
            patterns = []
            
            if len(closes) >= 5:
                last5 = closes[-5:]
                if all(last5[i] < last5[i+1] for i in range(4)):
                    patterns.append({'name': 'Yükselen Trend', 'signal': 'BULLISH'})
                elif all(last5[i] > last5[i+1] for i in range(4)):
                    patterns.append({'name': 'Düşen Trend', 'signal': 'BEARISH'})
            
            if len(closes) >= 3:
                if closes[-1] > closes[-2] < closes[-3]:
                    patterns.append({'name': 'V Dip', 'signal': 'BULLISH'})
                elif closes[-1] < closes[-2] > closes[-3]:
                    patterns.append({'name': 'Ters V Tepe', 'signal': 'BEARISH'})
            
            recent_high = max(highs[-10:])
            recent_low = min(lows[-10:])
            current = closes[-1]
            
            if current >= recent_high * 0.98:
                patterns.append({'name': 'Direnç Testi', 'signal': 'WATCH'})
            elif current <= recent_low * 1.02:
                patterns.append({'name': 'Destek Testi', 'signal': 'WATCH'})
            
            fib_range = recent_high - recent_low
            fib_382 = recent_low + fib_range * 0.382
            fib_618 = recent_low + fib_range * 0.618
            
            return {
                'patterns': patterns,
                'support': round(recent_low, 6),
                'resistance': round(recent_high, 6),
                'fib_382': round(fib_382, 6),
                'fib_618': round(fib_618, 6)
            }
            
        except:
            return {'patterns': []}
    
    def ml_prediction(self, symbol: str) -> Dict:
        try:
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.preprocessing import MinMaxScaler
            
            resp = requests.get(
                f"https://graph-api.btcturk.com/v1/klines/history",
                params={
                    "symbol": f"{symbol}USDT",
                    "resolution": "D",
                    "from": int((datetime.now() - timedelta(days=90)).timestamp()),
                    "to": int(datetime.now().timestamp())
                },
                timeout=15
            )
            
            if resp.status_code != 200:
                return {'prediction': 'N/A'}
            
            data = resp.json()
            if 'c' not in data or len(data['c']) < 30:
                return {'prediction': 'N/A'}
            
            closes = [float(x) for x in data['c']]
            volumes = [float(x) for x in data.get('v', [0]*len(closes))]
            
            df = pd.DataFrame({'close': closes, 'volume': volumes})
            
            df['returns'] = df['close'].pct_change()
            df['ma_5'] = df['close'].rolling(5).mean()
            df['ma_10'] = df['close'].rolling(10).mean()
            df['volatility'] = df['returns'].rolling(10).std()
            df['momentum'] = df['close'] / df['close'].shift(5) - 1
            df['target'] = df['close'].shift(-7) / df['close'] - 1
            
            df = df.dropna()
            
            if len(df) < 20:
                return {'prediction': 'N/A'}
            
            features = ['returns', 'ma_5', 'ma_10', 'volatility', 'momentum']
            X = df[features].values
            y = df['target'].values
            
            X_train, y_train = X[:-7], y[:-7]
            
            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(X_train)
            
            rf = RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42)
            gb = GradientBoostingRegressor(n_estimators=50, max_depth=5, random_state=42)
            
            rf.fit(X_scaled, y_train)
            gb.fit(X_scaled, y_train)
            
            latest = scaler.transform(X[-1:])
            pred_rf = rf.predict(latest)[0]
            pred_gb = gb.predict(latest)[0]
            prediction = (pred_rf + pred_gb) / 2
            
            current_price = closes[-1]
            predicted_price = current_price * (1 + prediction)
            
            confidence = min(85, max(40, 60 + prediction * 100))
            
            self._save_prediction(symbol, current_price, predicted_price, prediction)
            
            if prediction > 0.10:
                signal = 'GÜÇLÜ_AL'
            elif prediction > 0.05:
                signal = 'AL'
            elif prediction < -0.10:
                signal = 'GÜÇLÜ_SAT'
            elif prediction < -0.05:
                signal = 'SAT'
            else:
                signal = 'TUT'
            
            return {
                'current_price': round(current_price, 6),
                'predicted_price': round(predicted_price, 6),
                'change_percent': round(prediction * 100, 2),
                'confidence': round(confidence, 1),
                'signal': signal,
                'timeframe': '7 gün'
            }
            
        except Exception as e:
            logger.error(f"ML tahmin hatası {symbol}: {e}")
            return {'prediction': 'N/A'}
    
    def _save_prediction(self, symbol: str, current: float, predicted: float, change: float):
        if symbol not in self.prediction_history:
            self.prediction_history[symbol] = []
        
        self.prediction_history[symbol].append({
            'date': datetime.now().isoformat(),
            'current': current,
            'predicted': predicted,
            'change': change
        })
        
        if len(self.prediction_history[symbol]) > 100:
            self.prediction_history[symbol] = self.prediction_history[symbol][-100:]
    
    def get_prediction_accuracy(self) -> Dict:
        try:
            accuracy_data = []
            
            for symbol, predictions in self.prediction_history.items():
                if len(predictions) >= 7:
                    for i in range(len(predictions) - 7):
                        pred = predictions[i]
                        actual_later = predictions[i + 7]['current'] if i + 7 < len(predictions) else None
                        
                        if actual_later:
                            predicted_change = pred['change']
                            actual_change = (actual_later - pred['current']) / pred['current']
                            
                            direction_correct = (predicted_change > 0) == (actual_change > 0)
                            accuracy_data.append(1 if direction_correct else 0)
            
            if accuracy_data:
                overall_accuracy = sum(accuracy_data) / len(accuracy_data) * 100
                return {
                    'accuracy': round(overall_accuracy, 1),
                    'sample_size': len(accuracy_data),
                    'status': 'OK'
                }
            
            return {'accuracy': 0, 'sample_size': 0, 'status': 'NO_DATA'}
            
        except:
            return {'accuracy': 0, 'status': 'ERROR'}
    
    def ultimate_analyze(self, symbol: str) -> Dict:
        symbol = symbol.upper().replace('TRY', '').replace('USDT', '')
        
        technical = self.get_technical_analysis(symbol)
        ml_pred = self.ml_prediction(symbol)
        patterns = self.detect_patterns(symbol)
        news = self.get_news_sentiment(symbol.lower())
        fear_greed = self.get_fear_greed()
        whale = self.get_whale_activity()
        reddit = self.get_reddit_sentiment()
        btc_dom = self.get_btc_dominance()
        trending = self.get_trending_coins()
        
        is_trending = any(t['symbol'] == symbol for t in trending)
        
        weights = {
            'technical': 0.30,
            'ml': 0.25,
            'news': 0.15,
            'fear_greed': 0.10,
            'whale': 0.10,
            'social': 0.10
        }
        
        tech_score = technical.get('score', 50)
        
        ml_change = ml_pred.get('change_percent', 0)
        ml_score = 50 + ml_change * 2
        ml_score = max(0, min(100, ml_score))
        
        news_sentiment = news.get('avg_score', 0)
        news_score = 50 + news_sentiment * 50
        
        fg = fear_greed.get('value', 50)
        fg_score = 100 - fg if fg > 50 else fg + 50
        
        whale_activity = whale.get('activity', 'MODERATE')
        whale_map = {'VERY_HIGH': 30, 'HIGH': 40, 'MODERATE': 50, 'LOW': 60, 'UNKNOWN': 50}
        whale_score = whale_map.get(whale_activity, 50)
        
        reddit_sent = reddit.get('avg_sentiment', 0)
        social_score = 50 + reddit_sent * 50
        
        final_score = (
            tech_score * weights['technical'] +
            ml_score * weights['ml'] +
            news_score * weights['news'] +
            fg_score * weights['fear_greed'] +
            whale_score * weights['whale'] +
            social_score * weights['social']
        )
        
        if is_trending:
            final_score += 5
        
        final_score = max(0, min(100, final_score))
        
        if final_score >= 70:
            recommendation = 'GÜÇLÜ_AL'
            emoji = '🔥'
        elif final_score >= 55:
            recommendation = 'AL'
            emoji = '🟢'
        elif final_score <= 30:
            recommendation = 'GÜÇLÜ_SAT'
            emoji = '🔴'
        elif final_score <= 45:
            recommendation = 'SAT'
            emoji = '🟡'
        else:
            recommendation = 'TUT'
            emoji = '⚪'
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'final_score': round(final_score, 1),
            'recommendation': recommendation,
            'emoji': emoji,
            'is_trending': is_trending,
            'technical': technical,
            'ml_prediction': ml_pred,
            'patterns': patterns,
            'news': news,
            'fear_greed': fear_greed,
            'whale': whale,
            'reddit': reddit,
            'btc_dominance': btc_dom,
            'component_scores': {
                'technical': round(tech_score, 1),
                'ml': round(ml_score, 1),
                'news': round(news_score, 1),
                'fear_greed': round(fg_score, 1),
                'whale': round(whale_score, 1),
                'social': round(social_score, 1)
            }
        }
    
    def generate_report(self, symbol: str) -> str:
        analysis = self.ultimate_analyze(symbol)
        
        tech = analysis['technical']
        ml = analysis['ml_prediction']
        patterns = analysis['patterns']
        news = analysis['news']
        fg = analysis['fear_greed']
        whale = analysis['whale']
        reddit = analysis['reddit']
        scores = analysis['component_scores']
        
        report = f"""
{analysis['emoji']} <b>ULTIMATE ANALİZ: {symbol}</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>SONUÇ: {analysis['recommendation']}</b>
🎯 <b>Skor: {analysis['final_score']}/100</b>
{'🔥 <b>TRENDING!</b>' if analysis['is_trending'] else ''}

━━━ TEKNİK ANALİZ ━━━
💰 Fiyat: ${tech.get('price', 0):.4f}
📈 24s: {tech.get('change_24h', 0):+.2f}%
📊 7g: {tech.get('change_7d', 0):+.2f}%
📉 RSI: {tech.get('rsi', 50):.1f}
📐 MACD: {tech.get('macd', 0):.6f}
🎯 Sinyal: {', '.join(tech.get('signals', [])[:3])}

━━━ ML TAHMİN (7 GÜN) ━━━
🤖 Beklenen: {ml.get('change_percent', 0):+.1f}%
🎯 Hedef: ${ml.get('predicted_price', 0):.4f}
📊 Güven: %{ml.get('confidence', 0):.0f}
📍 Sinyal: {ml.get('signal', 'N/A')}

━━━ PATTERN ANALİZ ━━━
📈 Destek: ${patterns.get('support', 0):.4f}
📉 Direnç: ${patterns.get('resistance', 0):.4f}
🎯 Fib 38.2%: ${patterns.get('fib_382', 0):.4f}
🎯 Fib 61.8%: ${patterns.get('fib_618', 0):.4f}
"""
        
        if patterns.get('patterns'):
            patterns_str = ', '.join([p['name'] for p in patterns['patterns'][:3]])
            report += f"🔍 Paternler: {patterns_str}\n"
        
        report += f"""
━━━ HABER SENTİMENT ━━━
📰 Haber Sayısı: {news.get('count', 0)}
😊 Duygu: {news.get('sentiment', 'NEUTRAL')}
📍 Sinyal: {news.get('signal', 'HOLD')}

━━━ PİYASA DURUŞU ━━━
😨 Fear & Greed: {fg.get('value', 50)} ({fg.get('classification', 'Neutral')})
🐋 Whale Aktivite: {whale.get('activity', 'UNKNOWN')} ({whale.get('count', 0)} işlem)
💬 Reddit: {reddit.get('mood', 'NEUTRAL')}

━━━ SKOR DETAY ━━━
📊 Teknik: {scores['technical']:.0f}/100
🤖 ML: {scores['ml']:.0f}/100
📰 Haber: {scores['news']:.0f}/100
😨 F&G: {scores['fear_greed']:.0f}/100
🐋 Whale: {scores['whale']:.0f}/100
💬 Sosyal: {scores['social']:.0f}/100

━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {analysis['timestamp']}
🤖 Ultimate Analyzer - Akıllı Yatırım
"""
        return report
    
    def scan_all_coins(self) -> List[Dict]:
        all_coins = [
            'BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'AVAX', 'DOT',
            'LINK', 'MATIC', 'UNI', 'ATOM', 'LTC', 'NEAR', 'APT', 'ARB',
            'OP', 'SUI', 'SEI', 'INJ', 'FIL', 'HBAR', 'VET', 'ALGO',
            'FTM', 'SAND', 'MANA', 'GALA', 'AAVE', 'MKR', 'GRT', 'RNDR',
            'PEPE', 'WIF', 'BONK', 'FLOKI', 'SHIB', 'APE', 'CHZ', 'ENJ',
            'BCH', 'TRX', 'XLM', 'EOS', 'XMR', 'ETC', 'IMX', 'FLOW',
            'KAVA', 'CAKE', 'CRV', 'YFI', 'BAT', 'ZIL', 'IOTA', 'ZEC',
            'DASH', 'NEO', 'WAVES', 'KSM', 'CELO', 'ANKR', 'STORJ',
            'OCEAN', 'FET', 'AGIX', 'WLD', 'STX', 'MINA', 'XTZ', 'THETA',
            'EGLD', 'RUNE', 'COMP', 'SNX', 'LDO', 'GMX', 'DYDX', 'ENS',
            'RPL', 'SSV', 'BLUR', 'MAGIC', 'CFX', 'JASMY', 'MASK',
            'CELR', 'BAND', 'API3', 'TWT', 'QTUM', 'OMG', 'ICX', 'KLAY',
            'LUNC', 'LUNA', 'BTT', 'WIN', 'SXP', 'RSR', 'RVN', 'SC',
            'HIVE', 'STEEM', 'DGB', 'XEM', 'HOT', 'ONE', 'ZRX', 'BAL',
            'SUSHI', 'RAY', 'ROSE', 'SKL', 'AUDIO', 'ICP'
        ]
        
        results = []
        for coin in all_coins:
            try:
                analysis = self.ultimate_analyze(coin)
                if analysis.get('final_score'):
                    results.append({
                        'symbol': coin,
                        'score': analysis['final_score'],
                        'recommendation': analysis['recommendation'],
                        'emoji': analysis['emoji'],
                        'change_24h': analysis['technical'].get('change_24h', 0),
                        'ml_change': analysis['ml_prediction'].get('change_percent', 0)
                    })
                time.sleep(0.5)
            except:
                continue
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results


if __name__ == '__main__':
    analyzer = UltimateAnalyzer()
    print(analyzer.generate_report('BTC'))
