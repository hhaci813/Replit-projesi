"""
WATCHLIST - FAVORİ KRİPTOLAR LİSTESİ
Kullanıcı favori kriptolarını takip etme
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional

WATCHLIST_FILE = "watchlist_data.json"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class Watchlist:
    def __init__(self):
        self.watchlists = self.load_watchlists()
        
    def load_watchlists(self) -> Dict:
        """Watchlist'leri yükle"""
        try:
            if os.path.exists(WATCHLIST_FILE):
                with open(WATCHLIST_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_watchlists(self):
        """Watchlist'leri kaydet"""
        try:
            with open(WATCHLIST_FILE, 'w') as f:
                json.dump(self.watchlists, f, indent=2)
        except:
            pass
    
    def add_to_watchlist(self, user_id: str, symbol: str) -> bool:
        """Watchlist'e ekle"""
        symbol = symbol.upper()
        
        if user_id not in self.watchlists:
            self.watchlists[user_id] = {
                'symbols': [],
                'created_at': datetime.now().isoformat()
            }
        
        if symbol not in self.watchlists[user_id]['symbols']:
            self.watchlists[user_id]['symbols'].append(symbol)
            self.save_watchlists()
            return True
        return False
    
    def remove_from_watchlist(self, user_id: str, symbol: str) -> bool:
        """Watchlist'ten çıkar"""
        symbol = symbol.upper()
        
        if user_id in self.watchlists:
            if symbol in self.watchlists[user_id]['symbols']:
                self.watchlists[user_id]['symbols'].remove(symbol)
                self.save_watchlists()
                return True
        return False
    
    def get_watchlist(self, user_id: str) -> List[str]:
        """Kullanıcı watchlist'ini al"""
        if user_id in self.watchlists:
            return self.watchlists[user_id].get('symbols', [])
        return []
    
    def get_watchlist_prices(self, user_id: str) -> List[Dict]:
        """Watchlist fiyatlarını al"""
        symbols = self.get_watchlist(user_id)
        if not symbols:
            return []
        
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            tickers = resp.json().get('data', [])
            
            results = []
            for symbol in symbols:
                for t in tickers:
                    if t.get('pairNormalized') == f"{symbol}_TRY":
                        price = float(t.get('last', 0))
                        change = float(t.get('dailyPercent', 0))
                        volume = float(t.get('volume', 0))
                        high = float(t.get('high', 0))
                        low = float(t.get('low', 0))
                        
                        results.append({
                            'symbol': symbol,
                            'price': price,
                            'change': change,
                            'volume': volume,
                            'high': high,
                            'low': low,
                            'trend': 'UP' if change > 0 else ('DOWN' if change < 0 else 'FLAT')
                        })
                        break
            
            return sorted(results, key=lambda x: x['change'], reverse=True)
        except:
            return []
    
    def generate_report(self, user_id: str) -> str:
        """Watchlist raporu oluştur"""
        prices = self.get_watchlist_prices(user_id)
        
        if not prices:
            return """⭐ <b>WATCHLIST</b>

Henüz favori eklenmemiş.

<b>Eklemek için:</b>
/favori BTC
/favori ETH

<b>Çıkarmak için:</b>
/favori_sil BTC"""
        
        msg = "⭐ <b>FAVORİ KRİPTOLAR</b>\n\n"
        
        total_change = 0
        for p in prices:
            emoji = '📈' if p['change'] > 0 else ('📉' if p['change'] < 0 else '➡️')
            change_emoji = '🟢' if p['change'] > 0 else ('🔴' if p['change'] < 0 else '⚪')
            
            msg += f"""{emoji} <b>{p['symbol']}</b>
   💰 ₺{p['price']:,.2f}
   {change_emoji} {p['change']:+.2f}%
   📊 Yüksek: ₺{p['high']:,.2f} | Düşük: ₺{p['low']:,.2f}

"""
            total_change += p['change']
        
        avg_change = total_change / len(prices) if prices else 0
        msg += f"\n📊 <b>Ortalama:</b> {avg_change:+.2f}%"
        msg += f"\n⭐ <b>Toplam:</b> {len(prices)} kripto"
        
        return msg
    
    def check_alerts(self, user_id: str, threshold: float = 5.0) -> List[Dict]:
        """Önemli değişimleri kontrol et"""
        prices = self.get_watchlist_prices(user_id)
        alerts = []
        
        for p in prices:
            if abs(p['change']) >= threshold:
                alerts.append({
                    'symbol': p['symbol'],
                    'price': p['price'],
                    'change': p['change'],
                    'type': 'SURGE' if p['change'] > 0 else 'DROP'
                })
        
        return alerts
    
    def send_watchlist_alert(self, user_id: str, chat_id: str) -> bool:
        """Watchlist uyarısı gönder"""
        try:
            alerts = self.check_alerts(user_id)
            
            if not alerts:
                return False
            
            msg = "🚨 <b>WATCHLIST UYARI!</b>\n\n"
            
            for a in alerts:
                emoji = '🚀' if a['type'] == 'SURGE' else '💥'
                msg += f"""{emoji} <b>{a['symbol']}</b>
   💰 ₺{a['price']:,.2f}
   📊 {a['change']:+.2f}%

"""
            
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML'},
                timeout=10
            )
            return resp.status_code == 200
        except:
            return False
