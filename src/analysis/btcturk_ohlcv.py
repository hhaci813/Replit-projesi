"""
Multi-Source OHLCV Veri Modülü
- BTCTurk ticker verileri
- Binance OHLCV (yedek)
- Multi-timeframe desteği (15dk, 1s, 4s, günlük)
- Cache sistemi
"""

import requests
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BTCTurkOHLCV:
    def __init__(self):
        self.base_url = "https://api.btcturk.com/api/v2"
        self.cache = {}
        self.cache_ttl = 60  # 1 dakika cache
        
        # Timeframe mapping (saniye cinsinden)
        self.timeframes = {
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400
        }
    
    def get_ticker(self, symbol="BTCTRY"):
        """Anlık fiyat verisi"""
        try:
            resp = requests.get(f"{self.base_url}/ticker", timeout=10)
            data = resp.json().get('data', [])
            for t in data:
                if t.get('pair') == symbol:
                    return {
                        'price': float(t.get('last', 0)),
                        'high': float(t.get('high', 0)),
                        'low': float(t.get('low', 0)),
                        'volume': float(t.get('volume', 0)),
                        'change': float(t.get('dailyPercent', 0)),
                        'bid': float(t.get('bid', 0)),
                        'ask': float(t.get('ask', 0))
                    }
            return None
        except Exception as e:
            logger.error(f"Ticker error: {e}")
            return None
    
    def get_ohlcv(self, symbol="BTCTRY", timeframe="1h", limit=100):
        """
        BTCTurk'ten OHLCV verileri çek
        symbol: BTCTRY, ETHTRY, vb.
        timeframe: 15m, 1h, 4h, 1d
        """
        cache_key = f"{symbol}_{timeframe}"
        
        # Cache kontrolü
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached['time'] < self.cache_ttl:
                return cached['data']
        
        try:
            # BTCTurk kline endpoint
            resolution = self.timeframes.get(timeframe, 3600)
            
            # Son N periyot için
            end_time = int(time.time())
            start_time = end_time - (resolution * limit)
            
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol,
                'resolution': resolution,
                'from': start_time,
                'to': end_time
            }
            
            resp = requests.get(url, params=params, timeout=15)
            
            if resp.status_code != 200:
                # Fallback: ticker'dan güncel veri
                return self._fallback_ohlcv(symbol)
            
            data = resp.json()
            
            if not data or 't' not in data:
                return self._fallback_ohlcv(symbol)
            
            ohlcv = []
            times = data.get('t', [])
            opens = data.get('o', [])
            highs = data.get('h', [])
            lows = data.get('l', [])
            closes = data.get('c', [])
            volumes = data.get('v', [])
            
            for i in range(len(times)):
                ohlcv.append({
                    'timestamp': times[i],
                    'open': float(opens[i]) if i < len(opens) else 0,
                    'high': float(highs[i]) if i < len(highs) else 0,
                    'low': float(lows[i]) if i < len(lows) else 0,
                    'close': float(closes[i]) if i < len(closes) else 0,
                    'volume': float(volumes[i]) if i < len(volumes) else 0
                })
            
            # Cache'e kaydet
            self.cache[cache_key] = {'data': ohlcv, 'time': time.time()}
            
            return ohlcv
            
        except Exception as e:
            logger.error(f"OHLCV error for {symbol}: {e}")
            return self._fallback_ohlcv(symbol)
    
    def _fallback_ohlcv(self, symbol):
        """Binance'ten OHLCV al (yedek)"""
        try:
            # BTCTurk symbol'ünü Binance'e çevir
            base = symbol.replace('TRY', '').replace('USDT', '')
            binance_symbol = f"{base}USDT"
            
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': binance_symbol,
                'interval': '1h',
                'limit': 50
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                ohlcv = []
                for k in data:
                    ohlcv.append({
                        'timestamp': k[0] // 1000,
                        'open': float(k[1]),
                        'high': float(k[2]),
                        'low': float(k[3]),
                        'close': float(k[4]),
                        'volume': float(k[5])
                    })
                return ohlcv
        except:
            pass
        
        # Son çare: ticker'dan
        ticker = self.get_ticker(symbol)
        if ticker:
            return [{
                'timestamp': int(time.time()),
                'open': ticker['price'],
                'high': ticker['high'],
                'low': ticker['low'],
                'close': ticker['price'],
                'volume': ticker['volume']
            }]
        return []
    
    def get_binance_ohlcv(self, symbol, timeframe='1h', limit=50):
        """Binance'ten direkt OHLCV al"""
        try:
            interval_map = {
                '15m': '15m',
                '1h': '1h', 
                '4h': '4h',
                '1d': '1d'
            }
            
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': f"{symbol}USDT",
                'interval': interval_map.get(timeframe, '1h'),
                'limit': limit
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                ohlcv = []
                for k in data:
                    ohlcv.append({
                        'timestamp': k[0] // 1000,
                        'open': float(k[1]),
                        'high': float(k[2]),
                        'low': float(k[3]),
                        'close': float(k[4]),
                        'volume': float(k[5])
                    })
                return ohlcv
        except Exception as e:
            logger.error(f"Binance OHLCV error: {e}")
        return []
    
    def get_all_pairs(self):
        """Tüm TRY çiftlerini al"""
        try:
            resp = requests.get(f"{self.base_url}/ticker", timeout=10)
            data = resp.json().get('data', [])
            
            pairs = []
            for t in data:
                pair = t.get('pair', '')
                if pair.endswith('TRY') and not pair.startswith('USDT'):
                    pairs.append({
                        'pair': pair,
                        'symbol': pair.replace('TRY', ''),
                        'price': float(t.get('last', 0)),
                        'change': float(t.get('dailyPercent', 0)),
                        'volume': float(t.get('volume', 0)),
                        'high': float(t.get('high', 0)),
                        'low': float(t.get('low', 0))
                    })
            
            return pairs
        except Exception as e:
            logger.error(f"All pairs error: {e}")
            return []
    
    def get_multi_timeframe(self, symbol="BTCTRY"):
        """Birden fazla timeframe için OHLCV al"""
        result = {}
        for tf in ['15m', '1h', '4h', '1d']:
            result[tf] = self.get_ohlcv(symbol, tf, limit=50)
        return result


btcturk_ohlcv = BTCTurkOHLCV()
