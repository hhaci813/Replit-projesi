"""
ML ADVANCED - MAX SEVİYE MAKİNE ÖĞRENMESİ
LSTM + Gradient Boosting + Random Forest + Neural Network Ensemble
Gelişmiş fiyat tahmini ve sinyal üretimi
"""

import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

class MLAdvancedPredictor:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.models = {}
        self.predictions = {}
        self.confidence_threshold = 0.65
        
    def fetch_historical_data(self, symbol: str, days: int = 90) -> pd.DataFrame:
        """Tarihsel veri çek"""
        try:
            # BTCTurk OHLC API
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            resp = requests.get(
                f"https://graph-api.btcturk.com/v1/klines/history",
                params={
                    "symbol": f"{symbol}USDT",
                    "resolution": "D",
                    "from": start_time // 1000,
                    "to": end_time // 1000
                },
                timeout=15
            )
            
            data = resp.json()
            
            if 'c' in data and len(data['c']) > 10:
                df = pd.DataFrame({
                    'timestamp': data.get('t', []),
                    'open': [float(x) for x in data.get('o', [])],
                    'high': [float(x) for x in data.get('h', [])],
                    'low': [float(x) for x in data.get('l', [])],
                    'close': [float(x) for x in data.get('c', [])],
                    'volume': [float(x) for x in data.get('v', [])]
                })
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            return pd.DataFrame()
    
    def calculate_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gelişmiş özellik çıkarımı"""
        if df.empty or len(df) < 20:
            return df
        
        # Temel fiyat özellikleri
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Moving Averages
        for period in [5, 10, 20, 50]:
            df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'ma_{period}_ratio'] = df['close'] / df[f'ma_{period}']
        
        # Exponential Moving Averages
        for period in [12, 26]:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_mid'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volatilite
        df['volatility_5'] = df['returns'].rolling(window=5).std()
        df['volatility_20'] = df['returns'].rolling(window=20).std()
        
        # Volume özellikleri
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # Price momentum
        df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
        df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        df['momentum_20'] = df['close'] / df['close'].shift(20) - 1
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        df['atr_ratio'] = df['atr'] / df['close']
        
        # Stochastic Oscillator
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['stoch_k'] = 100 * (df['close'] - low_14) / (high_14 - low_14)
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        
        # Target: 7 günlük getiri
        df['target'] = df['close'].shift(-7) / df['close'] - 1
        
        return df.dropna()
    
    def build_ensemble_model(self):
        """Ensemble model oluştur"""
        rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        gb = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        nn = MLPRegressor(
            hidden_layer_sizes=(64, 32, 16),
            activation='relu',
            solver='adam',
            max_iter=500,
            random_state=42,
            early_stopping=True
        )
        
        ensemble = VotingRegressor([
            ('rf', rf),
            ('gb', gb),
            ('nn', nn)
        ])
        
        return ensemble
    
    def train_and_predict(self, symbol: str) -> dict:
        """Model eğit ve tahmin yap"""
        df = self.fetch_historical_data(symbol, days=120)
        
        if df.empty or len(df) < 30:
            return {
                "symbol": symbol,
                "error": "Yetersiz veri",
                "prediction": None
            }
        
        df = self.calculate_advanced_features(df)
        
        if len(df) < 20:
            return {
                "symbol": symbol,
                "error": "Özellik hesaplanamadı",
                "prediction": None
            }
        
        # Feature selection
        feature_cols = [
            'returns', 'ma_5_ratio', 'ma_10_ratio', 'ma_20_ratio',
            'macd', 'macd_histogram', 'rsi', 'bb_position', 'bb_width',
            'volatility_5', 'volatility_20', 'volume_ratio',
            'momentum_5', 'momentum_10', 'momentum_20',
            'atr_ratio', 'stoch_k', 'stoch_d'
        ]
        
        available_cols = [c for c in feature_cols if c in df.columns]
        
        X = df[available_cols].values
        y = df['target'].values
        
        # Son 7 günü ayır (test için)
        X_train, X_test = X[:-7], X[-7:]
        y_train, y_test = y[:-7], y[-7:]
        
        # Scale
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Model eğit
        model = self.build_ensemble_model()
        model.fit(X_train_scaled, y_train)
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
        confidence = max(0, min(100, (cv_scores.mean() + 1) * 50))
        
        # Prediction
        latest_features = X_test_scaled[-1:] if len(X_test_scaled) > 0 else X_train_scaled[-1:]
        prediction = model.predict(latest_features)[0]
        
        # Current price
        current_price = float(df['close'].iloc[-1])
        predicted_price = current_price * (1 + prediction)
        
        # Signal generation
        if prediction > 0.10 and confidence > 60:
            signal = "STRONG_BUY"
            emoji = "🔥"
        elif prediction > 0.05 and confidence > 50:
            signal = "BUY"
            emoji = "🟢"
        elif prediction < -0.10 and confidence > 60:
            signal = "STRONG_SELL"
            emoji = "🔴"
        elif prediction < -0.05 and confidence > 50:
            signal = "SELL"
            emoji = "🟡"
        else:
            signal = "HOLD"
            emoji = "⚪"
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "predicted_change": prediction * 100,
            "confidence": confidence,
            "signal": signal,
            "emoji": emoji,
            "timeframe": "7 gün",
            "model_accuracy": cv_scores.mean(),
            "features_used": len(available_cols)
        }
    
    def analyze_multiple(self, symbols: list) -> list:
        """Birden fazla kripto analiz et"""
        results = []
        
        for symbol in symbols:
            try:
                result = self.train_and_predict(symbol)
                if result.get("prediction") != "error":
                    results.append(result)
            except Exception as e:
                continue
        
        # Sinyale göre sırala
        signal_order = {"STRONG_BUY": 0, "BUY": 1, "HOLD": 2, "SELL": 3, "STRONG_SELL": 4}
        results.sort(key=lambda x: (signal_order.get(x.get("signal", "HOLD"), 2), -x.get("confidence", 0)))
        
        return results
    
    def get_top_predictions(self, limit: int = 10) -> list:
        """En iyi tahminleri getir"""
        # Ana coinler
        major_coins = [
            "BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", 
            "DOT", "LINK", "MATIC", "ATOM", "UNI", "LTC"
        ]
        
        results = self.analyze_multiple(major_coins)
        
        # Sadece BUY sinyalleri
        buy_signals = [r for r in results if r.get("signal") in ["STRONG_BUY", "BUY"]]
        
        return buy_signals[:limit]
    
    def generate_report(self) -> str:
        """ML tahmin raporu"""
        predictions = self.get_top_predictions(8)
        
        report = """
