"""Trade History - Geçmiş işlemleri kayıt ve öğren"""
import sqlite3
import json
from datetime import datetime

class TradeHistory:
    DB_FILE = "trade_history.db"
    
    @staticmethod
    def init_db():
        """Database oluştur"""
        conn = sqlite3.connect(TradeHistory.DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades
                     (id INTEGER PRIMARY KEY,
                      timestamp TEXT,
                      symbol TEXT,
                      action TEXT,
                      price REAL,
                      signal TEXT,
                      rsi REAL,
                      result TEXT)''')
        conn.commit()
        conn.close()
    
    @staticmethod
    def log_trade(symbol, action, price, signal, rsi, result="pending"):
        """İşlemi kayıt et"""
        try:
            conn = sqlite3.connect(TradeHistory.DB_FILE)
            c = conn.cursor()
            c.execute('''INSERT INTO trades 
                        (timestamp, symbol, action, price, signal, rsi, result)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (datetime.now().isoformat(), symbol, action, price, signal, rsi, result))
            conn.commit()
            conn.close()
        except:
            pass
    
    @staticmethod
    def get_win_rate(symbol=None):
        """Başarı oranı hesapla"""
        try:
            conn = sqlite3.connect(TradeHistory.DB_FILE)
            c = conn.cursor()
            
            if symbol:
                c.execute("SELECT COUNT(*) FROM trades WHERE symbol=? AND result='win'", (symbol,))
                wins = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM trades WHERE symbol=?", (symbol,))
                total = c.fetchone()[0]
            else:
                c.execute("SELECT COUNT(*) FROM trades WHERE result='win'")
                wins = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM trades")
                total = c.fetchone()[0]
            
            conn.close()
            
            if total == 0:
                return 0
            return (wins / total) * 100
        except:
            return 0
    
    @staticmethod
    def get_stats(symbol):
        """İstatistikler"""
        try:
            conn = sqlite3.connect(TradeHistory.DB_FILE)
            c = conn.cursor()
            c.execute("SELECT COUNT(*), AVG(rsi), MAX(price), MIN(price) FROM trades WHERE symbol=?", (symbol,))
            result = c.fetchone()
            conn.close()
            
            return {
                'total_trades': result[0],
                'avg_rsi': result[1],
                'max_price': result[2],
                'min_price': result[3]
            }
        except:
            return {}
