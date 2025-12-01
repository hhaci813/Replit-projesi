"""Universal Price Fetcher - Tüm Araçlar"""
import requests
import yfinance as yf

class PriceFetcher:
    @staticmethod
    def get_price(symbol):
        """Kripto, hisse, tüm araçlardan fiyat al"""
        try:
            # BTC USD
            if symbol in ["BTC-USD", "BTC"]:
                resp = requests.get("https://api.btcturk.com/api/v2/ticker?pairSymbol=BTCTRY", timeout=5)
                if resp.status_code == 200:
                    price_try = float(resp.json()['data'][0]['last'])
                    price_usd = price_try / 30
                    return price_usd, "BTCTurk"
            
            # ETH USD
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
            
            # Diğer kripto
            if symbol in ["BNB", "SOL", "ADA", "XRP", "DOGE", "AVAX", "LINK", "MATIC"]:
                ticker = yf.Ticker(symbol + "-USD")
                data = ticker.history(period='1d')
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    return float(price), "YFinance"
            
            # Tüm hisseler - YFinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                price = data['Close'].iloc[-1]
                return float(price), "YFinance"
        
        except:
            pass
        
        return 0, "error"
