"""Database Modelleri - SQLite / PostgreSQL"""
import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_type="sqlite", db_path="broker.db"):
        self.db_type = db_type
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Veritabanını initialize et"""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Trades tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY,
                    broker TEXT,
                    symbol TEXT,
                    trade_type TEXT,
                    quantity REAL,
                    price REAL,
                    timestamp TEXT,
                    status TEXT
                )
            ''')
            
            # Users tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    created_at TEXT
                )
            ''')
            
            # Portfolio tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    symbol TEXT,
                    quantity REAL,
                    avg_price REAL,
                    updated_at TEXT
                )
            ''')
            
            # Logs tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Database initialized (SQLite)")
    
    def execute_query(self, query, params=()):
        """Query çalıştır"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        results = cursor.fetchall()
        conn.close()
        return results
    
    def add_trade(self, broker, symbol, trade_type, quantity, price):
        """Trade kaydet"""
        query = '''
            INSERT INTO trades (broker, symbol, trade_type, quantity, price, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (broker, symbol, trade_type, quantity, price, datetime.now().isoformat(), 'completed')
        self.execute_query(query, params)
        return "✅ Trade kaydedildi"
    
    def get_trades(self, limit=10):
        """Trade'leri al"""
        query = 'SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?'
        return self.execute_query(query, (limit,))

if __name__ == "__main__":
    db = DatabaseManager()
    print("✅ Database Manager Aktif")
