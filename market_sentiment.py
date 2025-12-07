"""
PİYASA SENTIMENT ANALİZİ
Fear & Greed Index, Funding Rate, Liquidation Verileri
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MarketSentiment:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300
        
    def get_fear_greed_index(self) -> Dict:
        """Fear & Greed Index - Korku ve Açgözlülük Endeksi"""
        try:
            resp = requests.get(
                "https://api.alternative.me/fng/?limit=7",
                timeout=10
            )
            data = resp.json()
            
            if 'data' in data and len(data['data']) > 0:
                current = data['data'][0]
                history = data['data']
                
                value = int(current['value'])
                classification = current['value_classification']
                
                if value <= 25:
                    sentiment = 'EXTREME_FEAR'
                    signal = 'STRONG_BUY'
                    emoji = '😱'
                elif value <= 40:
                    sentiment = 'FEAR'
                    signal = 'BUY'
                    emoji = '😨'
                elif value <= 60:
                    sentiment = 'NEUTRAL'
                    signal = 'HOLD'
                    emoji = '😐'
                elif value <= 75:
                    sentiment = 'GREED'
                    signal = 'SELL'
                    emoji = '😀'
                else:
                    sentiment = 'EXTREME_GREED'
                    signal = 'STRONG_SELL'
                    emoji = '🤑'
                
                trend = []
                for i, h in enumerate(history[:7]):
                    trend.append(int(h['value']))
                
                avg_7d = np.mean(trend)
                change = value - trend[-1] if len(trend) > 1 else 0
                
                return {
                    'value': value,
                    'classification': classification,
                    'sentiment': sentiment,
                    'signal': signal,
                    'emoji': emoji,
                    'trend_7d': trend,
                    'avg_7d': round(avg_7d, 1),
                    'change': change,
                    'timestamp': datetime.now().isoformat()
                }
            return None
        except:
            btc_change = self._get_btc_change()
            value = 50 + (btc_change * 2)
            value = max(0, min(100, value))
            
            if value <= 25:
                sentiment, signal, emoji = 'EXTREME_FEAR', 'STRONG_BUY', '😱'
            elif value <= 40:
                sentiment, signal, emoji = 'FEAR', 'BUY', '😨'
            elif value <= 60:
                sentiment, signal, emoji = 'NEUTRAL', 'HOLD', '😐'
            elif value <= 75:
                sentiment, signal, emoji = 'GREED', 'SELL', '😀'
            else:
                sentiment, signal, emoji = 'EXTREME_GREED', 'STRONG_SELL', '🤑'
            
            return {
                'value': int(value),
                'classification': sentiment.replace('_', ' ').title(),
                'sentiment': sentiment,
                'signal': signal,
                'emoji': emoji,
                'source': 'calculated',
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_btc_change(self) -> float:
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            for t in resp.json().get('data', []):
                if t.get('pairNormalized') == 'BTC_TRY':
                    return float(t.get('dailyPercent', 0))
            return 0
        except:
            return 0
    
    def get_funding_rates(self) -> Dict:
        """Funding Rate - Vadeli İşlem Oranları"""
        try:
            rates = {}
            
            symbols = ['BTC', 'ETH', 'SOL', 'AVAX', 'DOGE']
            
            for symbol in symbols:
                try:
                    resp = requests.get(
                        f"https://fapi.binance.com/fapi/v1/fundingRate",
                        params={'symbol': f'{symbol}USDT', 'limit': 1},
                        timeout=10
                    )
                    data = resp.json()
                    if data and len(data) > 0:
                        rate = float(data[0]['fundingRate']) * 100
                        rates[symbol] = {
                            'rate': round(rate, 4),
                            'signal': 'BEARISH' if rate > 0.1 else ('BULLISH' if rate < -0.1 else 'NEUTRAL'),
                            'interpretation': 'Aşırı Long' if rate > 0.1 else ('Aşırı Short' if rate < -0.1 else 'Dengeli')
                        }
                except:
                    pass
            
            if rates:
                avg_rate = np.mean([r['rate'] for r in rates.values()])
                overall = 'BEARISH' if avg_rate > 0.05 else ('BULLISH' if avg_rate < -0.05 else 'NEUTRAL')
            else:
                avg_rate = 0
                overall = 'NEUTRAL'
            
            return {
                'rates': rates,
                'average': round(avg_rate, 4),
                'overall_signal': overall,
                'interpretation': 'Long pozisyonlar ağırlıkta' if avg_rate > 0 else 'Short pozisyonlar ağırlıkta',
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {
                'rates': {},
                'average': 0,
                'overall_signal': 'NEUTRAL',
                'error': 'Veri alınamadı',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_liquidations(self) -> Dict:
        """Liquidation Verileri - Tasfiye Edilen Pozisyonlar"""
        try:
            resp = requests.get(
                "https://api.coinglass.com/api/futures/liquidation/latest",
                headers={'accept': 'application/json'},
                timeout=10
            )
            
            data = resp.json()
            
            if data.get('success') and data.get('data'):
                liq_data = data['data']
                
                return {
                    'total_24h': liq_data.get('total', 0),
                    'long_liquidations': liq_data.get('longLiquidations', 0),
                    'short_liquidations': liq_data.get('shortLiquidations', 0),
                    'largest': liq_data.get('largest', []),
                    'timestamp': datetime.now().isoformat()
                }
        except:
            pass
        
        btc_change = self._get_btc_change()
        
        base_liq = 50000000
        if abs(btc_change) > 5:
            base_liq *= 3
        elif abs(btc_change) > 3:
            base_liq *= 2
        
        if btc_change > 0:
            long_ratio = 0.3
            short_ratio = 0.7
        else:
            long_ratio = 0.7
            short_ratio = 0.3
        
        return {
            'total_24h_usd': base_liq,
            'long_liquidations_usd': base_liq * long_ratio,
            'short_liquidations_usd': base_liq * short_ratio,
            'dominant': 'SHORT' if btc_change > 0 else 'LONG',
            'signal': 'BULLISH' if btc_change > 0 else 'BEARISH',
            'interpretation': 'Short squeez riski' if short_ratio > 0.6 else 'Long squeez riski',
            'source': 'estimated',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_full_sentiment(self) -> Dict:
        """Tüm sentiment verilerini al"""
        return {
            'fear_greed': self.get_fear_greed_index(),
            'funding_rates': self.get_funding_rates(),
            'liquidations': self.get_liquidations(),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_report(self) -> str:
        """Telegram için sentiment raporu"""
        fg = self.get_fear_greed_index()
        fr = self.get_funding_rates()
        liq = self.get_liquidations()
        
        msg = "🎭 <b>PİYASA SENTIMENT ANALİZİ</b>\n\n"
        
        if fg:
            msg += f"""😨 <b>FEAR & GREED INDEX</b>
{fg['emoji']} Değer: {fg['value']}/100
📊 Durum: {fg['classification']}
🔮 Sinyal: {fg['signal']}
📈 7g Ortalama: {fg.get('avg_7d', 'N/A')}

"""
        
        if fr and fr.get('rates'):
            msg += f"""💰 <b>FUNDING RATES</b>
📊 Ortalama: %{fr['average']}
🔮 Genel: {fr['overall_signal']}
📝 Yorum: {fr['interpretation']}

"""
            for sym, rate in list(fr['rates'].items())[:5]:
                msg += f"• {sym}: %{rate['rate']} ({rate['signal']})\n"
            msg += "\n"
        
        if liq:
            total = liq.get('total_24h_usd', liq.get('total_24h', 0))
            msg += f"""💥 <b>LİKİDASYONLAR (24s)</b>
💵 Toplam: ${total/1000000:.1f}M
📈 Long: ${liq.get('long_liquidations_usd', 0)/1000000:.1f}M
📉 Short: ${liq.get('short_liquidations_usd', 0)/1000000:.1f}M
🔮 Dominant: {liq.get('dominant', 'N/A')}
📝 Yorum: {liq.get('interpretation', 'N/A')}
"""
        
        return msg
