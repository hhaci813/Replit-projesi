"""
PORTFÖY TAKİP SİSTEMİ
Yatırımları takip et, kar/zarar hesapla, performans analizi yap
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

PORTFOLIO_FILE = "portfolio_data.json"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

class PortfolioTracker:
    def __init__(self):
        self.portfolio = self.load_portfolio()
    
    def load_portfolio(self) -> dict:
        """Portföyü yükle"""
        try:
            if os.path.exists(PORTFOLIO_FILE):
                with open(PORTFOLIO_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "holdings": [],
            "closed_positions": [],
            "total_invested": 0,
            "created_at": datetime.now().isoformat()
        }
    
    def save_portfolio(self):
        """Portföyü kaydet"""
        with open(PORTFOLIO_FILE, 'w') as f:
            json.dump(self.portfolio, f, indent=2, default=str)
    
    def add_position(self, symbol: str, amount_usd: float, 
                     entry_price: float = None, notes: str = ""):
        """Yeni pozisyon ekle"""
        if entry_price is None:
            entry_price = self.get_current_price(symbol)
        
        if entry_price <= 0:
            return None
        
        quantity = amount_usd / entry_price
        
        position = {
            "id": len(self.portfolio["holdings"]) + len(self.portfolio["closed_positions"]) + 1,
            "symbol": symbol.upper(),
            "entry_price": entry_price,
            "quantity": quantity,
            "amount_usd": amount_usd,
            "entry_date": datetime.now().isoformat(),
            "notes": notes,
            "status": "open"
        }
        
        self.portfolio["holdings"].append(position)
        self.portfolio["total_invested"] += amount_usd
        self.save_portfolio()
        
        return position
    
    def close_position(self, position_id: int, exit_price: float = None):
        """Pozisyon kapat"""
        for i, pos in enumerate(self.portfolio["holdings"]):
            if pos["id"] == position_id:
                if exit_price is None:
                    exit_price = self.get_current_price(pos["symbol"])
                
                # Kar/zarar hesapla
                exit_value = pos["quantity"] * exit_price
                entry_value = pos["amount_usd"]
                pnl = exit_value - entry_value
                pnl_percent = (pnl / entry_value) * 100
                
                # Kapatılan pozisyona ekle
                closed = {
                    **pos,
                    "exit_price": exit_price,
                    "exit_date": datetime.now().isoformat(),
                    "exit_value": exit_value,
                    "pnl": pnl,
                    "pnl_percent": pnl_percent,
                    "status": "closed"
                }
                
                self.portfolio["closed_positions"].append(closed)
                self.portfolio["holdings"].pop(i)
                self.save_portfolio()
                
                return closed
        return None
    
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
    
    def get_portfolio_value(self) -> dict:
        """Portföy değerini hesapla"""
        total_current = 0
        total_invested = 0
        positions = []
        
        for pos in self.portfolio["holdings"]:
            current_price = self.get_current_price(pos["symbol"])
            current_value = pos["quantity"] * current_price
            entry_value = pos["amount_usd"]
            pnl = current_value - entry_value
            pnl_percent = (pnl / entry_value) * 100 if entry_value > 0 else 0
            
            positions.append({
                "symbol": pos["symbol"],
                "quantity": pos["quantity"],
                "entry_price": pos["entry_price"],
                "current_price": current_price,
                "entry_value": entry_value,
                "current_value": current_value,
                "pnl": pnl,
                "pnl_percent": pnl_percent
            })
            
            total_current += current_value
            total_invested += entry_value
        
        total_pnl = total_current - total_invested
        total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "positions": positions,
            "total_invested": total_invested,
            "total_current": total_current,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "position_count": len(positions)
        }
    
    def get_performance_stats(self) -> dict:
        """Performans istatistikleri"""
        closed = self.portfolio["closed_positions"]
        
        if not closed:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_profit": 0,
                "total_loss": 0,
                "net_pnl": 0,
                "best_trade": None,
                "worst_trade": None
            }
        
        winning = [p for p in closed if p["pnl"] > 0]
        losing = [p for p in closed if p["pnl"] <= 0]
        
        total_profit = sum(p["pnl"] for p in winning)
        total_loss = sum(abs(p["pnl"]) for p in losing)
        
        best = max(closed, key=lambda x: x["pnl_percent"]) if closed else None
        worst = min(closed, key=lambda x: x["pnl_percent"]) if closed else None
        
        return {
            "total_trades": len(closed),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": len(winning) / len(closed) * 100 if closed else 0,
            "total_profit": total_profit,
            "total_loss": total_loss,
            "net_pnl": total_profit - total_loss,
            "best_trade": {
                "symbol": best["symbol"],
                "pnl_percent": best["pnl_percent"]
            } if best else None,
            "worst_trade": {
                "symbol": worst["symbol"],
                "pnl_percent": worst["pnl_percent"]
            } if worst else None
        }
    
    def generate_report(self) -> str:
        """Telegram için portföy raporu"""
        value = self.get_portfolio_value()
        stats = self.get_performance_stats()
        
        # Emoji seç
        if value["total_pnl"] > 0:
            pnl_emoji = "🟢"
            trend = "📈"
        elif value["total_pnl"] < 0:
            pnl_emoji = "🔴"
            trend = "📉"
        else:
            pnl_emoji = "⚪"
            trend = "➡️"
        
        report = f"""
📊 <b>PORTFÖY RAPORU</b>
━━━━━━━━━━━━━━━━━━━━━━━

💰 <b>ÖZET</b>
• Toplam Yatırım: ${value['total_invested']:.2f}
• Güncel Değer: ${value['total_current']:.2f}
• {pnl_emoji} Kar/Zarar: ${value['total_pnl']:+.2f} ({value['total_pnl_percent']:+.2f}%)
• Pozisyon Sayısı: {value['position_count']}

{trend} <b>AKTİF POZİSYONLAR</b>
"""
        
        for pos in value["positions"][:10]:
            emoji = "🟢" if pos["pnl"] > 0 else "🔴"
            report += f"""
• <b>{pos['symbol']}</b>
  Giriş: ${pos['entry_price']:.6f} → Şimdi: ${pos['current_price']:.6f}
  {emoji} {pos['pnl_percent']:+.2f}% (${pos['pnl']:+.2f})
"""
        
        if stats["total_trades"] > 0:
            report += f"""
━━━━━━━━━━━━━━━━━━━━━━━
📈 <b>PERFORMANS</b>
• Toplam İşlem: {stats['total_trades']}
• Kazanan: {stats['winning_trades']} | Kaybeden: {stats['losing_trades']}
• Başarı Oranı: %{stats['win_rate']:.1f}
• Net Kar: ${stats['net_pnl']:+.2f}
"""
            if stats["best_trade"]:
                report += f"• En İyi: {stats['best_trade']['symbol']} (+{stats['best_trade']['pnl_percent']:.1f}%)\n"
        
        report += "\n🤖 <i>Portföy Takip - Akıllı Yatırım Asistanı</i>"
        
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


if __name__ == "__main__":
    # Test
    tracker = PortfolioTracker()
    
    # Örnek pozisyonlar
    tracker.add_position("BTC", 100, 100000)
    tracker.add_position("ETH", 50, 3800)
    tracker.add_position("SPELL", 25, 0.000266)
    
    print(tracker.generate_report())
