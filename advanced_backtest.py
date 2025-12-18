"""
Gelişmiş Backtest Modülü
Sharpe Ratio, Sortino Ratio, Max Drawdown, Profit Factor hesaplama
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class AdvancedBacktester:
    """Gelişmiş backtest engine"""
    
    def __init__(self):
        self.results_file = Path('backtest_results.json')
        self.risk_free_rate = 0.05
    
    def calculate_returns(self, prices: List[float]) -> np.ndarray:
        """Getiri hesapla"""
        prices = np.array(prices)
        returns = np.diff(prices) / prices[:-1]
        return returns
    
    def calculate_sharpe_ratio(self, returns: np.ndarray, 
                               risk_free_rate: float = None,
                               periods_per_year: int = 365) -> float:
        """
        Sharpe Ratio hesapla
        (Ortalama getiri - Risk-free oran) / Standart sapma
        """
        if len(returns) < 2:
            return 0.0
        
        rf = risk_free_rate or self.risk_free_rate
        rf_daily = rf / periods_per_year
        
        excess_returns = returns - rf_daily
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns)
        annualized_sharpe = sharpe * np.sqrt(periods_per_year)
        
        return round(annualized_sharpe, 3)
    
    def calculate_sortino_ratio(self, returns: np.ndarray,
                                risk_free_rate: float = None,
                                periods_per_year: int = 365) -> float:
        """
        Sortino Ratio hesapla
        Sadece negatif volatiliteyi dikkate alır
        """
        if len(returns) < 2:
            return 0.0
        
        rf = risk_free_rate or self.risk_free_rate
        rf_daily = rf / periods_per_year
        
        excess_returns = returns - rf_daily
        negative_returns = returns[returns < 0]
        
        if len(negative_returns) == 0:
            return 10.0
        
        downside_std = np.std(negative_returns)
        
        if downside_std == 0:
            return 10.0
        
        sortino = np.mean(excess_returns) / downside_std
        annualized_sortino = sortino * np.sqrt(periods_per_year)
        
        return round(annualized_sortino, 3)
    
    def calculate_max_drawdown(self, prices: List[float]) -> Dict:
        """
        Maximum Drawdown hesapla
        En büyük tepe-dip düşüşü
        """
        prices = np.array(prices)
        
        peak = np.maximum.accumulate(prices)
        drawdown = (peak - prices) / peak
        max_dd = np.max(drawdown)
        
        max_dd_idx = np.argmax(drawdown)
        peak_idx = np.argmax(prices[:max_dd_idx + 1]) if max_dd_idx > 0 else 0
        
        return {
            'max_drawdown_percent': round(max_dd * 100, 2),
            'peak_value': prices[peak_idx] if len(prices) > peak_idx else 0,
            'trough_value': prices[max_dd_idx] if len(prices) > max_dd_idx else 0,
            'recovery_needed_percent': round((1 / (1 - max_dd) - 1) * 100, 2) if max_dd < 1 else 100
        }
    
    def calculate_profit_factor(self, trades: List[Dict]) -> float:
        """
        Profit Factor hesapla
        Gross Profit / Gross Loss
        """
        gross_profit = sum(t['pnl'] for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t['pnl'] for t in trades if t.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return 10.0 if gross_profit > 0 else 0.0
        
        return round(gross_profit / gross_loss, 2)
    
    def calculate_calmar_ratio(self, returns: np.ndarray, 
                               prices: List[float],
                               periods_per_year: int = 365) -> float:
        """
        Calmar Ratio hesapla
        Yıllık getiri / Max Drawdown
        """
        if len(returns) < 2:
            return 0.0
        
        annual_return = np.mean(returns) * periods_per_year
        max_dd = self.calculate_max_drawdown(prices)['max_drawdown_percent'] / 100
        
        if max_dd == 0:
            return 10.0
        
        return round(annual_return / max_dd, 3)
    
    def calculate_win_metrics(self, trades: List[Dict]) -> Dict:
        """Kazanma metrikleri"""
        if not trades:
            return {'win_rate': 0, 'avg_win': 0, 'avg_loss': 0, 'expectancy': 0}
        
        wins = [t for t in trades if t.get('pnl', 0) > 0]
        losses = [t for t in trades if t.get('pnl', 0) < 0]
        
        win_rate = len(wins) / len(trades) * 100
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losses])) if losses else 0
        
        expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * avg_loss)
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': round(win_rate, 2),
            'avg_win_percent': round(avg_win, 2),
            'avg_loss_percent': round(avg_loss, 2),
            'best_trade': round(max(t['pnl'] for t in trades), 2) if trades else 0,
            'worst_trade': round(min(t['pnl'] for t in trades), 2) if trades else 0,
            'expectancy': round(expectancy, 2)
        }
    
    def run_backtest(self, symbol: str, strategy_name: str,
                    prices: List[float], trades: List[Dict],
                    initial_capital: float = 10000) -> Dict:
        """Tam backtest raporu"""
        
        if not prices or len(prices) < 2:
            return {'error': 'Yetersiz veri'}
        
        returns = self.calculate_returns(prices)
        
        equity_curve = [initial_capital]
        for trade in trades:
            pnl_percent = trade.get('pnl', 0) / 100
            equity_curve.append(equity_curve[-1] * (1 + pnl_percent))
        
        result = {
            'symbol': symbol,
            'strategy': strategy_name,
            'period': {
                'start': datetime.now() - timedelta(days=len(prices)),
                'end': datetime.now(),
                'days': len(prices)
            },
            'capital': {
                'initial': initial_capital,
                'final': equity_curve[-1] if equity_curve else initial_capital,
                'total_return_percent': round((equity_curve[-1] / initial_capital - 1) * 100, 2) if equity_curve else 0
            },
            'ratios': {
                'sharpe_ratio': self.calculate_sharpe_ratio(returns),
                'sortino_ratio': self.calculate_sortino_ratio(returns),
                'calmar_ratio': self.calculate_calmar_ratio(returns, prices),
                'profit_factor': self.calculate_profit_factor(trades)
            },
            'risk': self.calculate_max_drawdown(equity_curve if len(equity_curve) > 1 else prices),
            'trades': self.calculate_win_metrics(trades),
            'timestamp': datetime.now().isoformat()
        }
        
        self.save_result(result)
        
        return result
    
    def save_result(self, result: Dict):
        """Sonucu kaydet"""
        try:
            if self.results_file.exists():
                with open(self.results_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {'results': []}
            
            result_serializable = result.copy()
            result_serializable['period'] = {
                'start': str(result['period']['start']),
                'end': str(result['period']['end']),
                'days': result['period']['days']
            }
            
            data['results'].append(result_serializable)
            data['results'] = data['results'][-50:]
            
            with open(self.results_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Backtest kaydetme hatası: {e}")
    
    def format_report(self, result: Dict) -> str:
        """Backtest raporu formatla"""
        
        if 'error' in result:
            return f"❌ {result['error']}"
        
        msg = f"📊 <b>BACKTEST RAPORU - {result['symbol']}</b>\n"
        msg += f"📋 Strateji: {result['strategy']}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        capital = result['capital']
        msg += "💰 <b>SERMAYE</b>\n"
        msg += f"   Başlangıç: ₺{capital['initial']:,.2f}\n"
        msg += f"   Bitiş: ₺{capital['final']:,.2f}\n"
        
        pnl_emoji = "🟢" if capital['total_return_percent'] > 0 else "🔴"
        msg += f"   Toplam: {pnl_emoji} %{capital['total_return_percent']:.2f}\n\n"
        
        ratios = result['ratios']
        msg += "📈 <b>PERFORMANS ORANLARI</b>\n"
        
        sharpe_color = "🟢" if ratios['sharpe_ratio'] > 1 else ("🟡" if ratios['sharpe_ratio'] > 0 else "🔴")
        msg += f"   {sharpe_color} Sharpe Ratio: {ratios['sharpe_ratio']}\n"
        
        sortino_color = "🟢" if ratios['sortino_ratio'] > 1.5 else ("🟡" if ratios['sortino_ratio'] > 0 else "🔴")
        msg += f"   {sortino_color} Sortino Ratio: {ratios['sortino_ratio']}\n"
        
        calmar_color = "🟢" if ratios['calmar_ratio'] > 1 else "🟡"
        msg += f"   {calmar_color} Calmar Ratio: {ratios['calmar_ratio']}\n"
        
        pf_color = "🟢" if ratios['profit_factor'] > 1.5 else ("🟡" if ratios['profit_factor'] > 1 else "🔴")
        msg += f"   {pf_color} Profit Factor: {ratios['profit_factor']}\n\n"
        
        risk = result['risk']
        msg += "⚠️ <b>RİSK METRİKLERİ</b>\n"
        dd_color = "🟢" if risk['max_drawdown_percent'] < 15 else ("🟡" if risk['max_drawdown_percent'] < 30 else "🔴")
        msg += f"   {dd_color} Max Drawdown: %{risk['max_drawdown_percent']}\n"
        msg += f"   🔄 Toparlanma İçin: %{risk['recovery_needed_percent']}\n\n"
        
        trades = result['trades']
        msg += "🎯 <b>İŞLEM İSTATİSTİKLERİ</b>\n"
        msg += f"   Toplam: {trades['total_trades']} işlem\n"
        msg += f"   ✅ Kazanan: {trades['winning_trades']}\n"
        msg += f"   ❌ Kaybeden: {trades['losing_trades']}\n"
        
        wr_color = "🟢" if trades['win_rate'] > 55 else ("🟡" if trades['win_rate'] > 45 else "🔴")
        msg += f"   {wr_color} Başarı Oranı: %{trades['win_rate']}\n"
        msg += f"   📊 Beklenti: %{trades['expectancy']}\n\n"
        
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
        
        score = 0
        if ratios['sharpe_ratio'] > 1: score += 2
        elif ratios['sharpe_ratio'] > 0: score += 1
        if ratios['profit_factor'] > 1.5: score += 2
        elif ratios['profit_factor'] > 1: score += 1
        if trades['win_rate'] > 55: score += 2
        elif trades['win_rate'] > 45: score += 1
        if risk['max_drawdown_percent'] < 15: score += 2
        elif risk['max_drawdown_percent'] < 30: score += 1
        
        if score >= 7:
            verdict = "🏆 MÜKEMMEL STRATEJİ"
        elif score >= 5:
            verdict = "✅ İYİ STRATEJİ"
        elif score >= 3:
            verdict = "⚠️ GELİŞTİRİLMELİ"
        else:
            verdict = "❌ RİSKLİ STRATEJİ"
        
        msg += f"<b>DEĞERLENDİRME:</b> {verdict}"
        
        return msg


def explain_metrics() -> str:
    """Metrikleri açıkla"""
    msg = "📚 <b>BACKTEST METRİKLERİ KILAVUZU</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += "📈 <b>SHARPE RATIO</b>\n"
    msg += "   Risk-ayarlı getiri ölçüsü\n"
    msg += "   🟢 >1 = İyi | 🟡 0-1 = Orta | 🔴 <0 = Kötü\n\n"
    
    msg += "📊 <b>SORTINO RATIO</b>\n"
    msg += "   Sadece düşüş riskini dikkate alır\n"
    msg += "   🟢 >1.5 = İyi | 🟡 0-1.5 = Orta\n\n"
    
    msg += "📉 <b>MAX DRAWDOWN</b>\n"
    msg += "   En büyük tepe-dip düşüşü\n"
    msg += "   🟢 <%15 | 🟡 %15-30 | 🔴 >%30\n\n"
    
    msg += "💰 <b>PROFIT FACTOR</b>\n"
    msg += "   Brüt Kar / Brüt Zarar\n"
    msg += "   🟢 >1.5 = İyi | 🟡 1-1.5 = Orta | 🔴 <1 = Zarar\n\n"
    
    msg += "🎯 <b>CALMAR RATIO</b>\n"
    msg += "   Yıllık Getiri / Max Drawdown\n"
    msg += "   🟢 >1 = İyi | 🟡 <1 = Riskli\n"
    
    return msg


if __name__ == "__main__":
    print(explain_metrics())
