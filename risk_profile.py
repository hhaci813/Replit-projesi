"""
KİŞİSEL RİSK PROFİLİ
Kullanıcıya özel öneriler ve risk yönetimi
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional

RISK_PROFILE_FILE = "risk_profiles.json"

class RiskProfile:
    def __init__(self):
        self.profiles = self.load_profiles()
        
        self.risk_levels = {
            'conservative': {
                'name': 'Muhafazakar',
                'emoji': '🛡️',
                'max_risk_per_trade': 1,
                'max_portfolio_risk': 5,
                'preferred_cryptos': ['BTC', 'ETH'],
                'avoid_volatility': True,
                'stop_loss': 3,
                'take_profit': 5
            },
            'moderate': {
                'name': 'Dengeli',
                'emoji': '⚖️',
                'max_risk_per_trade': 3,
                'max_portfolio_risk': 15,
                'preferred_cryptos': ['BTC', 'ETH', 'SOL', 'AVAX', 'LINK'],
                'avoid_volatility': False,
                'stop_loss': 5,
                'take_profit': 15
            },
            'aggressive': {
                'name': 'Agresif',
                'emoji': '🔥',
                'max_risk_per_trade': 5,
                'max_portfolio_risk': 30,
                'preferred_cryptos': [],
                'avoid_volatility': False,
                'stop_loss': 8,
                'take_profit': 30
            }
        }
    
    def load_profiles(self) -> Dict:
        """Profilleri yükle"""
        try:
            if os.path.exists(RISK_PROFILE_FILE):
                with open(RISK_PROFILE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_profiles(self):
        """Profilleri kaydet"""
        try:
            with open(RISK_PROFILE_FILE, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except:
            pass
    
    def set_profile(self, user_id: str, risk_level: str, capital: float = 10000) -> bool:
        """Kullanıcı profili ayarla"""
        if risk_level not in self.risk_levels:
            return False
        
        self.profiles[user_id] = {
            'risk_level': risk_level,
            'capital': capital,
            'created_at': datetime.now().isoformat(),
            'trades': [],
            'total_profit_loss': 0
        }
        self.save_profiles()
        return True
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Kullanıcı profilini al"""
        if user_id in self.profiles:
            profile = self.profiles[user_id]
            risk_settings = self.risk_levels.get(profile['risk_level'], self.risk_levels['moderate'])
            return {**profile, **risk_settings}
        return None
    
    def calculate_position_size(self, user_id: str, price: float) -> Dict:
        """Pozisyon büyüklüğü hesapla"""
        profile = self.get_profile(user_id)
        if not profile:
            profile = self.risk_levels['moderate']
            profile['capital'] = 10000
        
        capital = profile.get('capital', 10000)
        max_risk = profile.get('max_risk_per_trade', 3)
        stop_loss_pct = profile.get('stop_loss', 5)
        
        risk_amount = capital * (max_risk / 100)
        
        position_size = risk_amount / (stop_loss_pct / 100)
        
        position_size = min(position_size, capital * 0.25)
        
        quantity = position_size / price if price > 0 else 0
        
        return {
            'capital': capital,
            'risk_amount': risk_amount,
            'position_size': round(position_size, 2),
            'quantity': quantity,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': profile.get('take_profit', 15)
        }
    
    def get_personalized_recommendations(self, user_id: str) -> List[Dict]:
        """Kişiselleştirilmiş öneriler al"""
        profile = self.get_profile(user_id)
        if not profile:
            profile = self.risk_levels['moderate']
        
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            tickers = resp.json().get('data', [])
            
            recommendations = []
            preferred = profile.get('preferred_cryptos', [])
            avoid_volatility = profile.get('avoid_volatility', False)
            
            for t in tickers:
                pair = t.get('pairNormalized', '')
                if '_TRY' not in pair:
                    continue
                
                symbol = pair.split('_')[0]
                price = float(t.get('last', 0))
                change = float(t.get('dailyPercent', 0))
                volume = float(t.get('volume', 0))
                
                if preferred and symbol not in preferred:
                    continue
                
                if avoid_volatility and abs(change) > 10:
                    continue
                
                score = 50
                
                if -5 < change < 0:
                    score += 20
                elif 0 < change < 5:
                    score += 10
                
                if volume > 1000000:
                    score += 15
                
                if symbol in ['BTC', 'ETH']:
                    score += 10
                
                if score >= 60:
                    pos = self.calculate_position_size(user_id, price)
                    recommendations.append({
                        'symbol': symbol,
                        'price': price,
                        'change': change,
                        'score': score,
                        'position_size': pos['position_size'],
                        'stop_loss': price * (1 - pos['stop_loss_pct'] / 100),
                        'take_profit': price * (1 + pos['take_profit_pct'] / 100)
                    })
            
            return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:5]
        except:
            return []
    
    def generate_report(self, user_id: str) -> str:
        """Risk profili raporu"""
        profile = self.get_profile(user_id)
        
        if not profile:
            return """👤 <b>RİSK PROFİLİ</b>

Henüz profil oluşturulmamış.

<b>Profil oluşturmak için:</b>
/risk muhafazakar
/risk dengeli
/risk agresif

<b>Sermaye ayarlamak için:</b>
/sermaye 50000"""
        
        recommendations = self.get_personalized_recommendations(user_id)
        
        msg = f"""👤 <b>RİSK PROFİLİ</b>

{profile['emoji']} <b>Seviye:</b> {profile['name']}
💰 <b>Sermaye:</b> ₺{profile.get('capital', 10000):,.0f}
📊 <b>İşlem Başı Risk:</b> %{profile.get('max_risk_per_trade', 3)}
🛑 <b>Stop Loss:</b> %{profile.get('stop_loss', 5)}
🎯 <b>Take Profit:</b> %{profile.get('take_profit', 15)}

"""
        
        if recommendations:
            msg += "<b>Size Özel Öneriler:</b>\n\n"
            for r in recommendations[:3]:
                msg += f"""🎯 <b>{r['symbol']}</b>
   💰 Fiyat: ₺{r['price']:,.2f}
   📊 Pozisyon: ₺{r['position_size']:,.0f}
   🛑 Stop: ₺{r['stop_loss']:,.2f}
   🎯 Hedef: ₺{r['take_profit']:,.2f}

"""
        
        return msg
    
    def record_trade(self, user_id: str, symbol: str, entry: float, exit_price: float, size: float) -> Dict:
        """İşlem kaydet"""
        if user_id not in self.profiles:
            return None
        
        profit_loss = (exit_price - entry) * size / entry * 100
        profit_loss_tl = (exit_price - entry) * (size / entry)
        
        trade = {
            'symbol': symbol,
            'entry': entry,
            'exit': exit_price,
            'size': size,
            'profit_loss_pct': round(profit_loss, 2),
            'profit_loss_tl': round(profit_loss_tl, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        self.profiles[user_id]['trades'].append(trade)
        self.profiles[user_id]['total_profit_loss'] += profit_loss_tl
        self.profiles[user_id]['capital'] += profit_loss_tl
        self.save_profiles()
        
        return trade
