"""
COINGECKO API - Ek Veri Kaynağı
Piyasa değeri, hacim, arz bilgileri, global veriler
"""

import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CoinGeckoAPI:
    """CoinGecko API entegrasyonu"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300
        
        self.symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'XRP': 'ripple',
            'AVAX': 'avalanche-2',
            'DOGE': 'dogecoin',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'MATIC': 'matic-network',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'ATOM': 'cosmos',
            'LTC': 'litecoin',
            'SHIB': 'shiba-inu',
            'TRX': 'tron',
            'NEAR': 'near',
            'APT': 'aptos',
            'ARB': 'arbitrum',
            'OP': 'optimism',
            'INJ': 'injective-protocol',
            'SEI': 'sei-network',
            'SUI': 'sui',
            'JUV': 'juventus-fan-token',
            'ATM': 'atletico-madrid',
            'BAR': 'fc-barcelona-fan-token',
            'PSG': 'paris-saint-germain-fan-token',
            'CITY': 'manchester-city-fan-token',
            'GAL': 'galatasaray-fan-token',
            'CHZ': 'chiliz',
            'SANTOS': 'santos-fc-fan-token',
            'LAZIO': 'lazio-fan-token',
            'PORTO': 'fc-porto',
            'ACM': 'ac-milan-fan-token',
            'ASR': 'as-roma-fan-token',
            'INTER': 'inter-milan-fan-token',
            'NAP': 'napoli-fan-token',
        }
    
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Cache'den veri al"""
        if key in self.cache:
            if (datetime.now() - self.cache_time.get(key, datetime.min)).seconds < self.cache_duration:
                return self.cache[key]
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Cache'e veri kaydet"""
        self.cache[key] = data
        self.cache_time[key] = datetime.now()
    
    def get_global_data(self) -> Dict:
        """Global piyasa verileri"""
        cached = self._get_cached('global')
        if cached:
            return cached
        
        try:
            resp = requests.get(f"{self.base_url}/global", timeout=10)
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                result = {
                    'total_market_cap_usd': data.get('total_market_cap', {}).get('usd', 0),
                    'total_volume_24h_usd': data.get('total_volume', {}).get('usd', 0),
                    'btc_dominance': data.get('market_cap_percentage', {}).get('btc', 0),
                    'eth_dominance': data.get('market_cap_percentage', {}).get('eth', 0),
                    'active_cryptocurrencies': data.get('active_cryptocurrencies', 0),
                    'market_cap_change_24h': data.get('market_cap_change_percentage_24h_usd', 0)
                }
                self._set_cache('global', result)
                return result
        except Exception as e:
            logger.error(f"CoinGecko global error: {e}")
        
        return {}
    
    def get_coin_data(self, symbol: str) -> Dict:
        """Tek coin detaylı verileri"""
        coin_id = self.symbol_to_id.get(symbol.upper())
        if not coin_id:
            return {'error': f'{symbol} bulunamadı'}
        
        cached = self._get_cached(f'coin_{coin_id}')
        if cached:
            return cached
        
        try:
            resp = requests.get(
                f"{self.base_url}/coins/{coin_id}",
                params={
                    'localization': 'false',
                    'tickers': 'false',
                    'community_data': 'false',
                    'developer_data': 'false'
                },
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                market_data = data.get('market_data', {})
                
                result = {
                    'name': data.get('name', ''),
                    'symbol': data.get('symbol', '').upper(),
                    'market_cap_rank': data.get('market_cap_rank', 0),
                    'price_usd': market_data.get('current_price', {}).get('usd', 0),
                    'price_try': market_data.get('current_price', {}).get('try', 0),
                    'market_cap_usd': market_data.get('market_cap', {}).get('usd', 0),
                    'volume_24h_usd': market_data.get('total_volume', {}).get('usd', 0),
                    'change_24h': market_data.get('price_change_percentage_24h', 0),
                    'change_7d': market_data.get('price_change_percentage_7d', 0),
                    'change_30d': market_data.get('price_change_percentage_30d', 0),
                    'ath_usd': market_data.get('ath', {}).get('usd', 0),
                    'ath_change_pct': market_data.get('ath_change_percentage', {}).get('usd', 0),
                    'atl_usd': market_data.get('atl', {}).get('usd', 0),
                    'circulating_supply': market_data.get('circulating_supply', 0),
                    'total_supply': market_data.get('total_supply', 0),
                    'max_supply': market_data.get('max_supply', 0),
                    'high_24h_usd': market_data.get('high_24h', {}).get('usd', 0),
                    'low_24h_usd': market_data.get('low_24h', {}).get('usd', 0),
                }
                
                if result['max_supply'] and result['circulating_supply']:
                    result['supply_ratio'] = (result['circulating_supply'] / result['max_supply']) * 100
                else:
                    result['supply_ratio'] = None
                
                self._set_cache(f'coin_{coin_id}', result)
                return result
        except Exception as e:
            logger.error(f"CoinGecko coin error: {e}")
        
        return {'error': 'Veri alınamadı'}
    
    def get_trending(self) -> List[Dict]:
        """Trend olan coinler"""
        cached = self._get_cached('trending')
        if cached:
            return cached
        
        try:
            resp = requests.get(f"{self.base_url}/search/trending", timeout=10)
            if resp.status_code == 200:
                coins = resp.json().get('coins', [])
                result = []
                for item in coins[:10]:
                    coin = item.get('item', {})
                    result.append({
                        'name': coin.get('name', ''),
                        'symbol': coin.get('symbol', ''),
                        'market_cap_rank': coin.get('market_cap_rank', 0),
                        'price_btc': coin.get('price_btc', 0),
                        'score': coin.get('score', 0)
                    })
                self._set_cache('trending', result)
                return result
        except Exception as e:
            logger.error(f"CoinGecko trending error: {e}")
        
        return []
    
    def format_coin_report(self, symbol: str) -> str:
        """Coin için Telegram formatında rapor"""
        data = self.get_coin_data(symbol)
        
        if 'error' in data:
            return f"❌ {symbol}: {data['error']}"
        
        if data.get('change_24h', 0) > 0:
            change_emoji = "🟢"
        elif data.get('change_24h', 0) < 0:
            change_emoji = "🔴"
        else:
            change_emoji = "⚪"
        
        supply_text = ""
        if data.get('supply_ratio'):
            supply_text = f"\n   Dolaşımdaki arz: %{data['supply_ratio']:.1f}"
        
        report = f"""📊 <b>{data['name']} ({data['symbol']})</b>
━━━━━━━━━━━━━━━━━━━━━━

💰 <b>FİYAT:</b>
   ${data['price_usd']:,.4f} | ₺{data['price_try']:,.4f}
   {change_emoji} 24s: {data['change_24h']:+.2f}%
   7g: {data['change_7d']:+.2f}% | 30g: {data['change_30d']:+.2f}%

📈 <b>PİYASA:</b>
   Sıralama: #{data['market_cap_rank']}
   Piyasa Değeri: ${data['market_cap_usd']:,.0f}
   24s Hacim: ${data['volume_24h_usd']:,.0f}{supply_text}

🏔️ <b>ATH/ATL:</b>
   ATH: ${data['ath_usd']:,.4f} ({data['ath_change_pct']:+.1f}% fark)
   ATL: ${data['atl_usd']:,.6f}
   24s Yüksek: ${data['high_24h_usd']:,.4f}
   24s Düşük: ${data['low_24h_usd']:,.4f}
"""
        return report


coingecko = CoinGeckoAPI()
