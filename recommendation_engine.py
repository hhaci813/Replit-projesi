"""🎯 Recommendation Engine - Kar/Zarar tahmini"""
import numpy as np
from datetime import datetime, timedelta

class RecommendationEngine:
    """Kar/Zarar tahmini ve öneriler"""
    
    def __init__(self):
        self.min_confidence = 0.6
    
    def generate_recommendation(self, asset_symbol, technical_score, sentiment_score, momentum_score):
        """
        Kar/Zarar önerisi oluştur
        Scores: -1 to +1 (negative to positive)
        """
        
        # Weighted average
        weights = {'technical': 0.4, 'sentiment': 0.3, 'momentum': 0.3}
        composite_score = (
            technical_score * weights['technical'] +
            sentiment_score * weights['sentiment'] +
            momentum_score * weights['momentum']
        )
        
        # Confidence
        confidence = abs(composite_score)
        
        # Action
        if composite_score > 0.3:
            action = 'STRONG_BUY'
            profit_potential = 10 + abs(composite_score) * 50
            risk_potential = 3
        elif composite_score > 0.1:
            action = 'BUY'
            profit_potential = 5 + abs(composite_score) * 30
            risk_potential = 5
        elif composite_score < -0.3:
            action = 'STRONG_SELL'
            profit_potential = -10 - abs(composite_score) * 50
            risk_potential = 8
        elif composite_score < -0.1:
            action = 'SELL'
            profit_potential = -5 - abs(composite_score) * 30
            risk_potential = 6
        else:
            action = 'HOLD'
            profit_potential = 0
            risk_potential = 2
        
        return {
            'asset': asset_symbol,
            'action': action,
            'confidence': confidence,
            'profit_potential': profit_potential,
            'risk_potential': risk_potential,
            'reasoning': self._generate_reasoning(action, composite_score),
            'emoji': self._action_emoji(action)
        }
    
    @staticmethod
    def _generate_reasoning(action, score):
        """Açıklama oluştur"""
        reasons = []
        
        if score > 0.4:
            reasons.append("📈 Strong uptrend momentum")
            reasons.append("🟢 Positive expert sentiment")
            reasons.append("💪 Technical indicators bullish")
            return " • ".join(reasons)
        elif score > 0.1:
            reasons.append("📈 Moderate uptrend")
            reasons.append("🟢 Positive sentiment")
            return " • ".join(reasons)
        elif score < -0.4:
            reasons.append("📉 Strong downtrend")
            reasons.append("🔴 Negative sentiment")
            reasons.append("⚠️ Technical indicators bearish")
            return " • ".join(reasons)
        elif score < -0.1:
            reasons.append("📉 Downtrend risk")
            reasons.append("🔴 Negative sentiment")
            return " • ".join(reasons)
        else:
            return "🟡 Balanced - Wait for clearer signal"
    
    @staticmethod
    def _action_emoji(action):
        """Action emoji"""
        emojis = {
            'STRONG_BUY': '🟢🟢🚀',
            'BUY': '🟢📈',
            'HOLD': '🟡⏸️',
            'SELL': '🔴📉',
            'STRONG_SELL': '🔴🔴🌪️'
        }
        return emojis.get(action, '🟡')
    
    def calculate_profit_loss(self, entry_price, current_price, action):
        """Kar/Zarar hesapla"""
        change_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
        
        if change_pct > 0:
            status = "✅ PROFIT"
            emoji = "💰"
        elif change_pct < 0:
            status = "❌ LOSS"
            emoji = "📉"
        else:
            status = "➡️ BREAK EVEN"
            emoji = "⚪"
        
        return {
            'status': status,
            'pnl_pct': change_pct,
            'emoji': emoji,
            'action_recommendation': f"Consider {action} to lock in profits" if change_pct > 5 else f"Hold or {action}"
        }

if __name__ == "__main__":
    engine = RecommendationEngine()
    rec = engine.generate_recommendation('BTC', 0.6, 0.4, 0.7)
    print(f"Recommendation: {rec['action']}")
    print(f"Profit Potential: +{rec['profit_potential']:.1f}%")
    print(f"Risk: {rec['risk_potential']:.1f}%")
