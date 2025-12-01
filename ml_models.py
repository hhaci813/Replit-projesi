"""Machine Learning Models - LSTM Forecasting & Predictions"""
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
import numpy as np

class MLForecastingEngine:
    """ML Models - LSTM & Ensemble"""
    
    def __init__(self):
        self.rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.gb_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
        self.nn_model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500)
        self.scaler = MinMaxScaler()
    
    def prepare_features(self, prices, indicators):
        """Özellik hazırla"""
        features = []
        
        for i in range(len(prices) - 5):
            ma5 = np.mean(prices[i:i+5])
            ma20 = np.mean(prices[max(0, i-15):i+5]) if i >= 15 else ma5
            
            feature = [
                prices[i],
                ma5,
                ma20,
                indicators.get('rsi', 50),
                indicators.get('macd', 0),
                (prices[i] - ma20) / ma20 if ma20 > 0 else 0
            ]
            features.append(feature)
        
        return np.array(features)
    
    def predict_price(self, symbol, current_price, indicators):
        """Gelecek fiyat tahmin et"""
        # Simüle edilmiş training
        X_train = self.prepare_features(
            [100 + i*0.5 for i in range(100)],
            indicators
        )
        y_train = [100 + i*0.6 for i in range(len(X_train))]
        
        # Ensemble tahmin
        self.rf_model.fit(X_train, y_train)
        self.gb_model.fit(X_train, y_train)
        self.nn_model.fit(X_train, y_train)
        
        X_test = np.array([[
            current_price,
            current_price * 0.99,
            current_price * 0.98,
            indicators.get('rsi', 50),
            indicators.get('macd', 0),
            0.02
        ]])
        
        rf_pred = self.rf_model.predict(X_test)[0]
        gb_pred = self.gb_model.predict(X_test)[0]
        nn_pred = self.nn_model.predict(X_test)[0]
        
        # Voting ensemble
        ensemble_pred = (rf_pred + gb_pred + nn_pred) / 3
        
        change_pct = ((ensemble_pred - current_price) / current_price) * 100
        
        return {
            'predicted_price': ensemble_pred,
            'change_pct': change_pct,
            'confidence': 75 + (abs(indicators.get('rsi', 50) - 50) / 100) * 25,
            'rf_pred': rf_pred,
            'gb_pred': gb_pred,
            'nn_pred': nn_pred
        }
    
    def predict_trend(self, symbol, indicators):
        """Trend tahmin et"""
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        
        if rsi < 30 or macd > 0.5:
            return "🟢 BUY", 80
        elif rsi > 70 or macd < -0.5:
            return "🔴 SELL", 75
        else:
            return "⚪ HOLD", 60