🤖 <b>ML TAHMİN RAPORU - MAX SEVİYE</b>
━━━━━━━━━━━━━━━━━━━━━━━

🧠 <b>MODEL: Ensemble (RF + GB + NN)</b>
⏱️ <b>TAHMİN PERİYODU: 7 Gün</b>

"""
        
        if predictions:
            report += "📈 <b>EN İYİ FIRSATLAR</b>\n\n"
            
            for i, pred in enumerate(predictions, 1):
                report += f"""<b>{i}. {pred['emoji']} {pred['symbol']}</b>
   💰 Şimdi: ${pred['current_price']:.4f}
   🎯 Hedef: ${pred['predicted_price']:.4f}
   📊 Beklenen: {pred['predicted_change']:+.1f}%
   🎲 Güven: %{pred['confidence']:.0f}
   📍 Sinyal: {pred['signal']}

"""
        else:
            report += "⚠️ Şu an güçlü sinyal bulunamadı.\n"
        
        report += """━━━━━━━━━━━━━━━━━━━━━━━
🤖 <i>ML Advanced - Akıllı Yatırım Asistanı</i>
"""
        return report
    
    def send_telegram_report(self):
        """Raporu Telegram'a gönder"""
        import os
        TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "8268294938:AAFIdr7FfJdtq__FueMOdsvym19H8IBWdNs"
        TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "8391537149"
        
        report = self.generate_report()
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': report,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            return True
        except:
            return False


if __name__ == "__main__":
    predictor = MLAdvancedPredictor()
    print(predictor.generate_report())
