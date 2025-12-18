"""
Binance Exchange Entegrasyonu
Multi-exchange support için Binance API
"""

import os
import time
import hmac
import hashlib
import requests
import logging
from urllib.parse import urlencode
from datetime import datetime

logger = logging.getLogger(__name__)

class BinanceTrader:
    """Binance API entegrasyonu"""
    
    BASE_URL = "https://api.binance.com"
    
    def __init__(self):
        self.api_key = os.environ.get('BINANCE_API_KEY', '')
        self.api_secret = os.environ.get('BINANCE_API_SECRET', '')
    
    def _sign(self, params: dict) -> str:
        """İmza oluştur"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self) -> dict:
        return {'X-MBX-APIKEY': self.api_key}
    
    def get_ticker(self, symbol: str) -> dict:
        """Fiyat bilgisi (USDT paritesi)"""
        try:
            pair = f"{symbol.upper()}USDT"
            resp = requests.get(
                f"{self.BASE_URL}/api/v3/ticker/24hr",
                params={'symbol': pair},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'symbol': symbol,
                    'price': float(data.get('lastPrice', 0)),
                    'price_usd': float(data.get('lastPrice', 0)),
                    'bid': float(data.get('bidPrice', 0)),
                    'ask': float(data.get('askPrice', 0)),
                    'volume': float(data.get('volume', 0)),
                    'change_24h': float(data.get('priceChangePercent', 0)),
                    'high_24h': float(data.get('highPrice', 0)),
                    'low_24h': float(data.get('lowPrice', 0))
                }
            return {}
        except Exception as e:
            logger.error(f"Binance ticker hatası: {e}")
            return {}
    
    def get_all_tickers(self) -> list:
        """Tüm USDT paritelerinin fiyatları"""
        try:
            resp = requests.get(f"{self.BASE_URL}/api/v3/ticker/24hr", timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                usdt_pairs = [
                    {
                        'symbol': item['symbol'].replace('USDT', ''),
                        'price': float(item.get('lastPrice', 0)),
                        'change_24h': float(item.get('priceChangePercent', 0)),
                        'volume': float(item.get('quoteVolume', 0))
                    }
                    for item in data
                    if item['symbol'].endswith('USDT') and 
                    not any(x in item['symbol'] for x in ['UP', 'DOWN', 'BEAR', 'BULL'])
                ]
                return sorted(usdt_pairs, key=lambda x: x['volume'], reverse=True)[:100]
            return []
        except Exception as e:
            logger.error(f"Binance all tickers hatası: {e}")
            return []
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> list:
        """Mum verileri"""
        try:
            pair = f"{symbol.upper()}USDT"
            resp = requests.get(
                f"{self.BASE_URL}/api/v3/klines",
                params={'symbol': pair, 'interval': interval, 'limit': limit},
                timeout=10
            )
            
            if resp.status_code == 200:
                return [
                    {
                        'timestamp': k[0],
                        'open': float(k[1]),
                        'high': float(k[2]),
                        'low': float(k[3]),
                        'close': float(k[4]),
                        'volume': float(k[5])
                    }
                    for k in resp.json()
                ]
            return []
        except Exception as e:
            logger.error(f"Klines hatası: {e}")
            return []
    
    def get_balance(self) -> dict:
        """Hesap bakiyesi (API key gerekli)"""
        if not self.api_key or not self.api_secret:
            return {'error': 'API anahtarları gerekli'}
        
        try:
            params = {'timestamp': int(time.time() * 1000)}
            params['signature'] = self._sign(params)
            
            resp = requests.get(
                f"{self.BASE_URL}/api/v3/account",
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                balances = {}
                for b in data.get('balances', []):
                    free = float(b.get('free', 0))
                    locked = float(b.get('locked', 0))
                    if free > 0 or locked > 0:
                        balances[b['asset']] = {
                            'free': free,
                            'locked': locked,
                            'total': free + locked
                        }
                return balances
            else:
                return {'error': resp.text}
        except Exception as e:
            return {'error': str(e)}
    
    def place_order(self, symbol: str, side: str, quantity: float, 
                   order_type: str = 'MARKET', price: float = None) -> dict:
        """Order ver"""
        if not self.api_key or not self.api_secret:
            return {'success': False, 'error': 'API anahtarları gerekli'}
        
        try:
            pair = f"{symbol.upper()}USDT"
            
            params = {
                'symbol': pair,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': str(quantity),
                'timestamp': int(time.time() * 1000)
            }
            
            if order_type.upper() == 'LIMIT' and price:
                params['price'] = str(price)
                params['timeInForce'] = 'GTC'
            
            params['signature'] = self._sign(params)
            
            resp = requests.post(
                f"{self.BASE_URL}/api/v3/order",
                headers=self._get_headers(),
                params=params,
                timeout=15
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'success': True,
                    'order_id': data.get('orderId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'status': data.get('status')
                }
            else:
                return {'success': False, 'error': resp.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_top_gainers(self, limit: int = 10) -> list:
        """En çok yükselenler"""
        tickers = self.get_all_tickers()
        return sorted(tickers, key=lambda x: x['change_24h'], reverse=True)[:limit]
    
    def get_top_losers(self, limit: int = 10) -> list:
        """En çok düşenler"""
        tickers = self.get_all_tickers()
        return sorted(tickers, key=lambda x: x['change_24h'])[:limit]
    
    def get_top_volume(self, limit: int = 10) -> list:
        """En yüksek hacim"""
        tickers = self.get_all_tickers()
        return tickers[:limit]
    
    def format_market_overview(self) -> str:
        """Piyasa özeti mesajı"""
        try:
            btc = self.get_ticker('BTC')
            eth = self.get_ticker('ETH')
            gainers = self.get_top_gainers(5)
            losers = self.get_top_losers(5)
            
            msg = "🌍 <b>BINANCE GLOBAL PİYASA</b>\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            if btc:
                emoji = "🟢" if btc['change_24h'] > 0 else "🔴"
                msg += f"₿ <b>BTC:</b> ${btc['price']:,.2f} {emoji} %{btc['change_24h']:.2f}\n"
            
            if eth:
                emoji = "🟢" if eth['change_24h'] > 0 else "🔴"
                msg += f"⟠ <b>ETH:</b> ${eth['price']:,.2f} {emoji} %{eth['change_24h']:.2f}\n"
            
            msg += "\n🚀 <b>EN ÇOK YÜKSELENLER:</b>\n"
            for g in gainers:
                msg += f"   {g['symbol']}: ${g['price']:.4f} 🟢 +%{g['change_24h']:.1f}\n"
            
            msg += "\n📉 <b>EN ÇOK DÜŞENLER:</b>\n"
            for l in losers:
                msg += f"   {l['symbol']}: ${l['price']:.4f} 🔴 %{l['change_24h']:.1f}\n"
            
            return msg
            
        except Exception as e:
            return f"❌ Binance verisi alınamadı: {e}"


class MultiExchangeAggregator:
    """Çoklu borsa fiyat karşılaştırma"""
    
    def __init__(self):
        self.binance = BinanceTrader()
    
    def compare_prices(self, symbol: str, usd_try_rate: float = 42.0) -> dict:
        """BTCTurk vs Binance fiyat karşılaştırma"""
        try:
            binance_ticker = self.binance.get_ticker(symbol)
            
            btcturk_resp = requests.get(
                f"https://api.btcturk.com/api/v2/ticker?pairSymbol={symbol}TRY",
                timeout=10
            )
            btcturk_price = 0
            if btcturk_resp.status_code == 200:
                data = btcturk_resp.json().get('data', [])
                if data:
                    btcturk_price = float(data[0].get('last', 0))
            
            binance_price_try = binance_ticker.get('price', 0) * usd_try_rate
            
            diff_percent = 0
            if btcturk_price and binance_price_try:
                diff_percent = ((btcturk_price - binance_price_try) / binance_price_try) * 100
            
            arbitrage = "BTCTurk'te pahalı" if diff_percent > 0 else "BTCTurk'te ucuz"
            
            return {
                'symbol': symbol,
                'btcturk_price': btcturk_price,
                'binance_price_usd': binance_ticker.get('price', 0),
                'binance_price_try': binance_price_try,
                'difference_percent': diff_percent,
                'arbitrage_note': arbitrage if abs(diff_percent) > 0.5 else "Fark yok"
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_comparison(self, symbol: str) -> str:
        """Karşılaştırma mesajı"""
        data = self.compare_prices(symbol)
        
        if 'error' in data:
            return f"❌ Hata: {data['error']}"
        
        msg = f"⚖️ <b>{symbol} FİYAT KARŞILAŞTIRMA</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        msg += f"🇹🇷 BTCTurk: ₺{data['btcturk_price']:,.2f}\n"
        msg += f"🌍 Binance: ${data['binance_price_usd']:,.2f}\n"
        msg += f"   (≈ ₺{data['binance_price_try']:,.2f})\n\n"
        
        diff = data['difference_percent']
        emoji = "🔴" if diff > 0 else "🟢"
        msg += f"📊 Fark: {emoji} %{abs(diff):.2f}\n"
        msg += f"💡 {data['arbitrage_note']}\n"
        
        return msg


if __name__ == "__main__":
    binance = BinanceTrader()
    print(binance.format_market_overview())
