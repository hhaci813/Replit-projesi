"""Real Broker Data - Gerçek Fiyatlar ve Veriler"""
import yfinance as yf
import requests
from datetime import datetime
import os

class RealBrokerData:
    def __init__(self):
        self.cache = {}
    
    def get_real_price(self, symbol, asset_type="hisse"):
        """Gerçek fiyat al"""
        try:
            if asset_type == "hisse":
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d")
                if data.empty:
                    return None
                price = data['Close'].iloc[-1]
                return float(price)
            elif asset_type == "kripto":
                # CoinGecko API ile gerçek kripto fiyatı
                response = requests.get(
                    f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd",
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if symbol.lower() in data:
                        return float(data[symbol.lower()]['usd'])
        except:
            pass
        return None
    
    def get_real_portfolio_value(self, symbols):
        """Gerçek portföy değerini hesapla"""
        total = 0
        details = {}
        
        for symbol, quantity in symbols.items():
            price = self.get_real_price(symbol)
            if price:
                value = price * quantity
                total += value
                details[symbol] = {
                    "price": price,
                    "quantity": quantity,
                    "value": value
                }
        
        return {
            "total": total,
            "details": details,
            "updated": datetime.now().isoformat()
        }
    
    def get_market_summary(self):
        """Pazar özeti - gerçek veriler"""
        try:
            summary = {}
            
            # S&P 500
            sp500 = yf.Ticker("^GSPC").history(period="1d")
            if not sp500.empty:
                summary["SP500"] = {
                    "price": float(sp500['Close'].iloc[-1]),
                    "change": float(sp500['Close'].pct_change().iloc[-1] * 100)
                }
            
            # Nasdaq
            nasdaq = yf.Ticker("^IXIC").history(period="1d")
            if not nasdaq.empty:
                summary["NASDAQ"] = {
                    "price": float(nasdaq['Close'].iloc[-1]),
                    "change": float(nasdaq['Close'].pct_change().iloc[-1] * 100)
                }
            
            # Bitcoin
            btc_response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true",
                timeout=5
            )
            if btc_response.status_code == 200:
                btc_data = btc_response.json()['bitcoin']
                summary["BTC"] = {
                    "price": btc_data['usd'],
                    "change": btc_data['usd_24h_change']
                }
            
            return summary
        except:
            return {}
    
    def get_stock_data(self, symbol, period="5d"):
        """Hisse geçmiş verileri"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return None
            
            return {
                "symbol": symbol,
                "current_price": float(data['Close'].iloc[-1]),
                "open": float(data['Open'].iloc[-1]),
                "high": float(data['High'].max()),
                "low": float(data['Low'].min()),
                "volume": int(data['Volume'].iloc[-1]),
                "change_pct": float(data['Close'].pct_change().iloc[-1] * 100),
                "data": data.to_dict()
            }
        except:
            return None

if __name__ == "__main__":
    real_data = RealBrokerData()
    
    # Test
    price = real_data.get_real_price("AAPL")
    print(f"✅ AAPL Gerçek Fiyat: ${price}")
    
    summary = real_data.get_market_summary()
    print(f"✅ Market Summary: {summary}")
    
    stock_data = real_data.get_stock_data("MSFT")
    print(f"✅ MSFT Verileri: {stock_data['current_price']}")
