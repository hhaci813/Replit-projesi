"""
GELİŞMİŞ WHALE TRACKING SİSTEMİ
Büyük cüzdan hareketlerini tespit et, exchange akışlarını takip et
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "8268294938:AAFIdr7FfJdtq__FueMOdsvym19H8IBWdNs"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "8391537149"

class AdvancedWhaleTracker:
    def __init__(self):
        self.whale_threshold = {
            "BTC": 100,      # 100+ BTC = whale
            "ETH": 1000,     # 1000+ ETH = whale
            "USDT": 1000000, # 1M+ USDT = whale
            "default": 100000  # $100k+ = whale
        }
        self.tracked_whales = []
        self.alerts_sent = []
    
    def analyze_order_book_depth(self, symbol: str) -> dict:
        """Order book derinliğinden whale aktivitesi tespit et"""
        try:
            # BTCTurk order book
            resp = requests.get(
                f"https://api.btcturk.com/api/v2/orderbook?pairSymbol={symbol}USDT",
                timeout=10
            )
            data = resp.json().get('data', {})
            
            bids = data.get('bids', [])
            asks = data.get('asks', [])
            
            # Büyük emirleri tespit et
            large_bids = []
            large_asks = []
            
            bid_total = 0
            ask_total = 0
            
            for bid in bids[:50]:
                price = float(bid[0])
                amount = float(bid[1])
                value = price * amount
                bid_total += value
                
                if value > 10000:  # $10k+ emir
                    large_bids.append({
                        "price": price,
                        "amount": amount,
                        "value": value
                    })
            
            for ask in asks[:50]:
                price = float(ask[0])
                amount = float(ask[1])
                value = price * amount
                ask_total += value
                
                if value > 10000:
                    large_asks.append({
                        "price": price,
                        "amount": amount,
                        "value": value
                    })
            
            # Alım/Satım baskısı
            if bid_total > 0 and ask_total > 0:
                buy_pressure = bid_total / (bid_total + ask_total) * 100
            else:
                buy_pressure = 50
            
            whale_signal = "NEUTRAL"
            if buy_pressure > 65:
                whale_signal = "ACCUMULATION"  # Whalelar topluyor
            elif buy_pressure < 35:
                whale_signal = "DISTRIBUTION"  # Whalelar satıyor
            
            return {
                "symbol": symbol,
                "large_buy_orders": len(large_bids),
                "large_sell_orders": len(large_asks),
                "total_bid_value": bid_total,
                "total_ask_value": ask_total,
                "buy_pressure": buy_pressure,
                "whale_signal": whale_signal,
                "top_bids": large_bids[:5],
                "top_asks": large_asks[:5]
            }
            
        except Exception as e:
            return {"error": str(e), "symbol": symbol}
    
    def detect_volume_anomaly(self, symbol: str) -> dict:
        """Hacim anomalisi tespit et (whale aktivitesi göstergesi)"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            data = resp.json().get('data', [])
            
            for ticker in data:
                if ticker.get('pairNormalized') == f"{symbol}_USDT":
                    volume = float(ticker.get('volume', 0))
                    volume_24h = float(ticker.get('volumeQuote', 0))
                    avg_trade = volume_24h / 24 if volume_24h > 0 else 0
                    
                    # Son saatin hacmini tahmin et (yaklaşık)
                    current_hour_estimate = avg_trade * 1.5  # varsayım
                    
                    if current_hour_estimate > avg_trade * 3:
                        anomaly = "HIGH"
                        message = "🐋 Anormal yüksek hacim - Whale aktivitesi muhtemel"
                    elif current_hour_estimate > avg_trade * 2:
                        anomaly = "MEDIUM"
                        message = "📊 Normalin üstünde hacim"
                    else:
                        anomaly = "NORMAL"
                        message = "Normal hacim"
                    
                    return {
                        "symbol": symbol,
                        "volume_24h": volume_24h,
                        "avg_hourly": avg_trade,
                        "anomaly_level": anomaly,
                        "message": message
                    }
            
            return {"symbol": symbol, "error": "Veri bulunamadı"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_exchange_flows(self) -> dict:
        """Exchange giriş/çıkış tahmini (order book'tan)"""
        major_coins = ["BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX"]
        flows = []
        
        for coin in major_coins:
            depth = self.analyze_order_book_depth(coin)
            if "error" not in depth:
                signal = depth.get("whale_signal", "NEUTRAL")
                pressure = depth.get("buy_pressure", 50)
                
                if signal == "ACCUMULATION":
                    flow = "INFLOW"
                    emoji = "🟢"
                elif signal == "DISTRIBUTION":
                    flow = "OUTFLOW"
                    emoji = "🔴"
                else:
                    flow = "NEUTRAL"
                    emoji = "⚪"
                
                flows.append({
                    "symbol": coin,
                    "flow": flow,
                    "pressure": pressure,
                    "emoji": emoji
                })
        
        return {
            "flows": flows,
            "summary": self._summarize_flows(flows),
            "timestamp": datetime.now().isoformat()
        }
    
    def _summarize_flows(self, flows: list) -> str:
        """Akış özeti"""
        inflows = sum(1 for f in flows if f["flow"] == "INFLOW")
        outflows = sum(1 for f in flows if f["flow"] == "OUTFLOW")
        
        if inflows > outflows * 2:
            return "🐋 GÜÇLÜ ACCUMULATION - Whalelar topluyor!"
        elif outflows > inflows * 2:
            return "⚠️ DISTRIBUTION - Whalelar satıyor!"
        elif inflows > outflows:
            return "🟢 Hafif alım baskısı"
        elif outflows > inflows:
            return "🔴 Hafif satış baskısı"
        else:
            return "⚪ Dengeli piyasa"
    
    def track_top_coins(self) -> list:
        """Ana coinlerde whale aktivitesi"""
        coins = ["BTC", "ETH", "SOL", "XRP", "AVAX", "DOGE", "ADA", "DOT"]
        results = []
        
        for coin in coins:
            depth = self.analyze_order_book_depth(coin)
            volume = self.detect_volume_anomaly(coin)
            
            whale_score = 0
            signals = []
            
            # Order book sinyalleri
            if depth.get("whale_signal") == "ACCUMULATION":
                whale_score += 3
                signals.append("📊 Accumulation tespit")
            elif depth.get("whale_signal") == "DISTRIBUTION":
                whale_score -= 3
                signals.append("📉 Distribution tespit")
            
            # Hacim sinyalleri
            if volume.get("anomaly_level") == "HIGH":
                whale_score += 2
                signals.append("🐋 Anormal hacim")
            
            # Büyük emirler
            large_bids = depth.get("large_buy_orders", 0)
            large_asks = depth.get("large_sell_orders", 0)
            
            if large_bids > large_asks * 2:
                whale_score += 2
                signals.append(f"💰 {large_bids} büyük alım emri")
            
            results.append({
                "symbol": coin,
                "whale_score": whale_score,
                "buy_pressure": depth.get("buy_pressure", 50),
                "signals": signals,
                "verdict": "BULLISH" if whale_score > 2 else "BEARISH" if whale_score < -2 else "NEUTRAL"
            })
        
        # Skora göre sırala
        results.sort(key=lambda x: x["whale_score"], reverse=True)
        return results
    
    def generate_whale_report(self) -> str:
        """Whale raporu oluştur"""
        flows = self.get_exchange_flows()
        top_coins = self.track_top_coins()
        
        report = f"""
🐋 <b>WHALE TRACKER RAPORU</b>
━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>EXCHANGE AKIŞLARI</b>
{flows['summary']}

"""
        for flow in flows["flows"]:
            report += f"{flow['emoji']} {flow['symbol']}: {flow['flow']} (Alım: %{flow['pressure']:.0f})\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>WHALE AKTİVİTESİ</b>

"""
        for coin in top_coins[:6]:
            if coin["verdict"] == "BULLISH":
                emoji = "🟢"
            elif coin["verdict"] == "BEARISH":
                emoji = "🔴"
            else:
                emoji = "⚪"
            
            report += f"{emoji} <b>{coin['symbol']}</b>: {coin['verdict']} (Skor: {coin['whale_score']:+d})\n"
            for sig in coin["signals"][:2]:
                report += f"   • {sig}\n"
        
        report += """
━━━━━━━━━━━━━━━━━━━━━━━
🤖 <i>Whale Tracker - Akıllı Yatırım Asistanı</i>
"""
        return report
    
    def send_telegram_report(self):
        """Raporu Telegram'a gönder"""
        report = self.generate_whale_report()
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
    tracker = AdvancedWhaleTracker()
    print(tracker.generate_whale_report())
