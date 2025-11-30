"""Multi-source Price Fetcher - Robust API Fallback"""
import requests
import time
from datetime import datetime

class PriceFetcher:
    """Çoklu kaynaktan güvenilir fiyat al - CoinGecko/IEX/Yahoo"""
    
    CRYPTOCURRENCIES = {
        'BTC-USD': 'bitcoin',
        'ETH-USD': 'ethereum',
    }
    
    @staticmethod
    def get_price(symbol):
        """Fiyat al - CoinGecko > IEX > Yahoo (fallback)"""
        
        # Kripto para
        if symbol in PriceFetcher.CRYPTOCURRENCIES:
            try:
                coin_id = PriceFetcher.CRYPTOCURRENCIES[symbol]
                resp = requests.get(
                    f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd",
                    timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    price = data.get(coin_id, {}).get('usd')
                    if price and price > 0:
                        return float(price), "coingecko"
            except:
                pass
        
        # Hisse senedi - IEX Cloud (free tier)
        if symbol not in PriceFetcher.CRYPTOCURRENCIES:
            try:
                # Yfinance'in yerine doğrudan yapı
                resp = requests.get(
                    f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=price",
                    timeout=5,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    price = data.get('quoteSummary', {}).get('result', [{}])[0].get('price', {}).get('regularMarketPrice', {}).get('raw')
                    if price and price > 0:
                        return float(price), "yahoo_direct"
            except:
                pass
        
        # Yfinance history fallback
        try:
            import yfinance as yf
            hist = yf.download(symbol, period="1d", progress=False)
            if hist is not None and not hist.empty:
                price = float(hist['Close'].iloc[-1])
                if price > 0:
                    return price, "history"
        except:
            pass
        
        return None, "error"
    
    @staticmethod
    def format_price(price, symbol):
        """Fiyatı formatlı göster"""
        if price is None or price == 0:
            return "N/A"
        
        if "TRY" in symbol:
            return f"₺{price:,.2f}"
        elif symbol in ["BTC-USD", "ETH-USD"]:
            return f"${price:,.0f}" if price > 100 else f"${price:.2f}"
        else:
            return f"${price:.2f}"
