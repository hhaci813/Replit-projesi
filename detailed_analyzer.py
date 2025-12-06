"""
DETAYLI ANALİZ MODÜLÜ - /analiz KOMUTU
Tek kripto için tam teknik analiz, destek/direnç, grafik analizi
"""

import os
import requests
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

class DetailedAnalyzer:
    def __init__(self):
        self.timeframes = ["1h", "4h", "1d", "1w"]
    
    def get_ticker_data(self, symbol: str) -> dict:
        """Ticker verisi al"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            data = resp.json().get('data', [])
            
            for ticker in data:
                if ticker.get('pairNormalized') == f"{symbol}_USDT":
                    return {
                        "symbol": symbol,
                        "price": float(ticker.get('last', 0)),
                        "high24": float(ticker.get('high', 0)),
                        "low24": float(ticker.get('low', 0)),
                        "volume": float(ticker.get('volume', 0)),
                        "change24": float(ticker.get('dailyPercent', 0)),
                        "bid": float(ticker.get('bid', 0)),
                        "ask": float(ticker.get('ask', 0)),
                        "open": float(ticker.get('open', 0))
                    }
            return None
        except:
            return None
    
    def get_historical_data(self, symbol: str, days: int = 30) -> list:
        """Tarihçe verisi al"""
        try:
            end_time = int(datetime.now().timestamp())
            start_time = int((datetime.now() - timedelta(days=days)).timestamp())
            
            resp = requests.get(
                f"https://graph-api.btcturk.com/v1/klines/history",
                params={
                    "symbol": f"{symbol}USDT",
                    "resolution": "D",
                    "from": start_time,
                    "to": end_time
                },
                timeout=15
            )
            
            data = resp.json()
            if 'c' in data:
                return {
                    "close": [float(x) for x in data.get('c', [])],
                    "high": [float(x) for x in data.get('h', [])],
                    "low": [float(x) for x in data.get('l', [])],
                    "open": [float(x) for x in data.get('o', [])],
                    "volume": [float(x) for x in data.get('v', [])]
                }
        except:
            pass
        return None
    
    def calculate_rsi(self, prices: list, period: int = 14) -> float:
        """RSI hesapla"""
        if len(prices) < period + 1:
            return 50
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(d, 0) for d in deltas]
        losses = [abs(min(d, 0)) for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices: list) -> dict:
        """MACD hesapla"""
        if len(prices) < 26:
            return {"macd": 0, "signal": 0, "histogram": 0}
        
        def ema(data, period):
            multiplier = 2 / (period + 1)
            ema_val = sum(data[:period]) / period
            for price in data[period:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return ema_val
        
        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd_line = ema12 - ema26
        
        return {
            "macd": macd_line,
            "signal": macd_line * 0.9,  # Simplified
            "histogram": macd_line * 0.1,
            "trend": "BULLISH" if macd_line > 0 else "BEARISH"
        }
    
    def calculate_bollinger(self, prices: list, period: int = 20) -> dict:
        """Bollinger Bands hesapla"""
        if len(prices) < period:
            return None
        
        recent = prices[-period:]
        middle = sum(recent) / period
        
        variance = sum((p - middle) ** 2 for p in recent) / period
        std = variance ** 0.5
        
        upper = middle + (std * 2)
        lower = middle - (std * 2)
        
        current = prices[-1]
        position = (current - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
        
        if position > 0.8:
            signal = "OVERBOUGHT"
        elif position < 0.2:
            signal = "OVERSOLD"
        else:
            signal = "NEUTRAL"
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "position": position * 100,
            "signal": signal
        }
    
    def calculate_support_resistance(self, highs: list, lows: list, current: float) -> dict:
        """Destek ve direnç seviyeleri"""
        if not highs or not lows:
            return None
        
        # Son 30 günün en yüksek ve en düşükleri
        recent_highs = sorted(highs[-30:], reverse=True)[:5]
        recent_lows = sorted(lows[-30:])[:5]
        
        # En yakın direnç
        resistances = [h for h in recent_highs if h > current]
        resistance1 = min(resistances) if resistances else current * 1.05
        resistance2 = max(resistances) if resistances else current * 1.10
        
        # En yakın destek
        supports = [l for l in recent_lows if l < current]
        support1 = max(supports) if supports else current * 0.95
        support2 = min(supports) if supports else current * 0.90
        
        return {
            "resistance1": resistance1,
            "resistance2": resistance2,
            "support1": support1,
            "support2": support2,
            "range_pct": ((resistance1 - support1) / current) * 100
        }
    
    def calculate_momentum(self, prices: list) -> dict:
        """Momentum göstergeleri"""
        if len(prices) < 20:
            return None
        
        # ROC (Rate of Change)
        roc_5 = ((prices[-1] - prices[-5]) / prices[-5]) * 100 if len(prices) >= 5 else 0
        roc_10 = ((prices[-1] - prices[-10]) / prices[-10]) * 100 if len(prices) >= 10 else 0
        roc_20 = ((prices[-1] - prices[-20]) / prices[-20]) * 100 if len(prices) >= 20 else 0
        
        # Trend strength
        above_ma = sum(1 for i in range(-10, 0) if prices[i] > sum(prices[-20:]) / 20)
        trend_strength = above_ma * 10  # 0-100
        
        if roc_5 > 5 and roc_10 > 10:
            momentum = "GÜÇLÜ YUKARI"
        elif roc_5 > 0 and roc_10 > 0:
            momentum = "YUKARI"
        elif roc_5 < -5 and roc_10 < -10:
            momentum = "GÜÇLÜ AŞAĞI"
        elif roc_5 < 0 and roc_10 < 0:
            momentum = "AŞAĞI"
        else:
            momentum = "YATAY"
        
        return {
            "roc_5": roc_5,
            "roc_10": roc_10,
            "roc_20": roc_20,
            "trend_strength": trend_strength,
            "momentum": momentum
        }
    
    def calculate_volume_analysis(self, volumes: list, prices: list) -> dict:
        """Hacim analizi"""
        if not volumes or len(volumes) < 20:
            return None
        
        avg_volume = sum(volumes[-20:]) / 20
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Price-Volume correlation
        price_up = prices[-1] > prices[-2] if len(prices) >= 2 else True
        volume_up = current_volume > avg_volume
        
        if price_up and volume_up:
            signal = "CONFIRMED UPTREND"
            emoji = "🟢"
        elif not price_up and volume_up:
            signal = "SELLING PRESSURE"
            emoji = "🔴"
        elif price_up and not volume_up:
            signal = "WEAK RALLY"
            emoji = "🟡"
        else:
            signal = "LOW INTEREST"
            emoji = "⚪"
        
        return {
            "current": current_volume,
            "average": avg_volume,
            "ratio": volume_ratio,
            "signal": signal,
            "emoji": emoji
        }
    
    def full_analysis(self, symbol: str) -> dict:
        """Tam analiz"""
        ticker = self.get_ticker_data(symbol)
        if not ticker:
            return {"error": f"{symbol} bulunamadı"}
        
        history = self.get_historical_data(symbol, 60)
        
        result = {
            "symbol": symbol,
            "ticker": ticker,
            "timestamp": datetime.now().isoformat()
        }
        
        if history:
            prices = history["close"]
            
            result["rsi"] = self.calculate_rsi(prices)
            result["macd"] = self.calculate_macd(prices)
            result["bollinger"] = self.calculate_bollinger(prices)
            result["support_resistance"] = self.calculate_support_resistance(
                history["high"], history["low"], ticker["price"]
            )
            result["momentum"] = self.calculate_momentum(prices)
            result["volume"] = self.calculate_volume_analysis(history["volume"], prices)
            
            # Genel sinyal
            signals = []
            
            # RSI sinyali
            rsi = result["rsi"]
            if rsi < 30:
                signals.append(("RSI", "BUY", 2))
            elif rsi > 70:
                signals.append(("RSI", "SELL", 2))
            else:
                signals.append(("RSI", "NEUTRAL", 0))
            
            # MACD sinyali
            if result["macd"]["trend"] == "BULLISH":
                signals.append(("MACD", "BUY", 1))
            else:
                signals.append(("MACD", "SELL", 1))
            
            # Bollinger sinyali
            if result["bollinger"]:
                if result["bollinger"]["signal"] == "OVERSOLD":
                    signals.append(("BB", "BUY", 2))
                elif result["bollinger"]["signal"] == "OVERBOUGHT":
                    signals.append(("BB", "SELL", 2))
            
            # Momentum sinyali
            if result["momentum"]:
                mom = result["momentum"]["momentum"]
                if "YUKARI" in mom:
                    signals.append(("MOM", "BUY", 1))
                elif "AŞAĞI" in mom:
                    signals.append(("MOM", "SELL", 1))
            
            # Toplam skor
            buy_score = sum(s[2] for s in signals if s[1] == "BUY")
            sell_score = sum(s[2] for s in signals if s[1] == "SELL")
            
            if buy_score >= 4:
                result["overall"] = "STRONG_BUY"
            elif buy_score > sell_score:
                result["overall"] = "BUY"
            elif sell_score >= 4:
                result["overall"] = "STRONG_SELL"
            elif sell_score > buy_score:
                result["overall"] = "SELL"
            else:
                result["overall"] = "HOLD"
            
            result["signals"] = signals
            result["scores"] = {"buy": buy_score, "sell": sell_score}
        
        return result
    
    def generate_report(self, symbol: str) -> str:
        """Detaylı analiz raporu"""
        analysis = self.full_analysis(symbol.upper())
        
        if "error" in analysis:
            return f"❌ {analysis['error']}"
        
        ticker = analysis["ticker"]
        
        # Overall emoji
        overall = analysis.get("overall", "HOLD")
        if overall == "STRONG_BUY":
            overall_emoji = "🔥"
            overall_text = "GÜÇLÜ AL"
        elif overall == "BUY":
            overall_emoji = "🟢"
            overall_text = "AL"
        elif overall == "STRONG_SELL":
            overall_emoji = "🔴"
            overall_text = "GÜÇLÜ SAT"
        elif overall == "SELL":
            overall_emoji = "🟡"
            overall_text = "SAT"
        else:
            overall_emoji = "⚪"
            overall_text = "BEKLE"
        
        report = f"""
