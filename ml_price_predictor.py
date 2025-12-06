"""🤖 ML PRICE PREDICTOR - MAKİNE ÖĞRENİMİ İLE TAHMİN
Random Forest + Gradient Boosting ensemble
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class MLPricePredictor:
    """Makine öğrenimi ile fiyat tahmini"""
    
    def __init__(self):
        self.rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.gb_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, prices):
        """Fiyatlardan özellikler çıkar"""
        if len(prices) < 20:
            return None
        
        features = []
        targets = []
        
        for i in range(20, len(prices)):
            window = prices[i-20:i]
            
            # Özellikler
            feat = [
                np.mean(window),           # Ortalama
                np.std(window),            # Volatilite
                np.max(window),            # Max
                np.min(window),            # Min
                window[-1],                # Son fiyat
                window[-1] - window[0],    # Değişim
                np.mean(window[-5:]),      # Son 5 gün ort
                np.mean(window[-10:]),     # Son 10 gün ort
                (window[-1] - np.min(window)) / (np.max(window) - np.min(window) + 0.0001),  # Pozisyon
                np.mean(np.diff(window))   # Trend
            ]
            
            features.append(feat)
            targets.append(prices[i])
        
        return np.array(features), np.array(targets)
    
    def train(self, prices):
        """Modeli eğit"""
        result = self.prepare_features(prices)
        if result is None:
            return False
        
        X, y = result
        
        if len(X) < 10:
            return False
        
        X_scaled = self.scaler.fit_transform(X)
        
        self.rf_model.fit(X_scaled, y)
        self.gb_model.fit(X_scaled, y)
        
        self.is_trained = True
        return True
    
    def predict_next(self, prices):
        """Sonraki fiyatı tahmin et"""
        if not self.is_trained:
            if not self.train(prices):
                return None
        
        if len(prices) < 20:
            return None
        
        window = prices[-20:]
        
        feat = [
            np.mean(window),
            np.std(window),
            np.max(window),
            np.min(window),
            window[-1],
            window[-1] - window[0],
            np.mean(window[-5:]),
            np.mean(window[-10:]),
            (window[-1] - np.min(window)) / (np.max(window) - np.min(window) + 0.0001),
            np.mean(np.diff(window))
        ]
        
        X = np.array([feat])
        X_scaled = self.scaler.transform(X)
        
        rf_pred = self.rf_model.predict(X_scaled)[0]
        gb_pred = self.gb_model.predict(X_scaled)[0]
        
        # Ensemble - ortalama
        ensemble_pred = (rf_pred + gb_pred) / 2
        
        current_price = prices[-1]
        change_pct = ((ensemble_pred - current_price) / current_price) * 100
        
        # Güven hesapla
        pred_diff = abs(rf_pred - gb_pred) / current_price * 100
        confidence = max(0, 100 - pred_diff * 10)
        
        return {
            'current_price': round(current_price, 4),
            'predicted_price': round(ensemble_pred, 4),
            'change_percent': round(change_pct, 2),
            'confidence': round(confidence, 1),
            'rf_prediction': round(rf_pred, 4),
            'gb_prediction': round(gb_pred, 4),
            'direction': 'UP' if change_pct > 0 else 'DOWN',
            'recommendation': self._get_recommendation(change_pct, confidence)
        }
    
    def _get_recommendation(self, change_pct, confidence):
        """Tahmine göre tavsiye"""
        if confidence < 50:
            return 'HOLD - Düşük güven'
        
        if change_pct > 5:
            return 'STRONG_BUY - Güçlü yükseliş bekleniyor'
        elif change_pct > 2:
            return 'BUY - Yükseliş bekleniyor'
        elif change_pct > -2:
            return 'HOLD - Yatay bekleniyor'
        elif change_pct > -5:
            return 'SELL - Düşüş bekleniyor'
        else:
            return 'STRONG_SELL - Güçlü düşüş bekleniyor'


def predict_crypto_price(prices):
    """Kripto fiyat tahmini"""
    predictor = MLPricePredictor()
    return predictor.predict_next(prices)


if __name__ == '__main__':
    # Test
    import random
    
    # Simüle fiyat verisi (yükselen trend)
    base = 100
    prices = []
    for i in range(100):
        base += random.uniform(-2, 3)  # Hafif yükseliş eğilimi
        prices.append(base)
    
    predictor = MLPricePredictor()
    result = predictor.predict_next(prices)
    
    print("🤖 ML FİYAT TAHMİNİ\n")
    print(f"Mevcut Fiyat: {result['current_price']}")
    print(f"Tahmin: {result['predicted_price']}")
    print(f"Değişim: {result['change_percent']}%")
    print(f"Güven: {result['confidence']}%")
    print(f"Yön: {result['direction']}")
    print(f"Tavsiye: {result['recommendation']}")
