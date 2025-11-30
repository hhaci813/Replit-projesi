"""İleri Risk Metrikleri"""
import numpy as np
import yfinance as yf

class RiskMetrics:
    @staticmethod
    def sharpe_ratio(symbol, risk_free_rate=0.05, period="1y"):
        """Sharpe Ratio hesapla"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            returns = data['Close'].pct_change().dropna()
            
            excess_return = returns.mean() - (risk_free_rate / 252)
            vol = returns.std()
            sharpe = (excess_return / vol) * np.sqrt(252) if vol != 0 else 0
            return sharpe, f"Sharpe: {sharpe:.2f}"
        except:
            return 0, "Hesaplanamadı"
    
    @staticmethod
    def max_drawdown(symbol, period="1y"):
        """Max Drawdown hesapla"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            prices = data['Close']
            cummax = prices.expanding().max()
            drawdown = (prices - cummax) / cummax
            max_dd = drawdown.min()
            return max_dd, f"Max DD: {max_dd*100:.2f}%"
        except:
            return 0, "Hesaplanamadı"
    
    @staticmethod
    def volatility(symbol, period="1y"):
        """Volatilite (annualized)"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            returns = data['Close'].pct_change().dropna()
            vol = returns.std() * np.sqrt(252)
            return vol, f"Volatilite: {vol*100:.2f}%"
        except:
            return 0, "Hesaplanamadı"
    
    @staticmethod
    def sortino_ratio(symbol, target_return=0, period="1y"):
        """Sortino Ratio"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            returns = data['Close'].pct_change().dropna()
            
            excess = returns - target_return
            downside = excess[excess < 0].std()
            sortino = (returns.mean() - target_return) / downside if downside != 0 else 0
            return sortino * np.sqrt(252), f"Sortino: {sortino*np.sqrt(252):.2f}"
        except:
            return 0, "Hesaplanamadı"
