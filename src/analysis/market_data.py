"""
Market Data Module - Max Version
- Fear & Greed Index
- Funding Rates (Binance)
- Global Market Data
"""

import requests
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class MarketDataProvider:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 dakika cache
    
    def get_fear_greed_index(self):
        """Alternative.me Fear & Greed Index"""
        cache_key = 'fear_greed'
        if cache_key in self.cache:
            if time.time() - self.cache[cache_key]['time'] < self.cache_ttl:
                return self.cache[cache_key]['data']
        
        try:
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('data'):
                fng = data['data'][0]
                result = {
                    'value': int(fng['value']),
                    'classification': fng['value_classification'],
                    'timestamp': datetime.now().isoformat()
                }
                
                self.cache[cache_key] = {'data': result, 'time': time.time()}
                logger.info(f"Fear & Greed: {result['value']} ({result['classification']})")
                return result
        except Exception as e:
            logger.error(f"Fear & Greed error: {e}")
        
        return {'value': 50, 'classification': 'Neutral', 'timestamp': None}
    
    def get_funding_rates(self, symbols=None):
        """Binance Futures Funding Rates"""
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'AVAXUSDT']
        
        cache_key = 'funding_rates'
        if cache_key in self.cache:
            if time.time() - self.cache[cache_key]['time'] < self.cache_ttl:
                return self.cache[cache_key]['data']
        
        try:
            url = "https://fapi.binance.com/fapi/v1/fundingRate"
            rates = {}
            
            for symbol in symbols:
                try:
                    params = {'symbol': symbol, 'limit': 1}
                    response = requests.get(url, params=params, timeout=5)
                    data = response.json()
                    
                    if data and len(data) > 0:
                        rate = float(data[0]['fundingRate']) * 100
                        rates[symbol.replace('USDT', '')] = {
                            'rate': round(rate, 4),
                            'sentiment': 'LONG' if rate > 0.01 else 'SHORT' if rate < -0.01 else 'NEUTRAL'
                        }
                except:
                    continue
            
            self.cache[cache_key] = {'data': rates, 'time': time.time()}
            return rates
        except Exception as e:
            logger.error(f"Funding rates error: {e}")
        
        return {}
    
    def get_long_short_ratio(self, symbol='BTCUSDT'):
        """Binance Long/Short Ratio"""
        try:
            url = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
            params = {'symbol': symbol, 'period': '1h', 'limit': 1}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data and len(data) > 0:
                ratio = float(data[0]['longShortRatio'])
                return {
                    'ratio': round(ratio, 2),
                    'long_pct': round(ratio / (1 + ratio) * 100, 1),
                    'short_pct': round(1 / (1 + ratio) * 100, 1),
                    'sentiment': 'BULLISH' if ratio > 1.2 else 'BEARISH' if ratio < 0.8 else 'NEUTRAL'
                }
        except Exception as e:
            logger.error(f"Long/Short ratio error: {e}")
        
        return {'ratio': 1.0, 'long_pct': 50, 'short_pct': 50, 'sentiment': 'NEUTRAL'}
    
    def get_open_interest(self, symbol='BTCUSDT'):
        """Binance Open Interest"""
        try:
            url = "https://fapi.binance.com/fapi/v1/openInterest"
            params = {'symbol': symbol}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data:
                return {
                    'open_interest': float(data['openInterest']),
                    'symbol': symbol
                }
        except Exception as e:
            logger.error(f"Open interest error: {e}")
        
        return None
    
    def get_global_market(self):
        """CoinGecko Global Market Data"""
        cache_key = 'global_market'
        if cache_key in self.cache:
            if time.time() - self.cache[cache_key]['time'] < self.cache_ttl:
                return self.cache[cache_key]['data']
        
        try:
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('data'):
                market = data['data']
                result = {
                    'total_market_cap_usd': market.get('total_market_cap', {}).get('usd', 0),
                    'total_volume_usd': market.get('total_volume', {}).get('usd', 0),
                    'btc_dominance': round(market.get('market_cap_percentage', {}).get('btc', 0), 1),
                    'eth_dominance': round(market.get('market_cap_percentage', {}).get('eth', 0), 1),
                    'market_cap_change_24h': round(market.get('market_cap_change_percentage_24h_usd', 0), 2),
                    'active_cryptocurrencies': market.get('active_cryptocurrencies', 0)
                }
                
                self.cache[cache_key] = {'data': result, 'time': time.time()}
                return result
        except Exception as e:
            logger.error(f"Global market error: {e}")
        
        return None
    
    def get_market_sentiment_score(self):
        """Tüm verileri birleştirip sentiment skoru hesapla"""
        score = 50  # Başlangıç: Nötr
        signals = []
        
        # Fear & Greed
        fng = self.get_fear_greed_index()
        if fng['value'] > 0:
            fng_contribution = (fng['value'] - 50) / 2  # -25 ile +25 arası
            score += fng_contribution
            
            if fng['value'] >= 75:
                signals.append(f"⚠️ Aşırı Açgözlülük: {fng['value']}")
            elif fng['value'] >= 55:
                signals.append(f"🟢 Açgözlülük: {fng['value']}")
            elif fng['value'] <= 25:
                signals.append(f"🔴 Aşırı Korku: {fng['value']}")
            elif fng['value'] <= 45:
                signals.append(f"🟡 Korku: {fng['value']}")
            else:
                signals.append(f"⚪ Nötr: {fng['value']}")
        
        # Funding Rates
        funding = self.get_funding_rates()
        if funding:
            btc_funding = funding.get('BTC', {}).get('rate', 0)
            if btc_funding > 0.05:
                score -= 10
                signals.append(f"⚠️ Yüksek Long: {btc_funding:.3f}%")
            elif btc_funding < -0.05:
                score += 10
                signals.append(f"🟢 Short Baskı: {btc_funding:.3f}%")
        
        # Long/Short Ratio
        ls_ratio = self.get_long_short_ratio()
        if ls_ratio['ratio'] > 1.5:
            score -= 5
            signals.append(f"⚠️ Çok Long: %{ls_ratio['long_pct']:.0f}")
        elif ls_ratio['ratio'] < 0.7:
            score += 5
            signals.append(f"🟢 Short Ağırlıklı: %{ls_ratio['short_pct']:.0f}")
        
        # Global Market
        global_data = self.get_global_market()
        if global_data:
            change_24h = global_data.get('market_cap_change_24h', 0)
            if change_24h > 3:
                score += 5
                signals.append(f"🟢 Piyasa +%{change_24h:.1f}")
            elif change_24h < -3:
                score -= 5
                signals.append(f"🔴 Piyasa %{change_24h:.1f}")
        
        score = max(0, min(100, score))
        
        return {
            'score': round(score),
            'signals': signals,
            'fear_greed': fng,
            'funding_rates': funding,
            'long_short': ls_ratio,
            'global': global_data
        }
