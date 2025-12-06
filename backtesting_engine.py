"""
GELİŞMİŞ BACKTESTING ENGINE
Geçmiş önerilerin performansını analiz et, strateji başarı oranını hesapla
Real-time öneri takibi ve sonuç kaydı
"""

import os
import json
import requests
from datetime import datetime, timedelta

BACKTESTING_FILE = "backtesting_results.json"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

class BacktestingEngine:
    def __init__(self):
        self.results = self.load_results()
    
    def load_results(self) -> dict:
        """Sonuçları yükle"""
        try:
            if os.path.exists(BACKTESTING_FILE):
                with open(BACKTESTING_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "recommendations": [],
            "completed": [],
            "summary": {}
        }
    
    def save_results(self):
        """Sonuçları kaydet"""
        with open(BACKTESTING_FILE, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
    
    def record_recommendation(self, symbol: str, action: str, 
                               entry_price: float, target_price: float,
                               stop_loss: float, confidence: float):
        """Yeni öneri kaydet"""
        rec = {
            "id": len(self.results["recommendations"]) + 1,
            "symbol": symbol.upper(),
            "action": action,
            "entry_price": entry_price,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "result": None
        }
        self.results["recommendations"].append(rec)
        self.save_results()
        return rec
    
    def get_current_price(self, symbol: str) -> float:
        """Güncel fiyat al"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
            data = resp.json().get('data', [])
            
            for ticker in data:
                pair = ticker.get('pairNormalized', '')
                if pair == f"{symbol}_USDT":
                    return float(ticker.get('last', 0))
            return 0
        except:
            return 0
    
    def check_recommendations(self):
        """Aktif önerileri kontrol et"""
        active = [r for r in self.results["recommendations"] if r["status"] == "active"]
        
        for rec in active:
            current = self.get_current_price(rec["symbol"])
            if current <= 0:
                continue
            
            entry = rec.get("entry_price", current)
            
            # Hedef kontrolü
            if current >= rec["target_price"]:
                rec["status"] = "completed"
                rec["result"] = "WIN"
                rec["exit_price"] = current
                rec["exit_date"] = datetime.now().isoformat()
                rec["pnl_percent"] = ((current - entry) / entry) * 100
                self.results["completed"].append(rec)
            
            # Stop loss kontrolü
            elif current <= rec["stop_loss"]:
                rec["status"] = "completed"
                rec["result"] = "LOSS"
                rec["exit_price"] = current
                rec["exit_date"] = datetime.now().isoformat()
                rec["pnl_percent"] = ((current - entry) / entry) * 100
                self.results["completed"].append(rec)
            
            # Zaman aşımı (14 gün)
            try:
                created = datetime.fromisoformat(rec["created_at"])
                if datetime.now() - created > timedelta(days=14):
                    rec["status"] = "expired"
                    rec["result"] = "EXPIRED"
                    rec["exit_price"] = current
                    rec["exit_date"] = datetime.now().isoformat()
                    rec["pnl_percent"] = ((current - entry) / entry) * 100
                    self.results["completed"].append(rec)
            except:
                pass
        
        self.save_results()
        return self.get_statistics()
    
    def get_statistics(self) -> dict:
        """İstatistikleri hesapla"""
        completed = self.results["completed"]
        
        if not completed:
            return {
                "total_recommendations": len(self.results["recommendations"]),
                "active": len([r for r in self.results["recommendations"] if r.get("status") == "active"]),
                "completed": 0,
                "win_rate": 0,
                "avg_profit": 0,
                "avg_loss": 0,
                "best_trade": None,
                "worst_trade": None
            }
        
        wins = [r for r in completed if r.get("result") == "WIN"]
        losses = [r for r in completed if r.get("result") == "LOSS"]
        
        avg_profit = sum(r.get("pnl_percent", 0) for r in wins) / len(wins) if wins else 0
        avg_loss = sum(r.get("pnl_percent", 0) for r in losses) / len(losses) if losses else 0
        
        all_pnl = [r for r in completed if r.get("pnl_percent") is not None]
        best = max(all_pnl, key=lambda x: x.get("pnl_percent", 0)) if all_pnl else None
        worst = min(all_pnl, key=lambda x: x.get("pnl_percent", 0)) if all_pnl else None
        
        win_rate = len(wins) / len(completed) * 100 if completed else 0
        
        # Profit factor
        total_profit = sum(r.get("pnl_percent", 0) for r in wins) if wins else 0
        total_loss = abs(sum(r.get("pnl_percent", 0) for r in losses)) if losses else 1
        profit_factor = total_profit / total_loss if total_loss > 0 else total_profit
        
        return {
            "total_recommendations": len(self.results["recommendations"]),
            "active": len([r for r in self.results["recommendations"] if r.get("status") == "active"]),
            "completed": len(completed),
            "wins": len(wins),
            "losses": len(losses),
            "expired": len([r for r in completed if r.get("result") == "EXPIRED"]),
            "win_rate": win_rate,
            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "best_trade": {
                "symbol": best["symbol"],
                "pnl": best.get("pnl_percent", 0)
            } if best else None,
            "worst_trade": {
                "symbol": worst["symbol"],
                "pnl": worst.get("pnl_percent", 0)
            } if worst else None
        }
    
    def backtest_strategy(self, symbol: str, initial_capital: float = 10000, days: int = 30) -> dict:
        """RSI stratejisini backtest et"""
        prices = self._get_historical_prices(symbol, days)
        
        if not prices or len(prices) < 14:
            return None
        
        cash = initial_capital
        shares = 0
        trades = []
        portfolio_values = [initial_capital]
        
        for i in range(14, len(prices)):
            price = prices[i]
            if not price or price <= 0:
                continue
            
            rsi = self._calculate_rsi(prices[:i+1], 14)
            
            if rsi < 30 and shares == 0 and cash >= price:
                buy_shares = cash * 0.8 / price
                if buy_shares > 0:
                    cash -= buy_shares * price
                    shares = buy_shares
                    trades.append({'type': 'BUY', 'price': price, 'shares': buy_shares})
            
            elif rsi > 70 and shares > 0:
                cash += shares * price
                trades.append({'type': 'SELL', 'price': price, 'shares': shares})
                shares = 0
            
            portfolio_val = cash + (shares * price)
            portfolio_values.append(portfolio_val)
        
        final_value = cash + (shares * prices[-1]) if shares > 0 else cash
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        
        buy_prices = [t['price'] for t in trades if t['type'] == 'BUY']
        sell_prices = [t['price'] for t in trades if t['type'] == 'SELL']
        win_count = sum(1 for i, bp in enumerate(buy_prices) if i < len(sell_prices) and sell_prices[i] > bp)
        win_rate = (win_count / len(buy_prices)) * 100 if buy_prices else 0
        
        return {
            'symbol': symbol,
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return_pct': total_return,
            'total_trades': len(trades),
            'win_rate_pct': win_rate,
            'max_drawdown': self._calculate_max_drawdown(portfolio_values)
        }
    
    def _get_historical_prices(self, symbol: str, days: int) -> list:
        """BTCTurk'ten tarihçe al"""
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
                return [float(x) for x in data['c']]
        except:
            pass
        
        return []
    
    def _calculate_rsi(self, prices: list, period: int = 14) -> float:
        """RSI hesapla"""
        if len(prices) < period:
            return 50
        
        prices = prices[-period:]
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = sum(max(d, 0) for d in deltas) / len(deltas)
        losses = sum(max(-d, 0) for d in deltas) / len(deltas)
        
        if losses == 0:
            return 100
        
        rs = gains / losses
        return 100 - (100 / (1 + rs))
    
    def _calculate_max_drawdown(self, values: list) -> float:
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
    
    def generate_report(self) -> str:
        """Backtesting raporu"""
        stats = self.get_statistics()
        
        if stats["win_rate"] >= 70:
            grade = "🏆 MÜKEMMEL"
            color = "🟢"
        elif stats["win_rate"] >= 50:
            grade = "✅ İYİ"
            color = "🟡"
        else:
            grade = "⚠️ GELİŞTİRİLMELİ"
            color = "🔴"
        
        report = f"""
📊 <b>BACKTESTING RAPORU</b>
━━━━━━━━━━━━━━━━━━━━━━━

{color} <b>GENEL PERFORMANS</b>
• Toplam Öneri: {stats['total_recommendations']}
• Aktif: {stats['active']}
• Tamamlanan: {stats['completed']}

🎯 <b>SONUÇLAR</b>
• Kazanan: {stats.get('wins', 0)} ✅
• Kaybeden: {stats.get('losses', 0)} ❌
• Süresi Dolan: {stats.get('expired', 0)} ⏰

📈 <b>BAŞARI ORANI: %{stats['win_rate']:.1f}</b>
{grade}

💰 <b>ORTALAMALAR</b>
• Ortalama Kar: +{stats['avg_profit']:.1f}%
• Ortalama Zarar: {stats['avg_loss']:.1f}%
• Profit Factor: {stats.get('profit_factor', 0):.2f}
"""
        
        if stats.get("best_trade"):
            report += f"\n🏆 <b>EN İYİ:</b> {stats['best_trade']['symbol']} (+{stats['best_trade']['pnl']:.1f}%)"
        
        if stats.get("worst_trade"):
            report += f"\n📉 <b>EN KÖTÜ:</b> {stats['worst_trade']['symbol']} ({stats['worst_trade']['pnl']:.1f}%)"
        
        report += """

━━━━━━━━━━━━━━━━━━━━━━━
🤖 <i>Backtesting - Akıllı Yatırım Asistanı</i>
"""
        return report
    
    def send_telegram_report(self):
        """Raporu Telegram'a gönder"""
        report = self.generate_report()
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


def auto_record_recommendations(recommendations: list):
    """Önerilerden otomatik kayıt"""
    engine = BacktestingEngine()
    
    for rec in recommendations:
        if rec.get('action') in ['STRONG_BUY', 'BUY']:
            engine.record_recommendation(
                symbol=rec['symbol'],
                action=rec['action'],
                entry_price=rec.get('price', 0),
                target_price=rec.get('target_price', rec.get('price', 0) * 1.25),
                stop_loss=rec.get('stop_loss', rec.get('price', 0) * 0.92),
                confidence=rec.get('confidence', 70)
            )
    
    return engine.get_statistics()


if __name__ == "__main__":
    engine = BacktestingEngine()
    print(engine.generate_report())
