"""Real-time Symbol Analyzer - Teknik Analiz & Sinyal"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from price_fetcher import PriceFetcher

class SymbolAnalyzer:
    def generate_signal(self, symbol):
        """AL/SAT sinyali ver"""
        try:
            # Gerçek fiyat al
            real_price, source = PriceFetcher.get_price(symbol)
            
            try:
                data = yf.download(symbol, period="3mo", progress=False)
            except:
                data = None
            
            # Null checks
            if data is None or data.empty or len(data) < 20:
                return {
                    "signal": "?", 
                    "reason": "Veri yok",
                    "price": real_price if real_price else 0,
                    "source": source
                }
            
            # RSI hesapla (NaN handling ile)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series: pd.Series = 100 - (100 / (1 + rs))
            rsi_clean: pd.Series = rsi_series.dropna()
            rsi: float = float(rsi_clean.iloc[-1]) if len(rsi_clean) > 0 else 50.0
            
            # MACD
            exp1 = data['Close'].ewm(span=12).mean()
            exp2 = data['Close'].ewm(span=26).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=9).mean()
            
            # MA - safe indexing
            ma20_vals: pd.Series = data['Close'].rolling(20).mean()
            ma50_vals: pd.Series = data['Close'].rolling(50).mean()
            
            if ma20_vals.isna().all() or ma50_vals.isna().all():
                return {"signal": "?", "reason": "MA hesaplanamadı"}
            
            ma20: float = float(ma20_vals.iloc[-1])
            ma50: float = float(ma50_vals.iloc[-1])
            # Gerçek fiyat varsa onu kullan, yoksa yfinance'dan al
            if real_price and real_price > 0:
                price = real_price
            else:
                price: float = float(data['Close'].iloc[-1])
            
            score = 0
            reasons = []
            
            if rsi < 30:
                score += 2
                reasons.append(f"RSI {rsi:.1f} - Oversold")
            elif rsi > 70:
                score -= 2
                reasons.append(f"RSI {rsi:.1f} - Overbought")
            
            macd_last: float = float(macd.iloc[-1])
            signal_last: float = float(signal_line.iloc[-1])
            
            if macd_last > signal_last:
                score += 1
                reasons.append("MACD Bullish")
            else:
                score -= 1
                reasons.append("MACD Bearish")
            
            if price > ma20 > ma50:
                score += 1
                reasons.append("Trend UP")
            elif price < ma20 < ma50:
                score -= 1
                reasons.append("Trend DOWN")
            
            if score >= 2:
                sig = "🟢 AL"
            elif score <= -2:
                sig = "🔴 SAT"
            else:
                sig = "⚪ HOLD"
            
            return {
                "signal": sig,
                "score": score,
                "rsi": float(rsi),
                "price": float(price),
                "ma20": float(ma20),
                "ma50": float(ma50),
                "reasons": reasons,
                "source": source
            }
        except Exception as e:
            return {"signal": "?", "reason": str(e)[:50]}
    
    def xrptry_manual_analysis(self):
        """XRPTRY manuel analiz (BTCTurk chart'tan)"""
        return {
            "signal": "🟢 AL",
            "current_price": 98.7,
            "support": 92.0,
            "resistance": 104.0,
            "change_24h": 0.78,
            "reasons": [
                "Bullish trend başladı (son 5 gün)",
                "Support (92.0) test ettikten sonra recovery",
                "Volume arttı (bullish signal)",
                "Fiyat MA üstünde"
            ],
            "target": 104.0,
            "stop_loss": 92.0,
            "risk_reward": 1.5
        }

if __name__ == "__main__":
    analyzer = SymbolAnalyzer()
    print(analyzer.xrptry_manual_analysis())
