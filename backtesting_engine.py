"""Backtesting Engine - Tarihçe analizi & Win Rate"""
from datetime import datetime, timedelta
from price_fetcher import PriceFetcher

class BacktestingEngine:
    """Gerçek backtesting - tarihçe verisi ile test et"""
    
    def __init__(self):
        self.results = {}
    
    def backtest_strategy(self, symbol, initial_capital=10000, days=30):
        """Stratejiyi test et - geçmiş 30 günü simüle et"""
        
        # Simüle edilmiş tarihçe (gerçek: API'den çekilmeli)
        prices = self._get_historical_prices(symbol, days)
        
        if not prices:
            return None
        
        cash = initial_capital
        shares = 0
        trades = []
        portfolio_values = [initial_capital]
        
        # Simple RSI strategy - oversold al, overbought sat
        for i, (date, price) in enumerate(prices):
            if i < 14:  # RSI için min 14 veri
                continue
            
            # Basit RSI hesapla
            rsi = self._calculate_rsi(prices[:i+1], 14)
            
            # AL sinyali (RSI < 30)
            if rsi < 30 and shares == 0 and cash >= price:
                buy_shares = int(cash * 0.8 / price)
                if buy_shares > 0:
                    cash -= buy_shares * price
                    shares = buy_shares
                    trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': price,
                        'shares': buy_shares
                    })
            
            # SAT sinyali (RSI > 70)
            elif rsi > 70 and shares > 0:
                cash += shares * price
                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': price,
                    'shares': shares
                })
                shares = 0
            
            # Portfolio value
            portfolio_val = cash + (shares * price)
            portfolio_values.append(portfolio_val)
        
        # Final kapanış
        final_value = cash + (shares * price) if shares > 0 else cash
        
        # Metrikler hesapla
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        buy_count = len([t for t in trades if t['type'] == 'BUY'])
        sell_count = len([t for t in trades if t['type'] == 'SELL'])
        win_count = 0
        
        # Win rate
        buy_prices = [t['price'] for t in trades if t['type'] == 'BUY']
        sell_prices = [t['price'] for t in trades if t['type'] == 'SELL']
        
        for i, buy_price in enumerate(buy_prices):
            if i < len(sell_prices) and sell_prices[i] > buy_price:
                win_count += 1
        
        win_rate = (win_count / len(buy_prices)) * 100 if buy_prices else 0
        
        return {
            'symbol': symbol,
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return_pct': total_return,
            'total_trades': len(trades),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'win_count': win_count,
            'win_rate_pct': win_rate,
            'trades': trades,
            'portfolio_values': portfolio_values,
            'max_drawdown': self._calculate_max_drawdown(portfolio_values)
        }
    
    def _get_historical_prices(self, symbol, days):
        """Tarihçe fiyatları al (simüle)"""
        prices = []
        base_price = 100
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            # Simüle trend
            price = base_price * (1 + (i * 0.001 + (i % 3) * 0.002))
            prices.append((date, price))
        
        return prices
    
    def _calculate_rsi(self, prices, period=14):
        """RSI hesapla"""
        if len(prices) < period:
            return 50
        
        prices = [p[1] for p in prices[-period:]]
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = sum(max(d, 0) for d in deltas) / len(deltas)
        losses = sum(max(-d, 0) for d in deltas) / len(deltas)
        
        if losses == 0:
            return 100
        
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_max_drawdown(self, values):
        """Max drawdown hesapla"""
        if not values:
            return 0
        
        peak = values[0]
        max_drawdown = 0
        
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown * 100
