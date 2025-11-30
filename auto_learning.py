"""Auto Learning - Geçmiş verilerden öğren, performansı iyileştir"""
from trade_history import TradeHistory
import pickle
import os

class AutoLearner:
    MODEL_FILE = "trading_model.pkl"
    
    @staticmethod
    def learn_from_history():
        """Geçmiş trade'lerden öğren"""
        try:
            # Win rate'i analiz et
            win_rate = TradeHistory.get_win_rate()
            
            # En iyi işlem gören symbolü bul
            symbols = ["BTC", "XRPTRY", "AAPL", "MSFT", "GOOGL", "ETH"]
            best_symbol = None
            best_win_rate = 0
            
            for sym in symbols:
                rate = TradeHistory.get_win_rate(sym)
                if rate > best_win_rate:
                    best_win_rate = rate
                    best_symbol = sym
            
            # Model yarat
            model = {
                'global_win_rate': win_rate,
                'best_symbol': best_symbol,
                'best_win_rate': best_win_rate,
                'learned_at': str(__import__('datetime').datetime.now())
            }
            
            # Model kayıt et
            with open(AutoLearner.MODEL_FILE, 'wb') as f:
                pickle.dump(model, f)
            
            return model
        except:
            return None
    
    @staticmethod
    def get_model():
        """Öğrenilen modeli yükle"""
        try:
            if os.path.exists(AutoLearner.MODEL_FILE):
                with open(AutoLearner.MODEL_FILE, 'rb') as f:
                    return pickle.load(f)
        except:
            pass
        return None
    
    @staticmethod
    def recommend_symbol():
        """En iyi symbolu öner"""
        model = AutoLearner.get_model()
        if model:
            return model.get('best_symbol', 'BTC')
        return 'BTC'
