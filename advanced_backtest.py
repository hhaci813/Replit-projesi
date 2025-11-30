"""Advanced Backtesting"""
import yfinance as yf
import numpy as np

class AdvancedBacktest:
    def __init__(self):
        self.trades = []
        self.equity = 10000
    
    def backtest_rsi_strategy(self, symbol, period="1y", rsi_low=30, rsi_high=70):
        """RSI strateji backtest"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            
            # RSI hesapla
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            trades = []
            equity = 10000
            shares = 0
            
            for i in range(15, len(data)-1):
                price = data['Close'].iloc[i]
                
                # AL sinyali
                if rsi.iloc[i] < rsi_low and shares == 0:
                    shares = equity / price
                    trades.append(("AL", price, i))
                    equity = 0
                
                # SAT sinyali
                elif rsi.iloc[i] > rsi_high and shares > 0:
                    equity = shares * price
                    trades.append(("SAT", price, i))
                    shares = 0
            
            final_equity = equity if equity > 0 else shares * data['Close'].iloc[-1]
            profit = final_equity - 10000
            return_pct = (profit / 10000) * 100
            
            return {
                "initial": 10000,
                "final": final_equity,
                "profit": profit,
                "return_pct": return_pct,
                "trades": len(trades),
                "status": f"Kar: ${profit:.2f} ({return_pct:.2f}%)"
            }
        except Exception as e:
            return {"status": f"Hata: {str(e)[:30]}"}
