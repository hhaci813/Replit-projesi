"""Real-time Price Fetcher - Multiple Live API Sources"""
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class PriceFetcher:
    """Gerçek zamanlı online fiyat - BTCTurk + CoinGecko + Web Scraping"""
    
    SESSION = requests.Session()
    RETRIES = Retry(total=3, backoff_factor=0.3, status_forcelist=(500, 502, 504))
    SESSION.mount('https://', HTTPAdapter(max_retries=RETRIES))
    SESSION.mount('http://', HTTPAdapter(max_retries=RETRIES))
    
    CRYPTO_MAP = {'BTC-USD': 'bitcoin', 'ETH-USD': 'ethereum'}
    
    # BTCTurk pairs
    BTCTURK_PAIRS = {
        'BTC-USD': 'BTCUSD',
        'XRPTRY': 'XRPTRY',
    }
    
    @staticmethod
    def get_price(symbol):
        """Online'dan gerçek fiyat al"""
        try:
            # 1. BTCTurk (Türkiye merkezli - en güvenilir)
            if symbol in PriceFetcher.BTCTURK_PAIRS:
                pair = PriceFetcher.BTCTURK_PAIRS[symbol]
                resp = PriceFetcher.SESSION.get(
                    f"https://api.btcturk.com/api/v2/ticker?pairSymbol={pair}",
                    timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json().get('data', [{}])[0]
                    price = float(data.get('last', 0))
                    if price > 0:
                        return price, "BTCTurk"
        except:
            pass
        
        try:
            # 2. KRIPTO - CoinGecko
            if symbol in PriceFetcher.CRYPTO_MAP:
                coin = PriceFetcher.CRYPTO_MAP[symbol]
                resp = PriceFetcher.SESSION.get(
                    f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd",
                    timeout=5
                )
                if resp.status_code == 200:
                    price = resp.json().get(coin, {}).get('usd')
                    if price and price > 0:
                        return float(price), "CoinGecko"
        except:
            pass
        
        # 2. HİSSE - Web Scraping (Yahoo Finance)
        if symbol not in PriceFetcher.CRYPTO_MAP:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                resp = PriceFetcher.SESSION.get(
                    f"https://finance.yahoo.com/quote/{symbol}",
                    timeout=8,
                    headers=headers
                )
                if resp.status_code == 200:
                    import re
                    match = re.search(r'"regularMarketPrice":\{[^}]*"fmt":"([\d,\.]+)"', resp.text)
                    if match:
                        price_str = match.group(1).replace(',', '')
                        price = float(price_str)
                        if price > 0:
                            return price, "Yahoo-Scrape"
            except:
                pass
        
        # 3. HISSE - Alternative Scraping
        if symbol not in PriceFetcher.CRYPTO_MAP:
            try:
                # TradingView embed API
                resp = PriceFetcher.SESSION.get(
                    f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}",
                    timeout=5,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    price = data.get('quoteResponse', {}).get('result', [{}])[0].get('regularMarketPrice')
                    if price and price > 0:
                        return float(price), "Yahoo-API-v7"
            except:
                pass
        
        # 4. BACKUP - IEX Cloud (serbest tiers bile var)
        if symbol not in PriceFetcher.CRYPTO_MAP:
            try:
                resp = PriceFetcher.SESSION.get(
                    f"https://api.example.com/stock/{symbol}/price",
                    timeout=5
                )
                if resp.status_code == 200:
                    price = resp.json().get('price')
                    if price and price > 0:
                        return float(price), "IEX"
            except:
                pass
        
        # 5. Fallback - yfinance (son çare)
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            # Doğrudan history'den çek (API'si daha güvenli)
            hist = yf.download(symbol, period="1d", progress=False, repair=True)
            if hist is not None and not hist.empty:
                price = float(hist['Close'].iloc[-1])
                if price > 0:
                    return price, "YFinance-History"
        except:
            pass
        
        return None, "FAILED"
    
    @staticmethod
    def format_price(price, symbol):
        """Format fiyat"""
        if price is None or price == 0:
            return "🔴 Veri Alınamıyor"
        
        if "TRY" in symbol:
            return f"₺{price:,.2f}"
        else:
            if price > 100:
                return f"${price:,.0f}"
            else:
                return f"${price:.2f}"
