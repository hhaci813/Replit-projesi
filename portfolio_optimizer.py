"""Portfolio Optimizasyonu - Efficient Frontier"""
import numpy as np
import yfinance as yf

class PortfolioOptimizer:
    @staticmethod
    def optimize_weights(symbols, weights=None):
        """Portföy ağırlıklarını optimize et"""
        if weights is None:
            weights = np.array([1/len(symbols)] * len(symbols))
        
        try:
            # Returns hesapla
            returns_data = []
            for sym in symbols:
                data = yf.download(sym, period="1y", progress=False)
                returns = data['Close'].pct_change().dropna()
                returns_data.append(returns)
            
            returns_matrix = np.column_stack(returns_data)
            
            # Portföy metrikleri
            portfolio_return = np.sum(returns_matrix.mean() * 252 * weights)
            portfolio_std = np.sqrt(np.dot(weights, np.dot(np.cov(returns_matrix.T), weights))) * np.sqrt(252)
            
            return {
                "return": portfolio_return,
                "risk": portfolio_std,
                "weights": dict(zip(symbols, weights)),
                "sharpe": portfolio_return / portfolio_std if portfolio_std > 0 else 0
            }
        except:
            return {"error": "Optimizasyon başarısız"}