🔍 <b>DETAYLI ANALİZ: {symbol.upper()}</b>
━━━━━━━━━━━━━━━━━━━━━━━

💰 <b>FİYAT BİLGİSİ</b>
• Şu an: ${ticker['price']:.6f}
• 24s Değişim: {ticker['change24']:+.2f}%
• En Yüksek: ${ticker['high24']:.6f}
• En Düşük: ${ticker['low24']:.6f}
• Hacim: ${ticker['volume']:,.0f}

"""
        
        # RSI
        rsi = analysis.get("rsi", 50)
        if rsi < 30:
            rsi_emoji = "🟢"
            rsi_status = "AŞIRI SATIM"
        elif rsi > 70:
            rsi_emoji = "🔴"
            rsi_status = "AŞIRI ALIM"
        else:
            rsi_emoji = "⚪"
            rsi_status = "NORMAL"
        
        report += f"""📊 <b>TEKNİK GÖSTERGELER</b>
• RSI(14): {rsi:.1f} {rsi_emoji} {rsi_status}
"""
        
        # MACD
        macd = analysis.get("macd", {})
        macd_emoji = "🟢" if macd.get("trend") == "BULLISH" else "🔴"
        report += f"• MACD: {macd.get('macd', 0):.6f} {macd_emoji} {macd.get('trend', 'N/A')}\n"
        
        # Bollinger
        bb = analysis.get("bollinger")
        if bb:
            bb_emoji = "🟢" if bb["signal"] == "OVERSOLD" else "🔴" if bb["signal"] == "OVERBOUGHT" else "⚪"
            report += f"• Bollinger: %{bb['position']:.0f} pozisyon {bb_emoji}\n"
        
        # Momentum
        mom = analysis.get("momentum")
        if mom:
            report += f"• Momentum: {mom['momentum']} (ROC5: {mom['roc_5']:+.1f}%)\n"
        
        # Volume
        vol = analysis.get("volume")
        if vol:
            report += f"• Hacim: {vol['emoji']} {vol['signal']} (x{vol['ratio']:.1f})\n"
        
        # Destek/Direnç
        sr = analysis.get("support_resistance")
        if sr:
            report += f"""
