"""Universal Price Fetcher - Tüm Araçlar - ROBUST VERSİYON"""
import requests
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

class PriceFetcher:
    @staticmethod
    def get_price(symbol):
        """Kripto, hisse, tüm araçlardan fiyat al - SAFE"""
        try:
            if not symbol or not isinstance(symbol, str):
                return 0, "error"
            
            symbol = symbol.upper().strip()
            
            # BTC USD
            if symbol in ["BTC-USD", "BTC"]:
                try:
                    resp = requests.get("https://api.btcturk.com/api/v2/ticker?pairSymbol=BTCTRY", timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        if 'data' in data and data['data']:
                            price_try = float(data['data'][0].get('last', 0))
                            if price_try > 0:
                                price_usd = price_try / 30
                                return price_usd, "BTCTurk"
                except Exception as e:
                    logger.debug(f"BTC fetch error: {e}")
            
            # ETH USD
            if symbol in ["ETH-USD", "ETH"]:
                try:
                    resp = requests.get("https://api.btcturk.com/api/v2/ticker?pairSymbol=ETHTRY", timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        if 'data' in data and data['data']:
                            price_try = float(data['data'][0].get('last', 0))
                            if price_try > 0:
                                price_usd = price_try / 30
                                return price_usd, "BTCTurk"
                except Exception as e:
                    logger.debug(f"ETH fetch error: {e}")
            
            # XRPTRY - FIX
            if symbol in ["XRP", "XRPTRY"]:
                try:
                    resp = requests.get("https://api.btcturk.com/api/v2/ticker?pairSymbol=XRPTRY", timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        if 'data' in data and data['data']:
                            price = float(data['data'][0].get('last', 0))
                            if price > 0:
                                return price, "BTCTurk"
                except Exception as e:
                    logger.debug(f"XRP fetch error: {e}")
            
            # Diğer kripto
            if symbol in ["BNB", "SOL", "ADA", "XRP", "DOGE", "AVAX", "LINK", "MATIC"]:
                try:
                    ticker = yf.Ticker(symbol + "-USD")
                    data = ticker.history(period='1d')
                    if not data.empty:
                        price = float(data['Close'].iloc[-1])
                        if price > 0:
                            return price, "YFinance"
                except Exception as e:
                    logger.debug(f"Crypto fetch error {symbol}: {e}")
            
            # Tüm hisseler - YFinance
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d')
                if not data.empty:
                    price = float(data['Close'].iloc[-1])
                    if price > 0:
                        return price, "YFinance"
            except Exception as e:
                logger.debug(f"Stock fetch error {symbol}: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected price fetch error: {e}")
        
        return 0, "error"
