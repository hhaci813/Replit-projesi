"""Advanced Signal Generator - Multiple Algorithms"""
import numpy as np

class SignalGenerator:
    @staticmethod
    def ensemble_signal(symbol, indicators):
        """Ensemble sinyal - Çoklu algoritma"""
        votes = 0
        
        # RSI sinyali
        if indicators.get('rsi', 50) < 30: votes += 1
        elif indicators.get('rsi', 50) > 70: votes -= 1
        
        # MACD sinyali
        if indicators.get('macd', 0) > indicators.get('signal', 0): votes += 1
        else: votes -= 1
        
        # Moving Average sinyali
        price = indicators.get('price', 0)
        ma20 = indicators.get('ma20', 0)
        ma50 = indicators.get('ma50', 0)
        
        if price > ma20 > ma50: votes += 2
        elif price < ma20 < ma50: votes -= 2
        
        # Bollinger Bands
        if price < indicators.get('bb_low', 0): votes += 1
        elif price > indicators.get('bb_high', 0): votes -= 1
        
        # Final sinyal
        if votes >= 2: return "🟢 GÜÇLÜ AL"
        elif votes == 1: return "🟢 AL"
        elif votes == 0: return "⚪ HOLD"
        elif votes == -1: return "🔴 SAT"
        else: return "🔴 GÜÇLÜ SAT"
    
    @staticmethod
    def calculate_confidence(signals_agreement):
        """Sinyal tutarlılığı = Güven"""
        return min(0.999, 0.5 + (signals_agreement / 10))
