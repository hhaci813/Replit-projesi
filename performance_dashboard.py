"""Performance Dashboard - Analytics & Metrics"""
import json
from datetime import datetime, timedelta

class PerformanceDashboard:
    """Performance metrics ve analytics"""
    
    def __init__(self):
        self.trades = []
        self.daily_returns = {}
    
    def calculate_metrics(self, trades, starting_capital):
        """Tüm metrikleri hesapla"""
        
        if not trades:
            return self._empty_metrics()
        
        # Bazı hesaplamalar
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get('profit', 0) > 0)
        losing_trades = total_trades - winning_trades
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(t.get('profit', 0) for t in trades)
        roi = (total_profit / starting_capital * 100) if starting_capital > 0 else 0
        
        monthly_returns = self._calculate_monthly_returns(trades)
        
        sharpe_ratio = self._calculate_sharpe_ratio(monthly_returns)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate_pct': win_rate,
            'total_profit': total_profit,
            'roi_pct': roi,
            'monthly_returns': monthly_returns,
            'sharpe_ratio': sharpe_ratio,
            'timestamp': datetime.now()
        }
    
    def _calculate_monthly_returns(self, trades):
        """Aylık getirileri hesapla"""
        monthly = {}
        
        for trade in trades:
            month = trade.get('timestamp', datetime.now()).strftime('%Y-%m')
            if month not in monthly:
                monthly[month] = 0
            monthly[month] += trade.get('profit', 0)
        
        return monthly
    
    def _calculate_sharpe_ratio(self, returns):
        """Sharpe ratio hesapla"""
        if not returns:
            return 0
        
        values = list(returns.values())
        mean_return = sum(values) / len(values) if values else 0
        
        if len(values) < 2:
            return 0
        
        variance = sum((x - mean_return) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        risk_free_rate = 0.02  # 2% yıllık
        
        if std_dev == 0:
            return 0
        
        sharpe = (mean_return - risk_free_rate) / std_dev
        return sharpe
    
    def _empty_metrics(self):
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate_pct': 0,
            'total_profit': 0,
            'roi_pct': 0,
            'monthly_returns': {},
            'sharpe_ratio': 0
        }
    
    def get_dashboard_html(self, metrics):
        """Dashboard HTML oluştur"""
        return f"""
<div style="background: #1a1a1a; color: #fff; padding: 20px; border-radius: 10px;">
    <h2>📊 Performance Dashboard</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 20px 0;">
        <div style="background: #2a2a2a; padding: 15px; border-radius: 8px; border-left: 3px solid #00ff00;">
            <h4>📈 Total Trades</h4>
            <p style="font-size: 24px; color: #00ff00;">{metrics['total_trades']}</p>
        </div>
        
        <div style="background: #2a2a2a; padding: 15px; border-radius: 8px; border-left: 3px solid #00ff00;">
            <h4>✅ Win Rate</h4>
            <p style="font-size: 24px; color: #00ff00;">{metrics['win_rate_pct']:.1f}%</p>
        </div>
        
        <div style="background: #2a2a2a; padding: 15px; border-radius: 8px; border-left: 3px solid #00ff00;">
            <h4>💰 Total ROI</h4>
            <p style="font-size: 24px; color: #00ff00;">{metrics['roi_pct']:+.2f}%</p>
        </div>
        
        <div style="background: #2a2a2a; padding: 15px; border-radius: 8px; border-left: 3px solid #ffaa00;">
            <h4>📊 Sharpe Ratio</h4>
            <p style="font-size: 24px; color: #ffaa00;">{metrics['sharpe_ratio']:.2f}</p>
        </div>
        
        <div style="background: #2a2a2a; padding: 15px; border-radius: 8px; border-left: 3px solid #00aa00;">
            <h4>🟢 Winning Trades</h4>
            <p style="font-size: 24px; color: #00aa00;">{metrics['winning_trades']}</p>
        </div>
        
        <div style="background: #2a2a2a; padding: 15px; border-radius: 8px; border-left: 3px solid #ff0000;">
            <h4>🔴 Losing Trades</h4>
            <p style="font-size: 24px; color: #ff0000;">{metrics['losing_trades']}</p>
        </div>
    </div>
    
    <h3>📅 Monthly Returns</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr style="border-bottom: 1px solid #444;">
            <th style="padding: 10px; text-align: left;">Month</th>
            <th style="padding: 10px; text-align: right;">Return</th>
        </tr>
"""
        
        for month, ret in sorted(metrics['monthly_returns'].items()):
            color = "#00ff00" if ret > 0 else "#ff0000"
            return_html = f"""
        <tr style="border-bottom: 1px solid #333;">
            <td style="padding: 10px;">{month}</td>
            <td style="padding: 10px; text-align: right; color: {color};">${ret:+.2f}</td>
        </tr>
"""
        
        return_html += """
    </table>
</div>
"""
        return return_html
