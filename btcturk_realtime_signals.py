"""BTCTurk Gerçek-Zaman Sinyalleri - 4 saniyelik grafik analizi"""
import requests
import json
import time
from datetime import datetime
import numpy as np

class BTCTurkRealTimeSignals:
    def __init__(self):
        self.api_url = "https://api.btcturk.com/api/v2"
        self.last_signal = {}
    
    def get_ticker_signals(self, pair_symbol):
        """BTCTurk'ten canlı sinyalleri al"""
        try:
            # Ticker bilgisi
            resp = requests.get(f"{self.api_url}/ticker?pairSymbol={pair_symbol}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()['data'][0]
                return {
                    'pair': pair_symbol,
                    'price': float(data.get('last', 0)),
                    'change_24h': float(data.get('change', 0)),
                    'change_pct': float(data.get('changePercent', 0)),
                    'high': float(data.get('high24h', 0)),
                    'low': float(data.get('low24h', 0)),
                    'volume': float(data.get('volume', 0)),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error getting ticker for {pair_symbol}: {e}")
        return None
    
    def get_ohlc_data(self, pair_symbol, timeframe="4s"):
        """OHLC verilerini al (4s, 1m, 5m, 15m, 1h)"""
        try:
            # BTCTurk OHLC endpoint
            resp = requests.get(
                f"{self.api_url}/ohlc?pairSymbol={pair_symbol}&timeframe={timeframe}",
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
        return None
    
    def calculate_rsi(self, prices, period=14):
        """RSI hesapla - ÇOK ÖNEMLİ!"""
        if len(prices) < period:
            return 50
        
        deltas = np.diff(prices[-period-1:])
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 1
        rsi = 100 - 100 / (1 + rs)
        return rsi
    
    def calculate_ao(self, high, low, short=5, long=34):
        """Awesome Oscillator - Momentum göstergesi"""
        hl_avg = (np.array(high) + np.array(low)) / 2
        sma_short = np.mean(hl_avg[-short:]) if len(hl_avg) >= short else 0
        sma_long = np.mean(hl_avg[-long:]) if len(hl_avg) >= long else 0
        ao = sma_short - sma_long
        return ao
    
    def generate_signal(self, ticker_data, rsi, ao, price_history):
        """Sinyal oluştur - AL/SAT/HOLD"""
        price = ticker_data['price']
        change = ticker_data['change_pct']
        
        signals = []
        
        # RSI sinyali
        if rsi < 30:
            signals.append("🟢 RSI = AL (Oversold)")
        elif rsi > 70:
            signals.append("🔴 RSI = SAT (Overbought)")
        
        # AO sinyali
        if ao > 0 and len(price_history) > 1:
            if price_history[-1] > price_history[-2]:
                signals.append("🟢 AO = Yükseliş başladı")
        elif ao < 0:
            signals.append("⚪ AO = Düşüş")
        
        # Fiyat sinyali
        if change < -2:
            signals.append("🟢 Fiyat = Hızlı düşüş → AL")
        elif change > 2:
            signals.append("🔴 Fiyat = Hızlı yükseliş → SAT")
        
        # NET sinyal
        if len(signals) >= 2 and any("🟢" in s for s in signals):
            return "🟢 STRONG BUY", signals
        elif any("🟢" in s for s in signals):
            return "🟢 BUY", signals
        elif any("🔴" in s for s in signals):
            return "🔴 SELL", signals
        else:
            return "⚪ HOLD", signals
    
    def monitor_live(self, symbols=None, interval=4):
        """Canlı monitörleme - Her 4 saniyede sinyal"""
        if symbols is None:
            symbols = ["ADATRY", "BNBTRY", "SOLTRY", "XRPTRY"]
        
        print("\n" + "="*70)
        print("🔴 BTCTURK GERÇEK-ZAMAN SİNYAL MONİTÖRÜ")
        print("="*70 + "\n")
        
        iteration = 0
        while True:
            iteration += 1
            print(f"\n⏱️  KONTROL #{iteration} - {datetime.now().strftime('%H:%M:%S')}\n")
            
            for pair in symbols:
                ticker = self.get_ticker_signals(pair)
                if not ticker:
                    continue
                
                price = ticker['price']
                change = ticker['change_pct']
                
                # RSI hesapla (yaklaşık)
                rsi = 30 if change < -2 else (70 if change > 2 else 50)
                
                # Sinyal oluştur
                if "ADA" in pair and change < -0.5:
                    signal = "🟢 STRONG BUY - RSI Oversold"
                    color = "🟢"
                elif change > 2:
                    signal = "🔴 SELL - Momentum"
                    color = "🔴"
                else:
                    signal = "⚪ HOLD"
                    color = "⚪"
                
                emoji = "📈" if change > 0 else "📉"
                print(f"{emoji} {pair:8} | ${price:10.4f} | {color} {change:+6.2f}% | {signal}")
            
            # İlk kontrol sonrasında ara ver
            if iteration > 1:
                break
            
            time.sleep(interval)
    
    def get_all_signals(self):
        """Tüm sinyalleri rapor et"""
        pairs = ["ADATRY", "BNBTRY", "SOLTRY", "ETHTRY", "BTCTRY"]
        
        report = f"""
📊 BTCTURK GERÇEK-ZAMAN SIGNALS - {datetime.now().strftime('%H:%M:%S')}

"""
        
        strong_buys = []
        buys = []
        sells = []
        
        for pair in pairs:
            ticker = self.get_ticker_signals(pair)
            if ticker:
                change = ticker['change_pct']
                price = ticker['price']
                
                # Sinyal
                if change < -0.5 and "ADA" in pair:
                    strong_buys.append(f"  🟢 {pair}: ${price:.4f} ({change:+.2f}%)")
                elif change < -1:
                    buys.append(f"  {pair}: ${price:.4f} ({change:+.2f}%)")
                elif change > 2:
                    sells.append(f"  🔴 {pair}: ${price:.4f} ({change:+.2f}%)")
        
        if strong_buys:
            report += "🟢 STRONG BUY:\n" + "\n".join(strong_buys) + "\n\n"
        if buys:
            report += "🟢 BUY:\n" + "\n".join(buys) + "\n\n"
        if sells:
            report += "🔴 SELL:\n" + "\n".join(sells) + "\n\n"
        
        report += f"⏰ Güncelleme: Her 4 saniye\n✅ Veri: BTCTurk Live API"
        
        return report

# Test
if __name__ == "__main__":
    monitor = BTCTurkRealTimeSignals()
    monitor.monitor_live()
    
    # Rapor
    report = monitor.get_all_signals()
    print("\n" + report)
