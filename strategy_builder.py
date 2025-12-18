"""
Kullanıcı Özel Strateji Modülü
Custom strategy builder - Kullanıcılar kendi stratejilerini oluşturabilir
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

class StrategyBuilder:
    """Özel strateji oluşturucu"""
    
    INDICATORS = {
        'RSI': {'params': ['period'], 'default': {'period': 14}},
        'MACD': {'params': ['fast', 'slow', 'signal'], 'default': {'fast': 12, 'slow': 26, 'signal': 9}},
        'SMA': {'params': ['period'], 'default': {'period': 20}},
        'EMA': {'params': ['period'], 'default': {'period': 20}},
        'BB': {'params': ['period', 'std'], 'default': {'period': 20, 'std': 2}},
        'VOLUME': {'params': ['threshold'], 'default': {'threshold': 1.5}},
        'PRICE_CHANGE': {'params': ['percent'], 'default': {'percent': 3}},
    }
    
    CONDITIONS = {
        'GREATER_THAN': '>',
        'LESS_THAN': '<',
        'EQUALS': '==',
        'CROSSES_ABOVE': 'cross_up',
        'CROSSES_BELOW': 'cross_down',
    }
    
    def __init__(self):
        self.strategies_file = Path('user_strategies.json')
        self.load_strategies()
    
    def load_strategies(self):
        if self.strategies_file.exists():
            with open(self.strategies_file, 'r') as f:
                self.strategies = json.load(f)
        else:
            self.strategies = {'strategies': [], 'active': []}
    
    def save_strategies(self):
        with open(self.strategies_file, 'w') as f:
            json.dump(self.strategies, f, indent=2, ensure_ascii=False)
    
    def create_strategy(self, name: str, description: str, 
                       buy_conditions: List[Dict], 
                       sell_conditions: List[Dict],
                       risk_params: Dict = None) -> Dict:
        """
        Yeni strateji oluştur
        
        Örnek buy_conditions:
        [
            {'indicator': 'RSI', 'condition': 'LESS_THAN', 'value': 30},
            {'indicator': 'MACD', 'condition': 'CROSSES_ABOVE', 'value': 'signal'}
        ]
        """
        strategy_id = f"strat_{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        strategy = {
            'id': strategy_id,
            'name': name,
            'description': description,
            'buy_conditions': buy_conditions,
            'sell_conditions': sell_conditions,
            'risk_params': risk_params or {
                'stop_loss_percent': 5,
                'take_profit_percent': 10,
                'max_position_percent': 10
            },
            'created_at': datetime.now().isoformat(),
            'is_active': False,
            'performance': {
                'signals_generated': 0,
                'wins': 0,
                'losses': 0,
                'total_pnl': 0
            }
        }
        
        self.strategies['strategies'].append(strategy)
        self.save_strategies()
        
        return {'success': True, 'strategy_id': strategy_id, 'message': f"✅ '{name}' stratejisi oluşturuldu!"}
    
    def activate_strategy(self, strategy_id: str) -> Dict:
        """Stratejiyi aktif et"""
        for strat in self.strategies['strategies']:
            if strat['id'] == strategy_id:
                strat['is_active'] = True
                if strategy_id not in self.strategies['active']:
                    self.strategies['active'].append(strategy_id)
                self.save_strategies()
                return {'success': True, 'message': f"✅ {strat['name']} aktif!"}
        
        return {'success': False, 'error': 'Strateji bulunamadı'}
    
    def deactivate_strategy(self, strategy_id: str) -> Dict:
        """Stratejiyi deaktif et"""
        for strat in self.strategies['strategies']:
            if strat['id'] == strategy_id:
                strat['is_active'] = False
                if strategy_id in self.strategies['active']:
                    self.strategies['active'].remove(strategy_id)
                self.save_strategies()
                return {'success': True, 'message': f"⏹️ {strat['name']} durduruldu"}
        
        return {'success': False, 'error': 'Strateji bulunamadı'}
    
    def delete_strategy(self, strategy_id: str) -> Dict:
        """Strateji sil"""
        for i, strat in enumerate(self.strategies['strategies']):
            if strat['id'] == strategy_id:
                name = strat['name']
                del self.strategies['strategies'][i]
                if strategy_id in self.strategies['active']:
                    self.strategies['active'].remove(strategy_id)
                self.save_strategies()
                return {'success': True, 'message': f"🗑️ {name} silindi"}
        
        return {'success': False, 'error': 'Strateji bulunamadı'}
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        """Strateji detayları"""
        for strat in self.strategies['strategies']:
            if strat['id'] == strategy_id:
                return strat
        return None
    
    def list_strategies(self) -> List[Dict]:
        """Tüm stratejileri listele"""
        return self.strategies['strategies']
    
    def list_active_strategies(self) -> List[Dict]:
        """Aktif stratejileri listele"""
        return [s for s in self.strategies['strategies'] if s.get('is_active')]
    
    def evaluate_conditions(self, conditions: List[Dict], indicators: Dict) -> bool:
        """Koşulları değerlendir"""
        for cond in conditions:
            indicator = cond.get('indicator')
            condition_type = cond.get('condition')
            target_value = cond.get('value')
            
            current_value = indicators.get(indicator)
            
            if current_value is None:
                continue
            
            if condition_type == 'GREATER_THAN':
                if not (current_value > target_value):
                    return False
            elif condition_type == 'LESS_THAN':
                if not (current_value < target_value):
                    return False
            elif condition_type == 'EQUALS':
                if not (abs(current_value - target_value) < 0.01):
                    return False
            elif condition_type == 'CROSSES_ABOVE':
                pass
            elif condition_type == 'CROSSES_BELOW':
                pass
        
        return True
    
    def run_strategy(self, strategy_id: str, market_data: Dict) -> Dict:
        """Stratejiyi çalıştır ve sinyal üret"""
        strategy = self.get_strategy(strategy_id)
        
        if not strategy:
            return {'signal': None, 'error': 'Strateji bulunamadı'}
        
        if not strategy.get('is_active'):
            return {'signal': None, 'reason': 'Strateji aktif değil'}
        
        indicators = market_data.get('indicators', {})
        
        buy_signal = self.evaluate_conditions(strategy['buy_conditions'], indicators)
        sell_signal = self.evaluate_conditions(strategy['sell_conditions'], indicators)
        
        signal = None
        if buy_signal:
            signal = 'BUY'
        elif sell_signal:
            signal = 'SELL'
        
        if signal:
            strategy['performance']['signals_generated'] += 1
            self.save_strategies()
        
        return {
            'strategy_id': strategy_id,
            'strategy_name': strategy['name'],
            'signal': signal,
            'risk_params': strategy['risk_params'],
            'timestamp': datetime.now().isoformat()
        }
    
    def format_strategy_list(self) -> str:
        """Strateji listesi mesajı"""
        strategies = self.list_strategies()
        
        if not strategies:
            return "📋 Henüz strateji oluşturulmadı.\n\n💡 /strateji-olustur komutuyla başlayın!"
        
        msg = "📋 <b>STRATEJİLERİNİZ</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for strat in strategies:
            status = "🟢 AKTİF" if strat.get('is_active') else "⚪ BEKLEMEDE"
            perf = strat.get('performance', {})
            win_rate = perf.get('wins', 0) / max(perf.get('signals_generated', 1), 1) * 100
            
            msg += f"<b>{strat['name']}</b> {status}\n"
            msg += f"   📊 {perf.get('signals_generated', 0)} sinyal | %{win_rate:.1f} başarı\n"
            msg += f"   💰 Toplam: %{perf.get('total_pnl', 0):.2f}\n\n"
        
        return msg


class PrebuiltStrategies:
    """Hazır strateji şablonları"""
    
    @staticmethod
    def rsi_oversold_strategy() -> Dict:
        """RSI Aşırı Satım Stratejisi"""
        return {
            'name': 'RSI Aşırı Satım',
            'description': 'RSI 30 altına düştüğünde al, 70 üstüne çıktığında sat',
            'buy_conditions': [
                {'indicator': 'RSI', 'condition': 'LESS_THAN', 'value': 30}
            ],
            'sell_conditions': [
                {'indicator': 'RSI', 'condition': 'GREATER_THAN', 'value': 70}
            ],
            'risk_params': {'stop_loss_percent': 5, 'take_profit_percent': 15}
        }
    
    @staticmethod
    def macd_crossover_strategy() -> Dict:
        """MACD Kesişim Stratejisi"""
        return {
            'name': 'MACD Kesişim',
            'description': 'MACD sinyal çizgisini yukarı kestiğinde al, aşağı kestiğinde sat',
            'buy_conditions': [
                {'indicator': 'MACD', 'condition': 'CROSSES_ABOVE', 'value': 'signal'}
            ],
            'sell_conditions': [
                {'indicator': 'MACD', 'condition': 'CROSSES_BELOW', 'value': 'signal'}
            ],
            'risk_params': {'stop_loss_percent': 7, 'take_profit_percent': 12}
        }
    
    @staticmethod
    def bollinger_bounce_strategy() -> Dict:
        """Bollinger Band Bounce Stratejisi"""
        return {
            'name': 'Bollinger Bounce',
            'description': 'Alt banda dokunduğunda al, üst banda dokunduğunda sat',
            'buy_conditions': [
                {'indicator': 'BB_POSITION', 'condition': 'LESS_THAN', 'value': 0.1}
            ],
            'sell_conditions': [
                {'indicator': 'BB_POSITION', 'condition': 'GREATER_THAN', 'value': 0.9}
            ],
            'risk_params': {'stop_loss_percent': 4, 'take_profit_percent': 8}
        }
    
    @staticmethod
    def volume_breakout_strategy() -> Dict:
        """Hacim Kırılım Stratejisi"""
        return {
            'name': 'Hacim Kırılım',
            'description': 'Hacim ortalamanın 2x üstünde ve fiyat yükseliyorsa al',
            'buy_conditions': [
                {'indicator': 'VOLUME_RATIO', 'condition': 'GREATER_THAN', 'value': 2.0},
                {'indicator': 'PRICE_CHANGE_1H', 'condition': 'GREATER_THAN', 'value': 2}
            ],
            'sell_conditions': [
                {'indicator': 'PRICE_CHANGE_1H', 'condition': 'LESS_THAN', 'value': -3}
            ],
            'risk_params': {'stop_loss_percent': 5, 'take_profit_percent': 10}
        }
    
    @staticmethod
    def triple_confirmation_strategy() -> Dict:
        """Üçlü Onay Stratejisi (Güvenli)"""
        return {
            'name': 'Üçlü Onay',
            'description': 'RSI, MACD ve Trend aynı anda onaylarsa işlem yap',
            'buy_conditions': [
                {'indicator': 'RSI', 'condition': 'LESS_THAN', 'value': 40},
                {'indicator': 'MACD', 'condition': 'CROSSES_ABOVE', 'value': 'signal'},
                {'indicator': 'TREND', 'condition': 'EQUALS', 'value': 'UP'}
            ],
            'sell_conditions': [
                {'indicator': 'RSI', 'condition': 'GREATER_THAN', 'value': 65},
                {'indicator': 'MACD', 'condition': 'CROSSES_BELOW', 'value': 'signal'}
            ],
            'risk_params': {'stop_loss_percent': 6, 'take_profit_percent': 20}
        }


def format_prebuilt_strategies() -> str:
    """Hazır stratejiler mesajı"""
    msg = "🎯 <b>HAZIR STRATEJİ ŞABLONLARI</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    strategies = [
        ('1️⃣', PrebuiltStrategies.rsi_oversold_strategy()),
        ('2️⃣', PrebuiltStrategies.macd_crossover_strategy()),
        ('3️⃣', PrebuiltStrategies.bollinger_bounce_strategy()),
        ('4️⃣', PrebuiltStrategies.volume_breakout_strategy()),
        ('5️⃣', PrebuiltStrategies.triple_confirmation_strategy()),
    ]
    
    for num, strat in strategies:
        risk = strat['risk_params']
        msg += f"{num} <b>{strat['name']}</b>\n"
        msg += f"   {strat['description']}\n"
        msg += f"   🛑 Stop: %{risk['stop_loss_percent']} | 🎯 Hedef: %{risk['take_profit_percent']}\n\n"
    
    msg += "💡 Kullanmak için: /strateji-ekle [numara]"
    
    return msg


if __name__ == "__main__":
    builder = StrategyBuilder()
    print(format_prebuilt_strategies())
