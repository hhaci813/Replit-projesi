"""Backtest Engine - Gerçek Accuracy Ölçümü"""
import yfinance as yf
import pandas as pd
from symbol_analyzer import SymbolAnalyzer
from datetime import datetime, timedelta

class BacktestEngine:
    def __init__(self):
        self.analyzer = SymbolAnalyzer()
        self.results = {}
    
    def backtest_symbol(self, symbol, days=180):
        """Sembol için backtest yap"""
        try:
            print(f"\n📊 {symbol} Backtest Başlıyor ({days} gün)...")
            
            # Data indir
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days+30)
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if len(data) < 60:
                return None
            
            # Her gün analiz yap ve sonuç kayıt et
            trades = []
            correct = 0
            total = 0
            
            for i in range(60, len(data)-2):
                # Bugün sinyali ver
                today_high = data['High'].iloc[i]
                today_low = data['Low'].iloc[i]
                today_close = data['Close'].iloc[i]
                
                # Yarının sonucuna bak
                tomorrow_close = data['Close'].iloc[i+1]
                tomorrow_change = ((tomorrow_close - today_close) / today_close) * 100
                
                # Analiz yap
                result = self.analyzer.generate_signal(symbol)
                if result['signal'] == "?":
                    continue
                
                signal = result['signal']
                total += 1
                
                # Doğru mu yanlış mı?
                if "🟢" in signal and tomorrow_change > 0:
                    correct += 1
                    result_str = "✅"
                elif "🔴" in signal and tomorrow_change < 0:
                    correct += 1
                    result_str = "✅"
                else:
                    result_str = "❌"
                
                trades.append({
                    'date': data.index[i],
                    'signal': signal,
                    'change': tomorrow_change,
                    'result': result_str
                })
            
            accuracy = (correct / total * 100) if total > 0 else 0
            
            self.results[symbol] = {
                'accuracy': accuracy,
                'total_trades': total,
                'correct_trades': correct,
                'trades': trades[-10:]  # Son 10 trade
            }
            
            return accuracy
        
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            return None
    
    def run_multi_backtest(self, symbols, days=180):
        """Çoklu sembol backtest"""
        print("\n" + "="*80)
        print(f"🧪 BACKTEST ENGINE - ÇOKLU SEMBOL ({days} gün)")
        print("="*80)
        
        accuracies = []
        
        for symbol in symbols:
            acc = self.backtest_symbol(symbol, days)
            if acc:
                accuracies.append(acc)
                print(f"   {symbol}: {acc:.1f}% doğru")
        
        if accuracies:
            avg = sum(accuracies) / len(accuracies)
            print(f"\n📈 ORTALAMA DOĞRULUK: {avg:.1f}%")
            return avg
        
        return 0
    
    def print_results(self):
        """Sonuçları yazdır"""
        print("\n" + "="*80)
        print("📊 BACKTEST SONUÇLARI")
        print("="*80)
        
        for symbol, data in self.results.items():
            print(f"\n{symbol}:")
            print(f"   Doğruluk: {data['accuracy']:.1f}%")
            print(f"   Trade: {data['correct_trades']}/{data['total_trades']}")
            print(f"   Son İşlemler:")
            for trade in data['trades'][-5:]:
                print(f"      {trade['result']} {trade['signal']}: {trade['change']:+.2f}%")

if __name__ == "__main__":
    bt = BacktestEngine()
    avg_acc = bt.run_multi_backtest(['BTC-USD', 'AAPL', 'MSFT', 'GOOGL'], days=120)
    bt.print_results()
    
    print("\n" + "="*80)
    print(f"🎯 SİSTEM DOĞRULUĞU: {avg_acc:.1f}%")
    print("="*80)
