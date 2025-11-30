"""Real-time Price Fetcher - BTCTurk Direct"""
import requests

class PriceFetcher:
    """BTCTurk doğrudan fiyat - hızlı ve güvenilir"""
    
    SESSION = requests.Session()
    
    @staticmethod
    def get_price(symbol):
        """BTCTurk'ten fiyat al"""
        
        # Symbol mapping
        btcturk_symbol = {
            'BTC-USD': 'BTCTRY',  # USD cinsinden değil, TRY cinsinden al
            'ETH-USD': 'ETHTRY',
            'AAPL': 'AAPL',  # Yahoo'dan fallback yapılacak
            'MSFT': 'MSFT',
            'GOOGL': 'GOOGL',
            'XRPTRY': 'XRPTRY'
        }
        
        pair = btcturk_symbol.get(symbol)
        if not pair:
            return None, "unknown"
        
        try:
            # BTCTurk API çağrısı
            resp = PriceFetcher.SESSION.get(
                f"https://api.btcturk.com/api/v2/ticker?pairSymbol={pair}",
                timeout=5
            )
            
            if resp.status_code == 200:
                data = resp.json().get('data', [])
                if data:
                    price = float(data[0].get('last', 0))
                    if price > 0:
                        # USD'ye çevir (BTC/TRY → BTC/USD)
                        if 'TRY' in pair:
                            price = price / 30  # 1 USD ≈ 30 TRY
                        return price, "BTCTurk"
        except:
            pass
        
        # Fallback - CoinGecko kripto için
        if symbol in ['BTC-USD', 'ETH-USD']:
            try:
                coin = 'bitcoin' if 'BTC' in symbol else 'ethereum'
                resp = PriceFetcher.SESSION.get(
                    f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd",
                    timeout=5
                )
                if resp.status_code == 200:
                    price = resp.json().get(coin, {}).get('usd')
                    if price:
                        return float(price), "CoinGecko"
            except:
                pass
        
        return None, "error"
    
    @staticmethod
    def format_price(price, symbol):
        """Fiyat format"""
        if price is None or price == 0:
            return "🔴 Veri Yok"
        
        if "TRY" in symbol:
            return f"₺{price:,.0f}"
        else:
            return f"${price:,.2f}"
