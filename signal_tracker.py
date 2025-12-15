"""📊 SİNYAL PERFORMANS TAKİP SİSTEMİ
Verilen sinyallerin başarı oranını takip eder
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

SIGNALS_FILE = "signals_history.json"

class SignalTracker:
    def __init__(self):
        self.signals = self._load_signals()
    
    def _load_signals(self) -> List[Dict]:
        """Kayıtlı sinyalleri yükle"""
        if os.path.exists(SIGNALS_FILE):
            try:
                with open(SIGNALS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_signals(self):
        """Sinyalleri kaydet"""
        with open(SIGNALS_FILE, 'w') as f:
            json.dump(self.signals, f, indent=2, ensure_ascii=False)
    
    def add_signal(self, symbol: str, signal_type: str, price: float, 
                   target_percent: float = 10, stop_percent: float = -8) -> Dict:
        """Yeni sinyal ekle"""
        signal = {
            "id": len(self.signals) + 1,
            "symbol": symbol.upper(),
            "signal_type": signal_type,
            "entry_price": price,
            "target_percent": target_percent,
            "stop_percent": stop_percent,
            "target_price": price * (1 + target_percent / 100),
            "stop_price": price * (1 + stop_percent / 100),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "ACTIVE",
            "result": None,
            "result_percent": None,
            "closed_at": None
        }
        self.signals.append(signal)
        self._save_signals()
        return signal
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """BTCTurk'ten güncel fiyat al"""
        try:
            resp = requests.get('https://api.btcturk.com/api/v2/ticker', timeout=10)
            for t in resp.json().get('data', []):
                if t.get('pairNormalized') == f"{symbol}_TRY":
                    return float(t.get('last', 0))
        except:
            pass
        return None
    
    def check_signals(self) -> List[Dict]:
        """Aktif sinyalleri kontrol et ve sonuçları güncelle"""
        updated = []
        for signal in self.signals:
            if signal["status"] != "ACTIVE":
                continue
            
            current_price = self.get_current_price(signal["symbol"])
            if not current_price:
                continue
            
            entry_price = signal["entry_price"]
            change_percent = ((current_price - entry_price) / entry_price) * 100
            
            if change_percent >= signal["target_percent"]:
                signal["status"] = "WIN"
                signal["result"] = "HEDEF"
                signal["result_percent"] = round(change_percent, 2)
                signal["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                updated.append(signal)
            elif change_percent <= signal["stop_percent"]:
                signal["status"] = "LOSS"
                signal["result"] = "STOP"
                signal["result_percent"] = round(change_percent, 2)
                signal["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                updated.append(signal)
            
            signal_time = datetime.strptime(signal["timestamp"], "%Y-%m-%d %H:%M")
            if datetime.now() - signal_time > timedelta(days=7):
                signal["status"] = "EXPIRED"
                signal["result"] = "SÜRE DOLDU"
                signal["result_percent"] = round(change_percent, 2)
                signal["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                updated.append(signal)
        
        self._save_signals()
        return updated
    
    def get_performance_stats(self) -> Dict:
        """Performans istatistiklerini hesapla"""
        total = len(self.signals)
        if total == 0:
            return {
                "total_signals": 0,
                "active": 0,
                "wins": 0,
                "losses": 0,
                "expired": 0,
                "win_rate": 0,
                "avg_profit": 0,
                "total_profit": 0
            }
        
        active = sum(1 for s in self.signals if s["status"] == "ACTIVE")
        wins = sum(1 for s in self.signals if s["status"] == "WIN")
        losses = sum(1 for s in self.signals if s["status"] == "LOSS")
        expired = sum(1 for s in self.signals if s["status"] == "EXPIRED")
        
        closed = [s for s in self.signals if s["status"] != "ACTIVE"]
        total_profit = sum(s.get("result_percent", 0) or 0 for s in closed)
        avg_profit = total_profit / len(closed) if closed else 0
        
        completed = wins + losses
        win_rate = (wins / completed * 100) if completed > 0 else 0
        
        return {
            "total_signals": total,
            "active": active,
            "wins": wins,
            "losses": losses,
            "expired": expired,
            "win_rate": round(win_rate, 1),
            "avg_profit": round(avg_profit, 2),
            "total_profit": round(total_profit, 2)
        }
    
    def get_active_signals(self) -> List[Dict]:
        """Aktif sinyalleri getir"""
        active = []
        for signal in self.signals:
            if signal["status"] == "ACTIVE":
                current_price = self.get_current_price(signal["symbol"])
                if current_price:
                    change = ((current_price - signal["entry_price"]) / signal["entry_price"]) * 100
                    signal["current_price"] = current_price
                    signal["current_change"] = round(change, 2)
                active.append(signal)
        return active
    
    def get_recent_results(self, limit: int = 10) -> List[Dict]:
        """Son sonuçları getir"""
        closed = [s for s in self.signals if s["status"] != "ACTIVE"]
        return sorted(closed, key=lambda x: x.get("closed_at", ""), reverse=True)[:limit]
    
    def format_performance_message(self) -> str:
        """Telegram için performans mesajı oluştur"""
        stats = self.get_performance_stats()
        active = self.get_active_signals()
        recent = self.get_recent_results(5)
        
        msg = "📊 <b>SİNYAL PERFORMANS RAPORU</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        if stats["win_rate"] >= 70:
            emoji = "🏆"
        elif stats["win_rate"] >= 50:
            emoji = "📈"
        else:
            emoji = "📉"
        
        msg += f"{emoji} <b>BAŞARI ORANI: %{stats['win_rate']}</b>\n\n"
        msg += f"📋 Toplam Sinyal: {stats['total_signals']}\n"
        msg += f"✅ Kazanan: {stats['wins']}\n"
        msg += f"❌ Kaybeden: {stats['losses']}\n"
        msg += f"⏰ Süresi Dolan: {stats['expired']}\n"
        msg += f"🔄 Aktif: {stats['active']}\n"
        msg += f"💰 Ort. Kar/Zarar: %{stats['avg_profit']}\n"
        msg += f"📊 Toplam: %{stats['total_profit']}\n"
        
        if active:
            msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += "🔄 <b>AKTİF SİNYALLER:</b>\n\n"
            for s in active[:5]:
                change = s.get('current_change', 0)
                emoji = "🟢" if change > 0 else "🔴"
                msg += f"{emoji} <b>{s['symbol']}</b>\n"
                msg += f"   Giriş: ₺{s['entry_price']:,.4f}\n"
                msg += f"   Şuan: ₺{s.get('current_price', 0):,.4f} ({change:+.2f}%)\n"
                msg += f"   Hedef: %+{s['target_percent']} | Stop: %{s['stop_percent']}\n\n"
        
        if recent:
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += "📜 <b>SON SONUÇLAR:</b>\n\n"
            for s in recent:
                if s['status'] == 'WIN':
                    emoji = "✅"
                elif s['status'] == 'LOSS':
                    emoji = "❌"
                else:
                    emoji = "⏰"
                msg += f"{emoji} {s['symbol']}: {s['result']} ({s['result_percent']:+.2f}%)\n"
        
        return msg
    
    def auto_record_signals(self, rising_cryptos: List[Dict], potential_cryptos: List[Dict]):
        """
        Otomatik olarak verilen sinyalleri kaydet
        GELİŞMİŞ FİLTRELEME: Sadece güçlü sinyalleri kaydet
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        existing_today = [s for s in self.signals 
                        if s["timestamp"].startswith(today)]
        existing_symbols = [s["symbol"] for s in existing_today]
        
        for crypto in rising_cryptos[:3]:
            symbol = crypto.get('symbol', '')
            if symbol and symbol not in existing_symbols:
                rec = crypto.get('rec', 'BUY')
                pump_score = crypto.get('pump_score', 0)
                rsi = crypto.get('rsi', 50)
                channel_position = crypto.get('channel_position', 50)
                
                if rec not in ['STRONG_BUY', 'AL']:
                    continue
                
                if pump_score < 50:
                    continue
                
                if rsi > 70:
                    continue
                
                if channel_position > 85:
                    continue
                
                self.add_signal(
                    symbol=symbol,
                    signal_type=rec,
                    price=crypto.get('price', 0),
                    target_percent=12,
                    stop_percent=-5
                )
                existing_symbols.append(symbol)
        
        for crypto in potential_cryptos[:2]:
            symbol = crypto.get('symbol', '')
            if symbol and symbol not in existing_symbols:
                score = crypto.get('score', 0)
                
                if score < 50:
                    continue
                
                self.add_signal(
                    symbol=symbol,
                    signal_type="POTENTIAL",
                    price=crypto.get('price', 0),
                    target_percent=min(crypto.get('potential', 15), 20),
                    stop_percent=-7
                )
                existing_symbols.append(symbol)

signal_tracker = SignalTracker()
