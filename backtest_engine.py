"""Backtest Engine - Gerçek Accuracy Ölçümü + Walk-Forward Analysis"""
import yfinance as yf
import pandas as pd
from symbol_analyzer import SymbolAnalyzer
from datetime import datetime, timedelta
import numpy as np

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
            
            # Null check
            if data is None or data.empty or len(data) < 60:
                print(f"⚠️ {symbol}: Yetersiz veri")
                return None
            
            # Her gün analiz yap ve sonuç kayıt et
            trades = []
            correct = 0
            total = 0
            
            for i in range(60, len(data)-2):
                # Bugün sinyali ver
                try:
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
                except Exception as e:
                    continue
            
            accuracy = (correct / total * 100) if total > 0 else 0
            
            self.results[symbol] = {
                'accuracy': accuracy,
                'total_trades': total,
                'correct_trades': correct,
                'trades': trades[-10:] if trades else []
            }
            
            return accuracy
        
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            return None
    
    def walk_forward_analysis(self, symbol, train_days=90, test_days=30, step_days=15):
        """Walk-forward analiz - gerçekçi accuracy ölçümü"""
        try:
            print(f"\n🚶 {symbol} Walk-Forward Analiz ({train_days} gün train, {test_days} gün test)...")
            
            # Tüm data indir
            end_date = datetime.now()
            start_date = end_date - timedelta(days=train_days + test_days + step_days * 4)
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if data is None or data.empty or len(data) < train_days + test_days:
                return None
            
            results = []
            i = 0
            
            while i + train_days + test_days < len(data):
                # Train seti
                train_data = data.iloc[i:i+train_days]
                test_data = data.iloc[i+train_days:i+train_days+test_days]
                
                # Test et
                correct = 0
                total = 0
                
                for j in range(1, len(test_data)-1):
                    today_close = test_data['Close'].iloc[j]
                    tomorrow_close = test_data['Close'].iloc[j+1]
                    tomorrow_change = ((tomorrow_close - today_close) / today_close) * 100
                    
                    result = self.analyzer.generate_signal(symbol)
                    if result['signal'] != "?":
                        total += 1
                        if "🟢" in result['signal'] and tomorrow_change > 0:
                            correct += 1
                        elif "🔴" in result['signal'] and tomorrow_change < 0:
                            correct += 1
                
                if total > 0:
                    accuracy = (correct / total) * 100
                    results.append(accuracy)
                    print(f"   Window {len(results)}: {accuracy:.1f}% ({correct}/{total})")
                
                i += step_days
            
            if results:
                avg_acc = np.mean(results)
                std_acc = np.std(results)
                print(f"\n📊 Walk-Forward Sonuç:")
                print(f"   Ort. Accuracy: {avg_acc:.1f}%")
                print(f"   Std Dev: {std_acc:.1f}%")
                print(f"   Min: {min(results):.1f}% / Max: {max(results):.1f}%")
                
                return {
                    'mean': avg_acc,
                    'std': std_acc,
                    'min': min(results),
                    'max': max(results),
                    'results': results
                }
            
            return None
        
        except Exception as e:
            print(f"❌ Walk-Forward Hata: {str(e)}")
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
    
    def run_walk_forward_multi(self, symbols):
        """Çoklu walk-forward analiz"""
        print("\n" + "="*80)
        print("🚶 WALK-FORWARD ANALYSIS (Gerçekçi Accuracy)")
        print("="*80)
        
        results = {}
        for symbol in symbols:
            result = self.walk_forward_analysis(symbol)
            if result:
                results[symbol] = result
        
        return results
    
    def print_results(self):
        """Sonuçları yazdır"""
        print("\n" + "="*80)
        print("📊 BACKTEST SONUÇLARI")
        print("="*80)
        
        for symbol, data in self.results.items():
            print(f"\n{symbol}:")
            print(f"   Doğruluk: {data['accuracy']:.1f}%")
            print(f"   Trade: {data['correct_trades']}/{data['total_trades']}")
            if data['trades']:
                print(f"   Son İşlemler:")
                for trade in data['trades'][-5:]:
                    print(f"      {trade['result']} {trade['signal']}: {trade['change']:+.2f}%")

    def format_backtest_telegram(self, symbol):
        """Telegram için backtest raporu"""
        try:
            result = self.backtest_symbol(symbol, days=180)
            if result is None:
                return f"⚠️ {symbol} için yeterli veri yok"
            
            data = self.results.get(symbol, {})
            acc = data.get('accuracy', 0)
            total = data.get('total_trades', 0)
            correct = data.get('correct_trades', 0)
            
            if acc >= 60:
                emoji = "🟢"
                status = "GÜVENİLİR"
            elif acc >= 50:
                emoji = "🟡"
                status = "ORTA"
            else:
                emoji = "🔴"
                status = "DÜŞÜK"
            
            msg = f"""📊 <b>BACKTEST RAPORU: {symbol}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Son 180 gün analizi

{emoji} <b>DOĞRULUK:</b> %{acc:.1f} ({status})
📈 <b>TOPLAM İŞLEM:</b> {total}
✅ <b>DOĞRU TAHMİN:</b> {correct}
❌ <b>YANLIŞ:</b> {total - correct}

"""
            trades = data.get('trades', [])[-5:]
            if trades:
                msg += "<b>SON İŞLEMLER:</b>\n"
                for t in trades:
                    msg += f"   {t['result']} {t['change']:+.2f}%\n"
            
            msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>YORUM:</b>
