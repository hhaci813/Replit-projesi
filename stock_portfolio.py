"""
HİSSE PORTFÖY SİMÜLATÖRÜ
Sanal alış-satış, işlem geçmişi, performans takibi
Risk yönetimi entegrasyonu
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

class StockPortfolio:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.data_dir = '/home/runner/workspace/portfolio_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.portfolio_file = f'{self.data_dir}/stock_portfolio_{user_id}.json'
        self.history_file = f'{self.data_dir}/stock_history_{user_id}.json'
        
        self.portfolio = self._load_portfolio()
        self.history = self._load_history()
        
        # Başlangıç sermayesi (sanal)
        self.initial_capital = 100000  # 100.000 TL
        if 'cash' not in self.portfolio:
            self.portfolio['cash'] = self.initial_capital
            self.portfolio['positions'] = {}
            self._save_portfolio()
    
    def _load_portfolio(self) -> Dict:
        """Portföyü yükle"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'cash': 100000, 'positions': {}}
    
    def _save_portfolio(self):
        """Portföyü kaydet"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
        except Exception as e:
            logger.error(f"Portföy kaydetme hatası: {e}")
    
    def _load_history(self) -> List:
        """İşlem geçmişini yükle"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_history(self):
        """İşlem geçmişini kaydet"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Geçmiş kaydetme hatası: {e}")
    
    def get_stock_price(self, symbol: str) -> float:
        """Güncel hisse fiyatını al"""
        try:
            ticker = f"{symbol}.IS"
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if len(hist) > 0:
                return float(hist['Close'].iloc[-1])
        except Exception as e:
            logger.error(f"Fiyat alma hatası ({symbol}): {e}")
        return 0
    
    def buy_stock(self, symbol: str, amount_tl: float, stop_loss: float = None, take_profit: float = None) -> Dict:
        """Hisse al (TL bazlı)"""
        symbol = symbol.upper()
        price = self.get_stock_price(symbol)
        
        if price <= 0:
            return {'success': False, 'error': 'Fiyat alınamadı'}
        
        if amount_tl > self.portfolio['cash']:
            return {'success': False, 'error': f'Yetersiz bakiye. Mevcut: ₺{self.portfolio["cash"]:,.2f}'}
        
        # Lot hesapla
        shares = amount_tl / price
        total_cost = shares * price
        
        # Portföye ekle
        if symbol not in self.portfolio['positions']:
            self.portfolio['positions'][symbol] = {
                'shares': 0,
                'avg_price': 0,
                'total_cost': 0,
                'stop_loss': None,
                'take_profit': None
            }
        
        pos = self.portfolio['positions'][symbol]
        new_total_shares = pos['shares'] + shares
        new_total_cost = pos['total_cost'] + total_cost
        pos['avg_price'] = new_total_cost / new_total_shares if new_total_shares > 0 else 0
        pos['shares'] = new_total_shares
        pos['total_cost'] = new_total_cost
        
        if stop_loss:
            pos['stop_loss'] = stop_loss
        if take_profit:
            pos['take_profit'] = take_profit
        
        # Nakit düş
        self.portfolio['cash'] -= total_cost
        
        # Geçmişe ekle
        self.history.append({
            'type': 'BUY',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': total_cost,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_portfolio()
        self._save_history()
        
        return {
            'success': True,
            'symbol': symbol,
            'shares': round(shares, 4),
            'price': price,
            'total': round(total_cost, 2),
            'remaining_cash': round(self.portfolio['cash'], 2)
        }
    
    def sell_stock(self, symbol: str, shares: float = None, percent: float = None) -> Dict:
        """Hisse sat"""
        symbol = symbol.upper()
        
        if symbol not in self.portfolio['positions']:
            return {'success': False, 'error': 'Pozisyon bulunamadı'}
        
        pos = self.portfolio['positions'][symbol]
        
        if pos['shares'] <= 0:
            return {'success': False, 'error': 'Satılacak hisse yok'}
        
        # Satılacak miktar
        if percent:
            shares = pos['shares'] * (percent / 100)
        elif shares is None:
            shares = pos['shares']  # Tamamını sat
        
        if shares > pos['shares']:
            shares = pos['shares']
        
        price = self.get_stock_price(symbol)
        if price <= 0:
            return {'success': False, 'error': 'Fiyat alınamadı'}
        
        total_value = shares * price
        
        # Kar/Zarar hesapla
        avg_cost = pos['avg_price'] * shares
        pnl = total_value - avg_cost
        pnl_percent = (pnl / avg_cost * 100) if avg_cost > 0 else 0
        
        # Pozisyonu güncelle
        pos['shares'] -= shares
        pos['total_cost'] = pos['shares'] * pos['avg_price']
        
        if pos['shares'] <= 0:
            del self.portfolio['positions'][symbol]
        
        # Nakit ekle
        self.portfolio['cash'] += total_value
        
        # Geçmişe ekle
        self.history.append({
            'type': 'SELL',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': total_value,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_portfolio()
        self._save_history()
        
        return {
            'success': True,
            'symbol': symbol,
            'shares': round(shares, 4),
            'price': price,
            'total': round(total_value, 2),
            'pnl': round(pnl, 2),
            'pnl_percent': round(pnl_percent, 2),
            'cash': round(self.portfolio['cash'], 2)
        }
    
    def get_portfolio_value(self) -> Dict:
        """Portföy değerini hesapla"""
        total_stock_value = 0
        positions_detail = []
        
        for symbol, pos in self.portfolio.get('positions', {}).items():
            if pos['shares'] > 0:
                current_price = self.get_stock_price(symbol)
                current_value = pos['shares'] * current_price
                cost = pos['total_cost']
                pnl = current_value - cost
                pnl_percent = (pnl / cost * 100) if cost > 0 else 0
                
                total_stock_value += current_value
                
                positions_detail.append({
                    'symbol': symbol,
                    'shares': round(pos['shares'], 4),
                    'avg_price': round(pos['avg_price'], 4),
                    'current_price': round(current_price, 4),
                    'current_value': round(current_value, 2),
                    'cost': round(cost, 2),
                    'pnl': round(pnl, 2),
                    'pnl_percent': round(pnl_percent, 2),
                    'stop_loss': pos.get('stop_loss'),
                    'take_profit': pos.get('take_profit')
                })
        
        cash = self.portfolio.get('cash', 0)
        total_value = cash + total_stock_value
        total_pnl = total_value - self.initial_capital
        total_pnl_percent = (total_pnl / self.initial_capital * 100)
        
        return {
            'cash': round(cash, 2),
            'stock_value': round(total_stock_value, 2),
            'total_value': round(total_value, 2),
            'initial_capital': self.initial_capital,
            'total_pnl': round(total_pnl, 2),
            'total_pnl_percent': round(total_pnl_percent, 2),
            'positions': positions_detail,
            'position_count': len(positions_detail)
        }
    
    def check_stop_loss_take_profit(self) -> List[Dict]:
        """Stop-loss ve take-profit kontrolü"""
        alerts = []
        
        for symbol, pos in self.portfolio.get('positions', {}).items():
            if pos['shares'] <= 0:
                continue
            
            current_price = self.get_stock_price(symbol)
            if current_price <= 0:
                continue
            
            # Stop-loss kontrolü
            if pos.get('stop_loss') and current_price <= pos['stop_loss']:
                alerts.append({
                    'type': 'STOP_LOSS',
                    'symbol': symbol,
                    'trigger_price': pos['stop_loss'],
                    'current_price': current_price,
                    'action': 'SAT'
                })
            
            # Take-profit kontrolü
            if pos.get('take_profit') and current_price >= pos['take_profit']:
                alerts.append({
                    'type': 'TAKE_PROFIT',
                    'symbol': symbol,
                    'trigger_price': pos['take_profit'],
                    'current_price': current_price,
                    'action': 'SAT'
                })
        
        return alerts
    
    def get_trade_history(self, limit: int = 20) -> List[Dict]:
        """Son işlem geçmişi"""
        return self.history[-limit:][::-1]
    
    def reset_portfolio(self):
        """Portföyü sıfırla"""
        self.portfolio = {'cash': self.initial_capital, 'positions': {}}
        self.history = []
        self._save_portfolio()
        self._save_history()
        return {'success': True, 'message': 'Portföy sıfırlandı'}
    
    def generate_report(self) -> str:
        """Telegram için portföy raporu"""
        data = self.get_portfolio_value()
        
        pnl_emoji = "🟢" if data['total_pnl'] >= 0 else "🔴"
        
        report = f"""💼 <b>HİSSE PORTFÖYÜ</b>