📍 <b>DESTEK / DİRENÇ</b>
• Direnç 1: ${sr['resistance1']:.6f}
• Direnç 2: ${sr['resistance2']:.6f}
• Destek 1: ${sr['support1']:.6f}
• Destek 2: ${sr['support2']:.6f}
"""
        
        # Skor
        scores = analysis.get("scores", {})
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━
{overall_emoji} <b>GENEL SİNYAL: {overall_text}</b>
📊 AL Skoru: {scores.get('buy', 0)} | SAT Skoru: {scores.get('sell', 0)}
"""
        
        # Hedef ve Stop
        if overall in ["STRONG_BUY", "BUY"]:
            target = ticker['price'] * 1.15
            stop = ticker['price'] * 0.92
            report += f"""
🎯 <b>HEDEF:</b> ${target:.6f} (+15%)
🛑 <b>STOP:</b> ${stop:.6f} (-8%)
"""
        
        report += """
━━━━━━━━━━━━━━━━━━━━━━━
🤖 <i>Detaylı Analiz - Akıllı Yatırım Asistanı</i>
"""
        return report
    
    def send_telegram_report(self, symbol: str):
        """Raporu Telegram'a gönder"""
        report = self.generate_report(symbol)
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': report,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            return True
        except:
            return False


if __name__ == "__main__":
    analyzer = DetailedAnalyzer()
    print(analyzer.generate_report("BTC"))
    print(analyzer.generate_report("ETH"))
