"""Multi-source Price Fetcher - yfinance + CoinGecko Fallback"""
import yfinance as yf
import requests
import time

class PriceFetcher:
    """Çoklu kaynaktan gerçek fiyat al"""
    
    @staticmethod
    def get_price(symbol):
        """Gerçek fiyat al (yfinance > CoinGecko)"""
        # 1. yfinance'dan al
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.info.get('currentPrice') or ticker.info.get('bid')
            if price and price > 0:
                return float(price), "yfinance"
        except:
            pass
        
        # 2. CoinGecko'dan al (Crypto için)
        if symbol in ["BTC-USD", "ETH-USD"]:
            try:
                coin_id = "bitcoin" if "BTC" in symbol else "ethereum"
                resp = requests.get(
                    f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd",
                    timeout=3
                )
                if resp.status_code == 200:
                    data = resp.json()
                    price = data.get(coin_id, {}).get('usd')
                    if price and price > 0:
                        return float(price), "coingecko"
            except:
                pass
        
        # 3. Son çare: yfinance history'den
        try:
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
            return f"${price:,.2f}"
        else:
            return f"${price:.2f}"
