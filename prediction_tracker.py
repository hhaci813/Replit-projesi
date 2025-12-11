"""
Tahmin Takip Sistemi - Prediction Tracker
Tahminleri kaydeder, 10 gün sonra doğrular ve başarı oranı hesaplar
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import requests
import json

DB_PATH = "prediction_tracker.db"

class PredictionTracker:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Veritabanını ve tabloyu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                target_price REAL,
                target_percent REAL,
                source TEXT,
                reasoning TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                evaluation_at TIMESTAMP,
                resolved_at TIMESTAMP,
                exit_price REAL,
                result TEXT DEFAULT 'PENDING',
                outcome_pct REAL,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accuracy_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                total_predictions INTEGER,
                wins INTEGER,
                losses INTEGER,
                pending INTEGER,
                accuracy_pct REAL,
                avg_gain_pct REAL,
                avg_loss_pct REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_prediction(self, 
                       symbol: str, 
                       direction: str,
                       entry_price: float,
                       target_price: Optional[float] = None,
                       target_percent: Optional[float] = None,
                       source: str = "QUANTUM_SYSTEM",
                       reasoning: str = "",
                       evaluation_days: int = 10) -> int:
        """Yeni tahmin ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        created_at = datetime.now()
        evaluation_at = created_at + timedelta(days=evaluation_days)
        
        if target_percent and not target_price:
            if direction.upper() == "UP":
                target_price = entry_price * (1 + target_percent / 100)
            else:
                target_price = entry_price * (1 - target_percent / 100)
        
        cursor.execute('''
            INSERT INTO predictions 
            (symbol, direction, entry_price, target_price, target_percent, 
             source, reasoning, created_at, evaluation_at, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        ''', (symbol.upper(), direction.upper(), entry_price, target_price, 
              target_percent, source, reasoning, created_at, evaluation_at))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prediction_id
    
    def get_due_predictions(self) -> List[Dict]:
        """Değerlendirme zamanı gelmiş tahminleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute('''
            SELECT id, symbol, direction, entry_price, target_price, 
                   target_percent, source, reasoning, created_at, evaluation_at
            FROM predictions 
            WHERE result = 'PENDING' AND evaluation_at <= ?
        ''', (now,))
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            predictions.append({
                'id': row[0],
                'symbol': row[1],
                'direction': row[2],
                'entry_price': row[3],
                'target_price': row[4],
                'target_percent': row[5],
                'source': row[6],
                'reasoning': row[7],
                'created_at': row[8],
                'evaluation_at': row[9]
            })
        
        return predictions
    
    def get_pending_predictions(self) -> List[Dict]:
        """Bekleyen tüm tahminleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, symbol, direction, entry_price, target_price, 
                   target_percent, created_at, evaluation_at
            FROM predictions 
            WHERE result = 'PENDING'
            ORDER BY evaluation_at ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            days_left = (datetime.fromisoformat(row[7]) - datetime.now()).days
            predictions.append({
                'id': row[0],
                'symbol': row[1],
                'direction': row[2],
                'entry_price': row[3],
                'target_price': row[4],
                'target_percent': row[5],
                'created_at': row[6],
                'evaluation_at': row[7],
                'days_left': max(0, days_left)
            })
        
        return predictions
    
    def resolve_prediction(self, prediction_id: int, exit_price: float) -> Dict:
        """Tahmini değerlendir ve sonuçlandır"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, direction, entry_price, target_price
            FROM predictions WHERE id = ?
        ''', (prediction_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {'error': 'Prediction not found'}
        
        symbol, direction, entry_price, target_price = row
        
        outcome_pct = ((exit_price - entry_price) / entry_price) * 100
        
        if direction == 'UP':
            result = 'WIN' if exit_price > entry_price else 'LOSS'
        else:
            result = 'WIN' if exit_price < entry_price else 'LOSS'
        
        resolved_at = datetime.now()
        
        cursor.execute('''
            UPDATE predictions 
            SET exit_price = ?, result = ?, outcome_pct = ?, resolved_at = ?
            WHERE id = ?
        ''', (exit_price, result, outcome_pct, resolved_at, prediction_id))
        
        conn.commit()
        conn.close()
        
        return {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'outcome_pct': outcome_pct,
            'result': result
        }
    
    def evaluate_due_predictions(self) -> List[Dict]:
        """Zamanı gelen tahminleri BTCTurk fiyatlarıyla değerlendir"""
        due = self.get_due_predictions()
        if not due:
            return []
        
        try:
            resp = requests.get('https://api.btcturk.com/api/v2/ticker', timeout=15)
            tickers = {t['pair'].replace('TRY', ''): float(t['last']) 
                      for t in resp.json().get('data', []) if t['pair'].endswith('TRY')}
        except:
            return []
        
        results = []
        for pred in due:
            symbol = pred['symbol']
            if symbol in tickers:
                exit_price = tickers[symbol]
                result = self.resolve_prediction(pred['id'], exit_price)
                results.append(result)
        
        return results
    
    def get_stats(self) -> Dict:
        """Genel başarı istatistiklerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE result = 'WIN'")
        wins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE result = 'LOSS'")
        losses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE result = 'PENDING'")
        pending = cursor.fetchone()[0]
        
        resolved = wins + losses
        accuracy = (wins / resolved * 100) if resolved > 0 else 0
        
        cursor.execute("SELECT AVG(outcome_pct) FROM predictions WHERE result = 'WIN'")
        avg_win = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(outcome_pct) FROM predictions WHERE result = 'LOSS'")
        avg_loss = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT symbol, COUNT(*) as cnt, 
                   SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins
            FROM predictions 
            WHERE result != 'PENDING'
            GROUP BY symbol
            ORDER BY cnt DESC
            LIMIT 10
        ''')
        by_symbol = []
        for row in cursor.fetchall():
            symbol, cnt, sym_wins = row
            by_symbol.append({
                'symbol': symbol,
                'total': cnt,
                'wins': sym_wins,
                'accuracy': (sym_wins / cnt * 100) if cnt > 0 else 0
            })
        
        cursor.execute('''
            SELECT symbol, direction, entry_price, exit_price, outcome_pct, result, resolved_at
            FROM predictions
            WHERE result != 'PENDING'
            ORDER BY resolved_at DESC
            LIMIT 10
        ''')
        recent = []
        for row in cursor.fetchall():
            recent.append({
                'symbol': row[0],
                'direction': row[1],
                'entry_price': row[2],
                'exit_price': row[3],
                'outcome_pct': row[4],
                'result': row[5],
                'resolved_at': row[6]
            })
        
        conn.close()
        
        return {
            'total_predictions': total,
            'wins': wins,
            'losses': losses,
            'pending': pending,
            'resolved': resolved,
            'accuracy_pct': accuracy,
            'avg_win_pct': avg_win,
            'avg_loss_pct': avg_loss,
            'by_symbol': by_symbol,
            'recent_results': recent
        }
    
    def get_accuracy_report(self) -> str:
        """Telegram için formatlı başarı raporu"""
        stats = self.get_stats()
        pending = self.get_pending_predictions()
        
        report = f"""📊 <b>TAHMİN BAŞARI RAPORU</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}

📈 <b>GENEL İSTATİSTİKLER</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Toplam Tahmin: {stats['total_predictions']}
✅ Kazanan: {stats['wins']}
❌ Kaybeden: {stats['losses']}
⏳ Bekleyen: {stats['pending']}

🎯 <b>BAŞARI ORANI: %{stats['accuracy_pct']:.1f}</b>

💰 Ortalama Kazanç: +%{stats['avg_win_pct']:.2f}
📉 Ortalama Kayıp: %{stats['avg_loss_pct']:.2f}

"""
        
        if stats['by_symbol']:
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "📊 <b>COİN BAZLI BAŞARI</b>\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for s in stats['by_symbol'][:5]:
                emoji = '🟢' if s['accuracy'] >= 50 else '🔴'
                report += f"{emoji} {s['symbol']}: {s['wins']}/{s['total']} (%{s['accuracy']:.0f})\n"
            report += "\n"
        
        if stats['recent_results']:
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "🕐 <b>SON SONUÇLAR</b>\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for r in stats['recent_results'][:5]:
                emoji = '✅' if r['result'] == 'WIN' else '❌'
                dir_emoji = '📈' if r['direction'] == 'UP' else '📉'
                pct = f"+{r['outcome_pct']:.1f}%" if r['outcome_pct'] > 0 else f"{r['outcome_pct']:.1f}%"
                report += f"{emoji} {r['symbol']} {dir_emoji}: {pct}\n"
            report += "\n"
        
        if pending:
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "⏳ <b>BEKLEYEN TAHMİNLER</b>\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for p in pending[:5]:
                dir_emoji = '📈' if p['direction'] == 'UP' else '📉'
                report += f"{dir_emoji} {p['symbol']}: {p['days_left']} gün kaldı\n"
            report += "\n"
        
        report += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Quantum Sistem - Tahmin Takibi
"""
        
        return report


def send_accuracy_report():
    """Telegram'a başarı raporu gönder"""
    tracker = PredictionTracker()
    
    evaluated = tracker.evaluate_due_predictions()
    
    report = tracker.get_accuracy_report()
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        requests.post(url, json={
            'chat_id': chat_id, 
            'text': report, 
            'parse_mode': 'HTML'
        }, timeout=15)
    
    return {'evaluated': len(evaluated), 'report': report}


if __name__ == "__main__":
    tracker = PredictionTracker()
    
    print("Tahmin Takip Sistemi Aktif!")
    print(f"Veritabanı: {DB_PATH}")
    
    stats = tracker.get_stats()
    print(f"\nToplam Tahmin: {stats['total_predictions']}")
    print(f"Bekleyen: {stats['pending']}")
    print(f"Başarı Oranı: %{stats['accuracy_pct']:.1f}")