━━━━━━━━━━━━━━━━━━━━━

💰 <b>Nakit:</b> ₺{data['cash']:,.2f}
📊 <b>Hisse Değeri:</b> ₺{data['stock_value']:,.2f}
💎 <b>Toplam:</b> ₺{data['total_value']:,.2f}

{pnl_emoji} <b>Kar/Zarar:</b> ₺{data['total_pnl']:+,.2f} ({data['total_pnl_percent']:+.2f}%)

"""
        
        if data['positions']:
            report += "<b>POZİSYONLAR:</b>\n\n"
            for pos in data['positions']:
                pos_emoji = "🟢" if pos['pnl'] >= 0 else "🔴"
                report += f"{pos_emoji} <b>{pos['symbol']}</b>\n"
                report += f"   📊 {pos['shares']:.2f} lot @ ₺{pos['current_price']:.4f}\n"
                report += f"   💰 Değer: ₺{pos['current_value']:,.2f} ({pos['pnl_percent']:+.2f}%)\n"
                if pos['stop_loss']:
                    report += f"   🛑 SL: ₺{pos['stop_loss']:.4f}\n"
                if pos['take_profit']:
                    report += f"   🎯 TP: ₺{pos['take_profit']:.4f}\n"
                report += "\n"
        else:
            report += "📭 Henüz pozisyon yok\n"
        
        report += "━━━━━━━━━━━━━━━━━━━━━\n🤖 <i>Hisse Portföy Simülatörü</i>"
        
        return report
