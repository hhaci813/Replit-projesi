"""
KAR/ZARAR TAKİBİ
Gerçek işlem geçmişi ve performans analizi
"""

import json
import os
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

TRADE_HISTORY_FILE = "trade_history.json"

class TradeHistory:
    def __init__(self):
        self.history = self.load_history()
        
    def load_history(self) -> Dict:
        """İşlem geçmişini yükle"""
        try:
            if os.path.exists(TRADE_HISTORY_FILE):
                with open(TRADE_HISTORY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_history(self):
        """İşlem geçmişini kaydet"""
        try:
            with open(TRADE_HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2)
        except:
            pass
    
    def add_trade(self, user_id: str, trade_data: Dict) -> Dict:
        """İşlem ekle"""
        if user_id not in self.history:
            self.history[user_id] = {
                'trades': [],
                'stats': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'total_profit_loss': 0,
                    'best_trade': 0,
                    'worst_trade': 0
                }
            }
        
        trade = {
            'id': len(self.history[user_id]['trades']) + 1,
            'symbol': trade_data.get('symbol', ''),
            'type': trade_data.get('type', 'BUY'),
            'entry_price': trade_data.get('entry_price', 0),
            'exit_price': trade_data.get('exit_price', 0),
            'amount': trade_data.get('amount', 0),
            'profit_loss': 0,
            'profit_loss_pct': 0,
            'entry_date': trade_data.get('entry_date', datetime.now().isoformat()),
            'exit_date': trade_data.get('exit_date', None),
            'status': 'open' if not trade_data.get('exit_price') else 'closed',
            'notes': trade_data.get('notes', '')
        }
        
        if trade['exit_price'] and trade['entry_price']:
            trade['profit_loss'] = (trade['exit_price'] - trade['entry_price']) * trade['amount']
            trade['profit_loss_pct'] = ((trade['exit_price'] - trade['entry_price']) / trade['entry_price']) * 100
            trade['status'] = 'closed'
            
            self._update_stats(user_id, trade)
        
        self.history[user_id]['trades'].append(trade)
        self.save_history()
        
        return trade
    
    def _update_stats(self, user_id: str, trade: Dict):
        """İstatistikleri güncelle"""
        stats = self.history[user_id]['stats']
        stats['total_trades'] += 1
        stats['total_profit_loss'] += trade['profit_loss']
        
        if trade['profit_loss'] > 0:
            stats['winning_trades'] += 1
        else:
            stats['losing_trades'] += 1
        
        if trade['profit_loss'] > stats['best_trade']:
            stats['best_trade'] = trade['profit_loss']
        if trade['profit_loss'] < stats['worst_trade']:
            stats['worst_trade'] = trade['profit_loss']
    
    def close_trade(self, user_id: str, trade_id: int, exit_price: float) -> Optional[Dict]:
        """İşlemi kapat"""
        if user_id not in self.history:
            return None
        
        for trade in self.history[user_id]['trades']:
            if trade['id'] == trade_id and trade['status'] == 'open':
                trade['exit_price'] = exit_price
                trade['exit_date'] = datetime.now().isoformat()
                trade['profit_loss'] = (exit_price - trade['entry_price']) * trade['amount']
                trade['profit_loss_pct'] = ((exit_price - trade['entry_price']) / trade['entry_price']) * 100
                trade['status'] = 'closed'
                
                self._update_stats(user_id, trade)
                self.save_history()
                return trade
        
        return None
    
    def get_open_trades(self, user_id: str) -> List[Dict]:
        """Açık işlemleri al"""
        if user_id not in self.history:
            return []
        return [t for t in self.history[user_id]['trades'] if t['status'] == 'open']
    
    def get_statistics(self, user_id: str) -> Dict:
        """İstatistikleri al"""
        if user_id not in self.history:
            return {'total_trades': 0, 'win_rate': 0, 'total_profit_loss': 0}
        
        stats = self.history[user_id]['stats']
        closed = [t for t in self.history[user_id]['trades'] if t['status'] == 'closed']
        
        if not closed:
            return stats
        
        wins = [t['profit_loss'] for t in closed if t['profit_loss'] > 0]
        losses = [t['profit_loss'] for t in closed if t['profit_loss'] < 0]
        
        win_rate = (len(wins) / len(closed)) * 100 if closed else 0
        profit_factor = sum(wins) / abs(sum(losses)) if losses else 0
        
        return {
            **stats,
            'win_rate': round(win_rate, 1),
            'avg_profit': round(np.mean(wins), 2) if wins else 0,
            'avg_loss': round(np.mean(losses), 2) if losses else 0,
            'profit_factor': round(profit_factor, 2)
        }
    
    def generate_report(self, user_id: str) -> str:
        """Kar/zarar raporu"""
        stats = self.get_statistics(user_id)
        open_trades = self.get_open_trades(user_id)
        
        msg = "💹 <b>KAR/ZARAR RAPORU</b>\n\n"
        
        if not stats.get('total_trades'):
            msg += """Henüz işlem yok.

<b>İşlem eklemek için:</b>
/islem BTC 100000 1.5
(sembol, giriş fiyatı TL, miktar)

<b>İşlem kapatmak için:</b>
/kapat 1 105000
(işlem ID, çıkış fiyatı)"""
            return msg
        
        pnl_emoji = '📈' if stats['total_profit_loss'] >= 0 else '📉'
        msg += f"""📊 <b>İSTATİSTİKLER</b>
{pnl_emoji} Toplam K/Z: ₺{stats['total_profit_loss']:,.2f}
🎯 Kazanma Oranı: %{stats['win_rate']}
📝 Toplam İşlem: {stats['total_trades']}
✅ Kazanan: {stats['winning_trades']}
❌ Kaybeden: {stats['losing_trades']}
📊 Profit Factor: {stats.get('profit_factor', 0)}

"""
        
        if open_trades:
            msg += "<b>AÇIK POZİSYONLAR:</b>\n"
            for t in open_trades[:5]:
                msg += f"• #{t['id']} {t['symbol']}: ₺{t['entry_price']:,.2f} x {t['amount']}\n"
        
        return msg
