"""ML Tahmin - LSTM/Prophet alternatifi"""
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import yfinance as yf

class MLPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = MinMaxScaler()
        self.is_trained = False
    
    def train(self, symbol, days=90):
        """Model eğit"""
        try:
            data = yf.download(symbol, period=f"{days}d", progress=False)
            if len(data) < 20:
                return False, "Yeterli veri yok"
            
            # Features
            data['MA5'] = data['Close'].rolling(5).mean()
            data['MA20'] = data['Close'].rolling(20).mean()
            data['RSI'] = self._calc_rsi(data['Close'])
            data['Volume_MA'] = data['Volume'].rolling(5).mean()
            
            X = data[['MA5', 'MA20', 'RSI', 'Volume_MA']].dropna().values
            y = data['Close'][len(data)-len(X):].values
            
            if len(X) < 5:
                return False, "Eğitim için yeterli veri yok"
            
            self.model.fit(X, y)
            self.is_trained = True
            return True, f"✅ {symbol} modeli eğitildi ({len(X)} veri)"
        except Exception as e:
            return False, str(e)
    
    def predict(self, symbol):
        """Fiyat tahmini yap"""
        if not self.is_trained:
            return None, "Model eğitilmedi"
        
        try:
            data = yf.download(symbol, period="30d", progress=False)
            data['MA5'] = data['Close'].rolling(5).mean()
            data['MA20'] = data['Close'].rolling(20).mean()
            data['RSI'] = self._calc_rsi(data['Close'])
            data['Volume_MA'] = data['Volume'].rolling(5).mean()
            
            last_row = data[['MA5', 'MA20', 'RSI', 'Volume_MA']].dropna().iloc[-1].values.reshape(1, -1)
            prediction = self.model.predict(last_row)[0]
            
            current = data['Close'].iloc[-1]
            change_pct = ((prediction - current) / current) * 100
            
            return prediction, f"Tahmin: ${prediction:.2f} ({change_pct:+.2f}%)"
        except:
            return None, "Tahmin yapılamadı"
    
    def _calc_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