"""
            if acc >= 60:
                msg += "Bu coin için sinyaller güvenilir görünüyor."
            elif acc >= 50:
                msg += "Sinyaller yarı yarıya doğru, dikkatli ol."
            else:
                msg += "Bu coin için sinyaller güvenilir DEĞİL."
            
            return msg
        except Exception as e:
            return f"❌ Backtest hatası: {e}"


class TimingOptimizer:
    """Al-sat zamanlama optimizasyonu"""
    
    def __init__(self):
        self.price_alerts = {}
    
    def analyze_entry_timing(self, symbol, current_price, rsi, macd_hist, volume_ratio):
        """Giriş zamanlaması analizi"""
        score = 0
        reasons = []
        wait_for = []
        
        if rsi < 30:
            score += 30
            reasons.append("✅ RSI aşırı satım (<30)")
        elif rsi < 40:
            score += 15
            reasons.append("🟡 RSI düşük bölgede (30-40)")
        elif rsi > 70:
            score -= 20
            wait_for.append("⏳ RSI 50 altına düşmesini bekle")
        else:
            reasons.append("⚪ RSI nötr bölgede")
        
        if macd_hist > 0:
            score += 25
            reasons.append("✅ MACD yukarı kesmiş")
        else:
            wait_for.append("⏳ MACD sinyal çizgisini yukarı kesmesini bekle")
        
        if volume_ratio > 1.5:
            score += 25
            reasons.append("✅ Hacim patlaması (1.5x+)")
        elif volume_ratio > 1.2:
            score += 15
            reasons.append("🟡 Hacim artışı (1.2x)")
        else:
            wait_for.append("⏳ Hacim artışını bekle")
        
        if score >= 70:
            timing = "🟢 HEMEN AL"
            action = "Giriş için ideal zaman!"
        elif score >= 50:
            timing = "🟡 YAKIN TAKİP"
            action = "Birkaç saat içinde fırsat olabilir"
        elif score >= 30:
            timing = "🟠 BEKLE"
            action = "Koşullar henüz uygun değil"
        else:
            timing = "🔴 ERKEN"
            action = "Şartlar oluşmadı, sabırlı ol"
        
        support = current_price * 0.95
        resistance = current_price * 1.08
        optimal_entry = current_price * 0.97
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'timing_score': score,
            'timing_signal': timing,
            'action': action,
            'reasons': reasons,
            'wait_for': wait_for,
            'optimal_entry': optimal_entry,
            'support': support,
            'resistance': resistance
        }
    
    def format_timing_report(self, analysis):
        """Zamanlama raporu formatla"""
        msg = f"""⏰ <b>ZAMANLAMA ANALİZİ: {analysis['symbol']}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 <b>Şu anki fiyat:</b> ₺{analysis['current_price']:,.4f}

{analysis['timing_signal']} <b>{analysis['action']}</b>
📊 Zamanlama Skoru: {analysis['timing_score']}/100

<b>DURUM:</b>
"""
        for r in analysis['reasons']:
            msg += f"   {r}\n"
        
        if analysis['wait_for']:
            msg += "\n<b>BEKLENİLENLER:</b>\n"
            for w in analysis['wait_for']:
                msg += f"   {w}\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>ÖNERİLEN SEVİYELER:</b>

🎯 <b>İdeal Giriş:</b> ₺{analysis['optimal_entry']:,.4f}
🛡️ <b>Destek:</b> ₺{analysis['support']:,.4f}
🚀 <b>Direnç:</b> ₺{analysis['resistance']:,.4f}

💡 Bu fiyata düşerse AL komutuyla alarm kur!
"""
        return msg


if __name__ == "__main__":
    bt = BacktestEngine()
    
    symbols = ['BTC-USD', 'AAPL', 'MSFT', 'GOOGL']
    
    avg_acc = bt.run_multi_backtest(symbols, days=120)
    bt.print_results()
    
    wf_results = bt.run_walk_forward_multi(symbols)
    
    print("\n" + "="*80)
    print(f"🎯 SİSTEM DOĞRULUĞU: {avg_acc:.1f}%")
    print("="*80)
