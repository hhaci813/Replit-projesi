"""100 TL BTCTurk Simülasyonu - Otomatik Alım-Satım"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from price_fetcher import PriceFetcher
from symbol_analyzer import SymbolAnalyzer

class SimulatedTrader:
    def __init__(self, initial_balance=100):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.btc_holding = 0
        self.trades = []
        self.analyzer = SymbolAnalyzer()
    
    def backtest_last_7_days(self):
        """Son 7 günü simüle et"""
        print("\n" + "="*80)
        print("💰 BTCTurk SİMÜLASYON: 100 TL ile 7 GÜN Otomatik Trading")
        print("="*80)
        
        # BTC geçmiş verisi
        btc_data = yf.download("BTC-USD", period="7d", interval="1h", progress=False)
        
        if btc_data is None or btc_data.empty:
            print("❌ Veri alınamadı")
            return None
        
        btc_data = btc_data.reset_index()
        print(f"\n📊 {len(btc_data)} saat veri analiz ediliyor...\n")
        
        # Saatlik trading
        for idx, row in btc_data.iterrows():
            timestamp = row['Datetime']
            price_usd = row['Close']
            price_try = price_usd * 30  # 1 USD = 30 TL
            
            # Analiz yap
            signal = self._get_signal(btc_data, idx)
            
            if signal == "🟢 AL" and self.balance > 0:
                btc_amount = self.balance / price_try
                self.btc_holding += btc_amount
                self.balance = 0
                self.trades.append({
                    'time': timestamp,
                    'action': 'AL',
                    'price_try': price_try,
                    'btc': btc_amount,
                    'balance_after': 0
                })
                print(f"  🟢 {timestamp.strftime('%Y-%m-%d %H:%M')} - AL: ₺{price_try:,.0f} ({btc_amount:.6f} BTC)")
            
            elif signal == "🔴 SAT" and self.btc_holding > 0:
                tl_earned = self.btc_holding * price_try
                profit = tl_earned - self.initial_balance if self.trades else 0
                self.balance = tl_earned
                self.btc_holding = 0
                self.trades.append({
                    'time': timestamp,
                    'action': 'SAT',
                    'price_try': price_try,
                    'balance': tl_earned,
                    'profit': profit
                })
                print(f"  🔴 {timestamp.strftime('%Y-%m-%d %H:%M')} - SAT: ₺{price_try:,.0f} → ₺{tl_earned:,.2f} (Kar: ₺{profit:+.2f})")
        
        # Final hesap
        if self.btc_holding > 0:
            current_price_usd, _ = PriceFetcher.get_price("BTC-USD")
            current_price_try = current_price_usd * 30
            final_balance = self.btc_holding * current_price_try
        else:
            final_balance = self.balance
        
        net_profit = final_balance - self.initial_balance
        roi = (net_profit / self.initial_balance) * 100
        
        print("\n" + "="*80)
        print("📈 SONUÇLAR:")
        print("="*80)
        print(f"💵 Başlangıç: ₺{self.initial_balance:.2f}")
        print(f"💰 Final: ₺{final_balance:.2f}")
        print(f"📊 Kar/Zarar: ₺{net_profit:+.2f}")
        print(f"📈 Getiri: {roi:+.1f}%")
        print(f"📋 Toplam İşlem: {len(self.trades)}")
        print("="*80)
        
        return {
            'initial': self.initial_balance,
            'final': final_balance,
            'profit': net_profit,
            'roi': roi,
            'trades_count': len(self.trades)
        }
    
    def _get_signal(self, data, current_idx, lookback=20):
        """Saatlik sinyali hesapla"""
        if current_idx < lookback:
            return None
        
        subset = data.iloc[max(0, current_idx-lookback):current_idx+1]
        close_prices = subset['Close'].values
        
        if len(close_prices) < 5:
            return "⚪ HOLD"
        
        # RSI
        delta = pd.Series(close_prices).diff().values
        gains = delta[delta > 0].mean() if any(delta > 0) else 0
        losses = -delta[delta < 0].mean() if any(delta < 0) else 0
        rs = gains / losses if losses > 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs > 0 else 50
        
        # MA
        ma_fast = close_prices[-5:].mean()
        ma_slow = close_prices[-20:].mean() if len(close_prices) >= 20 else close_prices.mean()
        
        # Signal
        if float(rsi) < 30 and float(ma_fast) > float(ma_slow):
            return "🟢 AL"
        elif float(rsi) > 70 or float(ma_fast) < float(ma_slow):
            return "🔴 SAT"
        else:
            return "⚪ HOLD"


if __name__ == "__main__":
    trader = SimulatedTrader(initial_balance=100)
    result = trader.backtest_last_7_days()
    
    if result:
        print(f"\n💡 ÖZET:")
        print(f"   • 100 TL'yle başladın")
        print(f"   • {result['trades_count']} işlem yapıldı")
        print(f"   • Net Kar: ₺{result['profit']:+.2f} ({result['roi']:+.1f}%)")
        
        if result['profit'] > 0:
            print(f"\n🎉 BAŞARILI! Sistem ₺{result['profit']:.2f} kazandırabilirdi")
        else:
            print(f"\n⚠️  Kâr olmadı, fakat bu sadece 7 günlük testti")
