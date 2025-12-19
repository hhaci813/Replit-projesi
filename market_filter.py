"""
🔍 PİYASA FİLTRE SİSTEMİ
Volatilite, Likidite, Trend gücü kontrol
"""

import requests
import logging
from typing import Dict
import numpy as np

logger = logging.getLogger(__name__)

class MarketFilter:
    """Piyasa koşullarını kontrol et"""
    
    def __init__(self):
        self.min_liquidity_24h = 1000000  # 1M TL minimum
        self.max_volatility = 0.15  # %15 max volatilite
        self.min_volume_ratio = 0.8  # 80% ortalama hacim
    
    def check_market_conditions(self, symbol: str) -> Dict:
        """Piyasa koşullarını kontrol et"""
        try:
            # BTCTurk'ten veri al
            url = f"https://api.btcturk.com/api/v2/ticker/pair/{symbol}TRY"
            resp = requests.get(url, timeout=10)
            
            if resp.status_code != 200:
                return {'valid': False, 'reason': 'API hatası'}
            
            data = resp.json()['data']
            
            # 24h volume (TRY)
            volume_24h = float(data.get('volume24h', 0)) * float(data.get('last', 0))
            
            # Volatilite kontrolü (24h high/low spread)
            high = float(data.get('high24h', 0))
            low = float(data.get('low24h', 0))
            last = float(data.get('last', 0))
            
            if high > 0 and low > 0:
                volatility = (high - low) / last
            else:
                volatility = 0
            
            # Change kontrol
            change_24h = float(data.get('change', 0))
            
            filters = {
                'liquidity': {
                    'volume_24h': round(volume_24h, 2),
                    'valid': volume_24h >= self.min_liquidity_24h,
                    'reason': 'Yeterli hacim' if volume_24h >= self.min_liquidity_24h else f'Düşük hacim (₺{volume_24h/1e6:.1f}M < ₺1M)'
                },
                'volatility': {
                    'percent': round(volatility * 100, 1),
                    'valid': volatility <= self.max_volatility,
                    'reason': f"{'Volatilite normal' if volatility <= self.max_volatility else 'YÜKSEk volatilite (riskli)'}",
                },
                'momentum': {
                    'change_24h': round(change_24h, 2),
                    'valid': abs(change_24h) < 20,  # ±20% içinde
                    'reason': f"{'Momentum normal' if abs(change_24h) < 20 else 'Aşırı momentum (pump/dump)'}",
                }
            }
            
            # Genel karar
            all_valid = all(f['valid'] for f in filters.values())
            
            return {
                'symbol': symbol,
                'valid_for_trading': all_valid,
                'filters': filters,
                'recommendation': self._get_recommendation(filters),
                'risk_level': self._calculate_risk_level(filters)
            }
        
        except Exception as e:
            logger.error(f"Market filter hatası {symbol}: {e}")
            return {'valid': False, 'reason': str(e)}
    
    def _get_recommendation(self, filters: Dict) -> str:
        """Trading tavsiyesi"""
        if all(f['valid'] for f in filters.values()):
            return "✅ Trade edebilirsin - Ideal koşullar"
        elif sum(1 for f in filters.values() if f['valid']) >= 2:
            return "⚠️  Dikkatli trade - Bazı riskler var"
        else:
            return "🛑 Trade yapma - Piyasa riskli"
    
    def _calculate_risk_level(self, filters: Dict) -> str:
        """Risk seviyesi"""
        invalid_count = sum(1 for f in filters.values() if not f['valid'])
        if invalid_count == 0:
            return "LOW"
        elif invalid_count == 1:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def get_filter_message(self, symbol: str) -> str:
        """Telegram mesajı"""
        result = self.check_market_conditions(symbol)
        
        if 'error' in result or not result.get('valid_for_trading'):
            return f"⛔ {symbol} şu an trading için uygun değil"
        
        msg = f"🔍 {symbol} PİYASA KONTROL\n"
        msg += f"{'='*40}\n"
        
        f = result['filters']
        msg += f"📦 Hacim (24h): ₺{f['liquidity']['volume_24h']/1e6:.1f}M {'✅' if f['liquidity']['valid'] else '❌'}\n"
        msg += f"📊 Volatilite: {f['volatility']['percent']}% {'✅' if f['volatility']['valid'] else '❌'}\n"
        msg += f"⚡ Momentum (24h): {f['momentum']['change_24h']:+.1f}% {'✅' if f['momentum']['valid'] else '❌'}\n"
        msg += f"\n{result['recommendation']}\n"
        msg += f"⚠️  Risk Level: {result['risk_level']}"
        
        return msg
