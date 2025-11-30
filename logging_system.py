"""Logging Sistemi - Tüm İşlemlerin Kaydı"""
import logging
import json
from datetime import datetime
import os

class LoggingManager:
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Logging'i setup et"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = f"{log_dir}/broker_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def log_trade(self, broker, symbol, trade_type, quantity, price, status):
        """İşlemi kaydı"""
        self.logger.info(f"TRADE: {broker.upper()} {trade_type} {symbol} x{quantity} @ ${price} - {status}")
    
    def log_error(self, error_msg):
        """Hatayı kaydı"""
        self.logger.error(f"ERROR: {error_msg}")
    
    def log_alert(self, alert_msg):
        """Uyarı kaydı"""
        self.logger.warning(f"ALERT: {alert_msg}")
    
    def log_info(self, info_msg):
        """Bilgi kaydı"""
        self.logger.info(f"INFO: {info_msg}")
    
    def get_recent_logs(self, lines=20):
        """Son log'ları al"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return "Log dosyası yok"
        
        latest_log = max(
            [os.path.join(log_dir, f) for f in os.listdir(log_dir)],
            key=os.path.getctime
        )
        
        with open(latest_log, 'r') as f:
            all_lines = f.readlines()
        
        return ''.join(all_lines[-lines:])

if __name__ == "__main__":
    logger = LoggingManager()
    print("✅ Logging Manager Aktif")
