"""
HİSSE BACKTESTING MOTORU
Geçmiş strateji testi, performans metrikleri
Win-rate, Sharpe ratio, Max drawdown hesaplama
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class StockBacktest:
    def __init__(self):
        self.results = {}
    
    def fetch_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Tarihsel veri çek"""
        try:
            ticker = f"{symbol}.IS"
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            return df
        except Exception as e:
            logger.error(f"Veri çekme hatası ({symbol}): {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Teknik indikatörler hesapla"""
        if df.empty:
            return df
        
        df = df.copy()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Moving Averages
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        
        # MACD
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Bollinger Bands
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * 2)
        
        # NaN'leri doldur (date sütununu korumak için dropna yerine fillna)
        indicator_cols = ['rsi', 'sma_20', 'sma_50', 'ema_12', 'ema_26', 'macd', 'macd_signal', 'bb_mid', 'bb_std', 'bb_upper', 'bb_lower']
        for col in indicator_cols:
            if col in df.columns:
                df[col] = df[col].fillna(method='bfill').fillna(method='ffill').fillna(50 if col == 'rsi' else 0)
        
        return df
    
    def run_rsi_strategy(self, symbol: str, rsi_buy: int = 30, rsi_sell: int = 70) -> Dict:
        """RSI stratejisi backtest"""
        df = self.fetch_historical_data(symbol)
        df = self.calculate_indicators(df)
        
        if df.empty or len(df) < 50:
            return {'error': 'Yetersiz veri'}
        
        trades = []
        position = None
        
        for i in range(1, len(df)):
            rsi = df['rsi'].iloc[i]
            price = df['close'].iloc[i]
            date = df['date'].iloc[i] if 'date' in df.columns else df.index[i]
            
            if position is None and rsi < rsi_buy:
                position = {'entry_price': price, 'entry_date': date}
            
            elif position is not None and rsi > rsi_sell:
                pnl_percent = (price - position['entry_price']) / position['entry_price'] * 100
                trades.append({
                    'entry_date': str(position['entry_date']),
                    'exit_date': str(date),
                    'entry_price': position['entry_price'],
                    'exit_price': price,
                    'pnl_percent': pnl_percent
                })
                position = None
        
        return self._calculate_metrics(symbol, 'RSI', trades)
    
    def run_ma_crossover_strategy(self, symbol: str, short_period: int = 20, long_period: int = 50) -> Dict:
        """MA Crossover stratejisi backtest"""
        df = self.fetch_historical_data(symbol)
        df = self.calculate_indicators(df)
        
        if df.empty or len(df) < long_period + 10:
            return {'error': 'Yetersiz veri'}
        
        trades = []
        position = None
        
        for i in range(1, len(df)):
            sma_short = df['sma_20'].iloc[i]
            sma_long = df['sma_50'].iloc[i]
            prev_short = df['sma_20'].iloc[i-1]
            prev_long = df['sma_50'].iloc[i-1]
            price = df['close'].iloc[i]
            date = df['date'].iloc[i] if 'date' in df.columns else df.index[i]
            
            # Golden cross (AL)
            if position is None and prev_short <= prev_long and sma_short > sma_long:
                position = {'entry_price': price, 'entry_date': date}
            
            # Death cross (SAT)
            elif position is not None and prev_short >= prev_long and sma_short < sma_long:
                pnl_percent = (price - position['entry_price']) / position['entry_price'] * 100
                trades.append({
                    'entry_date': str(position['entry_date']),
                    'exit_date': str(date),
                    'entry_price': position['entry_price'],
                    'exit_price': price,
                    'pnl_percent': pnl_percent
                })
                position = None
        
        return self._calculate_metrics(symbol, 'MA_CROSSOVER', trades)
    
    def run_bollinger_strategy(self, symbol: str) -> Dict:
        """Bollinger Bands stratejisi backtest"""
        df = self.fetch_historical_data(symbol)
        df = self.calculate_indicators(df)
        
        if df.empty or len(df) < 50:
            return {'error': 'Yetersiz veri'}
        
        trades = []
        position = None
        
        for i in range(1, len(df)):
            price = df['close'].iloc[i]
            bb_lower = df['bb_lower'].iloc[i]
            bb_upper = df['bb_upper'].iloc[i]
            date = df['date'].iloc[i] if 'date' in df.columns else df.index[i]
            
            # Fiyat alt bandı kırdığında AL
            if position is None and price < bb_lower:
                position = {'entry_price': price, 'entry_date': date}
            
            # Fiyat üst bandı kırdığında SAT
            elif position is not None and price > bb_upper:
                pnl_percent = (price - position['entry_price']) / position['entry_price'] * 100
                trades.append({
                    'entry_date': str(position['entry_date']),
                    'exit_date': str(date),
                    'entry_price': position['entry_price'],
                    'exit_price': price,
                    'pnl_percent': pnl_percent
                })
                position = None
        
        return self._calculate_metrics(symbol, 'BOLLINGER', trades)
    
    def _calculate_metrics(self, symbol: str, strategy: str, trades: List[Dict]) -> Dict:
        """Performans metrikleri hesapla"""
        if not trades:
            return {
                'symbol': symbol,
                'strategy': strategy,
                'total_trades': 0,
                'message': 'İşlem bulunamadı'
            }
        
        pnls = [t['pnl_percent'] for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        
        total_return = sum(pnls)
        win_rate = len(wins) / len(pnls) * 100 if pnls else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        # Profit Factor
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Max Drawdown
        cumulative = np.cumsum(pnls)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = cumulative - running_max
        max_drawdown = abs(min(drawdowns)) if len(drawdowns) > 0 else 0
        
        # Sharpe Ratio (basit)
        if len(pnls) > 1:
            sharpe = np.mean(pnls) / np.std(pnls) if np.std(pnls) > 0 else 0
        else:
            sharpe = 0
        
        return {
            'symbol': symbol,
            'strategy': strategy,
            'total_trades': len(trades),
            'win_rate': round(win_rate, 2),
            'total_return': round(total_return, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe, 2),
            'best_trade': round(max(pnls), 2) if pnls else 0,
            'worst_trade': round(min(pnls), 2) if pnls else 0,
            'trades': trades[-10:]  # Son 10 işlem
        }
    
    def run_all_strategies(self, symbol: str) -> Dict:
        """Tüm stratejileri test et"""
        results = {
            'symbol': symbol,
            'strategies': {}
        }
        
        # RSI
        rsi_result = self.run_rsi_strategy(symbol)
        if 'error' not in rsi_result:
            results['strategies']['RSI'] = rsi_result
        
        # MA Crossover
        ma_result = self.run_ma_crossover_strategy(symbol)
        if 'error' not in ma_result:
            results['strategies']['MA_CROSSOVER'] = ma_result
        
        # Bollinger
        bb_result = self.run_bollinger_strategy(symbol)
        if 'error' not in bb_result:
            results['strategies']['BOLLINGER'] = bb_result
        
        # En iyi strateji
        best_strategy = None
        best_return = -999
        
        for name, data in results['strategies'].items():
            if data.get('total_return', -999) > best_return:
                best_return = data['total_return']
                best_strategy = name
        
        results['best_strategy'] = best_strategy
        results['best_return'] = best_return
        
        return results
    
    def generate_report(self, symbol: str) -> str:
        """Telegram için backtest raporu"""
        data = self.run_all_strategies(symbol)
        
        report = f"""📊 <b>{symbol} BACKTEST RAPORU</b>
━━━━━━━━━━━━━━━━━━━━━

🏆 <b>En İyi Strateji:</b> {data.get('best_strategy', 'N/A')}
📈 <b>En İyi Getiri:</b> %{data.get('best_return', 0):+.2f}

"""
        
        for name, strat in data.get('strategies', {}).items():
            emoji = "🟢" if strat.get('total_return', 0) > 0 else "🔴"
            report += f"""{emoji} <b>{name}</b>
   📊 İşlem: {strat.get('total_trades', 0)} | Win: %{strat.get('win_rate', 0):.1f}
   💰 Getiri: %{strat.get('total_return', 0):+.2f}
   📉 Max DD: %{strat.get('max_drawdown', 0):.2f}
   ⚖️ Sharpe: {strat.get('sharpe_ratio', 0):.2f}

"""
        
        report += "━━━━━━━━━━━━━━━━━━━━━\n🤖 <i>Hisse Backtesting Motoru</i>"
        
        return report
