"""Simple Price Fetcher - Working APIs Only"""
import requests
import yfinance as yf

class PriceFetcher:
    @staticmethod
    def get_price(symbol):
        """Doğrudan çalışan API'ler"""
        try:
            # BTCTRY'den fiyat al
            if symbol in ["BTC-USD", "BTC"]:
                resp = requests.get("https://api.btcturk.com/api/v2/ticker?pairSymbol=BTCTRY", timeout=5)
                if resp.status_code == 200:
                    price_try = float(resp.json()['data'][0]['last'])
                    price_usd = price_try / 30
                    return price_usd, "BTCTurk"
            
            # ETH TRY
            if symbol in ["ETH-USD", "ETH"]:
                resp = requests.get("https://api.btcturk.com/api/v2/ticker?pairSymbol=ETHTRY", timeout=5)
                if resp.status_code == 200:
                    price_try = float(resp.json()['data'][0]['last'])
                    price_usd = price_try / 30
                    return price_usd, "BTCTurk"
            
            # XRPTRY
            if symbol == "XRPTRY":
                resp = requests.get("https://api.btcturk.com/api/v2/ticker?pairSymbol=XRPTRY", timeout=5)
                if resp.status_code == 200:
                    price = float(resp.json()['data'][0]['last'])
                    return price, "BTCTurk"
            
            # Hisse senetleri - yfinance
            if symbol in ["AAPL", "MSFT", "GOOGL"]:
                try:
                    ticker = yf.Ticker(symbol)
                    price = ticker.info.get('regularMarketPrice') or ticker.info.get('bid')
                    if price and price > 0:
                        return float(price), "YFinance"
                except:
                    pass
        except:
            pass
        
        return 0, "error"
