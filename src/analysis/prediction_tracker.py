"""
Prediction Tracker - Tahmin Doğruluk Takibi
- Her tahmini kaydet
- 24 saat sonra doğruluğunu kontrol et
- İstatistikleri raporla
"""

import json
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

PREDICTIONS_FILE = "data/predictions.json"

class PredictionTracker:
    def __init__(self):
        self.predictions = []
        self.load_predictions()
    
    def load_predictions(self):
        """Kayıtlı tahminleri yükle"""
        try:
            os.makedirs("data", exist_ok=True)
            if os.path.exists(PREDICTIONS_FILE):
                with open(PREDICTIONS_FILE, 'r') as f:
                    self.predictions = json.load(f)
        except Exception as e:
            logger.error(f"Predictions load error: {e}")
            self.predictions = []
    
    def save_predictions(self):
        """Tahminleri kaydet"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(PREDICTIONS_FILE, 'w') as f:
                json.dump(self.predictions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Predictions save error: {e}")
    
    def add_prediction(self, symbol, price_at_prediction, signal, score, target_change=5):
        """Yeni tahmin ekle"""
        prediction = {
            'id': len(self.predictions) + 1,
            'symbol': symbol,
            'signal': signal,  # STRONG_BUY, BUY, SELL, etc.
            'score': score,
            'price_at_prediction': price_at_prediction,
            'target_change': target_change,  # Beklenen % değişim
            'timestamp': datetime.now().isoformat(),
            'check_after': (datetime.now() + timedelta(hours=24)).isoformat(),
            'verified': False,
            'result': None,  # 'correct' veya 'wrong'
            'actual_change': None
        }
        
        self.predictions.append(prediction)
        self.save_predictions()
        
        return prediction
    
    def verify_prediction(self, pred_id, current_price):
        """Tahmini doğrula"""
        for pred in self.predictions:
            if pred['id'] == pred_id and not pred['verified']:
                original_price = pred['price_at_prediction']
                actual_change = (current_price - original_price) / original_price * 100
                
                pred['actual_change'] = actual_change
                pred['verified'] = True
                pred['verified_at'] = datetime.now().isoformat()
                pred['final_price'] = current_price
                
                # Doğruluk kontrolü
                if pred['signal'] in ['STRONG_BUY', 'BUY']:
                    # Yükseliş tahmini
                    pred['result'] = 'correct' if actual_change > 0 else 'wrong'
                elif pred['signal'] in ['SELL', 'AVOID']:
                    # Düşüş tahmini
                    pred['result'] = 'correct' if actual_change < 0 else 'wrong'
                else:
                    # Nötr tahminler
                    pred['result'] = 'correct' if abs(actual_change) < 5 else 'partial'
                
                self.save_predictions()
                return pred
        
        return None
    
    def get_pending_verifications(self):
        """Doğrulanmayı bekleyen tahminler"""
        now = datetime.now()
        pending = []
        
        for pred in self.predictions:
            if not pred['verified']:
                check_time = datetime.fromisoformat(pred['check_after'])
                if now >= check_time:
                    pending.append(pred)
        
        return pending
    
    def get_accuracy_stats(self, days=7):
        """Son N gün için doğruluk istatistikleri"""
        cutoff = datetime.now() - timedelta(days=days)
        
        verified = [p for p in self.predictions 
                   if p['verified'] and 
                   datetime.fromisoformat(p['timestamp']) > cutoff]
        
        if not verified:
            return {'accuracy': 0, 'total': 0, 'correct': 0, 'wrong': 0}
        
        correct = len([p for p in verified if p['result'] == 'correct'])
        wrong = len([p for p in verified if p['result'] == 'wrong'])
        
        total = correct + wrong
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Sinyal tipine göre
        buy_signals = [p for p in verified if p['signal'] in ['STRONG_BUY', 'BUY']]
        sell_signals = [p for p in verified if p['signal'] in ['SELL', 'AVOID']]
        
        buy_accuracy = 0
        if buy_signals:
            buy_correct = len([p for p in buy_signals if p['result'] == 'correct'])
            buy_accuracy = buy_correct / len(buy_signals) * 100
        
        sell_accuracy = 0
        if sell_signals:
            sell_correct = len([p for p in sell_signals if p['result'] == 'correct'])
            sell_accuracy = sell_correct / len(sell_signals) * 100
        
        return {
            'accuracy': round(accuracy, 1),
            'total': total,
            'correct': correct,
            'wrong': wrong,
            'buy_accuracy': round(buy_accuracy, 1),
            'sell_accuracy': round(sell_accuracy, 1),
            'period_days': days
        }
    
    def get_recent_predictions(self, limit=10):
        """Son tahminleri getir"""
        sorted_preds = sorted(self.predictions, 
                             key=lambda x: x['timestamp'], 
                             reverse=True)
        return sorted_preds[:limit]
    
    def cleanup_old(self, days=30):
        """Eski tahminleri temizle"""
        cutoff = datetime.now() - timedelta(days=days)
        self.predictions = [p for p in self.predictions 
                          if datetime.fromisoformat(p['timestamp']) > cutoff]
        self.save_predictions()


prediction_tracker = PredictionTracker()
