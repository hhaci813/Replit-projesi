"""
⚖️  AĞIRLIKLANDIRILMIŞ SINYAL PUANLAMA
Pattern accuracy + Trend + Volume + Momentum = Gerçek skor
"""

from typing import Dict, List

class WeightedScoringEngine:
    """Çok faktörlü puanlama sistemi"""
    
    # Pattern Türüne Göre Tarihi Doğruluk Oranları
    PATTERN_ACCURACY = {
        'three_white_soldiers': 0.68,
        'three_black_crows': 0.67,
        'morning_star': 0.72,
        'evening_star': 0.70,
        'bullish_engulfing': 0.62,
        'bearish_engulfing': 0.64,
        'hammer': 0.58,
        'hanging_man': 0.60,
        'doji': 0.45,
        'bullish_marubozu': 0.66,
        'bearish_marubozu': 0.68,
        'cup_handle': 0.75,
        'head_shoulders': 0.73,
        'double_bottom': 0.64,
        'double_top': 0.62,
        'ascending_triangle': 0.60,
        'descending_triangle': 0.61,
        'bullish_flag': 0.59,
        'bearish_flag': 0.60,
        'inverse_head_shoulders': 0.71,
    }
    
    # Scoring Ağırlıkları (Toplam = 100)
    WEIGHTS = {
        'pattern': 0.40,      # 40% - Mum/Grafik formasyonu
        'trend': 0.25,        # 25% - Trend yönü ve kuvveti
        'volume': 0.20,       # 20% - İşlem hacmi
        'momentum': 0.15,     # 15% - Momentum göstergeleri (RSI, MACD)
    }
    
    def calculate_signal_score(self, analysis_data: Dict) -> Dict:
        """Tüm faktörleri birleştirip final skor hesapla"""
        
        pattern_score = self._score_pattern(analysis_data)
        trend_score = self._score_trend(analysis_data)
        volume_score = self._score_volume(analysis_data)
        momentum_score = self._score_momentum(analysis_data)
        
        # Ağırlıklı ortalama
        final_score = (
            pattern_score * self.WEIGHTS['pattern'] +
            trend_score * self.WEIGHTS['trend'] +
            volume_score * self.WEIGHTS['volume'] +
            momentum_score * self.WEIGHTS['momentum']
        )
        
        signal_type = self._determine_signal(final_score)
        
        return {
            'pattern_score': round(pattern_score, 1),
            'trend_score': round(trend_score, 1),
            'volume_score': round(volume_score, 1),
            'momentum_score': round(momentum_score, 1),
            'final_score': round(final_score, 1),
            'signal_type': signal_type,
            'confidence': min(final_score / 100, 1.0),
            'breakdown': {
                'pattern': f"{pattern_score:.0f}% × {self.WEIGHTS['pattern']:.0%} = {pattern_score * self.WEIGHTS['pattern']:.1f}",
                'trend': f"{trend_score:.0f}% × {self.WEIGHTS['trend']:.0%} = {trend_score * self.WEIGHTS['trend']:.1f}",
                'volume': f"{volume_score:.0f}% × {self.WEIGHTS['volume']:.0%} = {volume_score * self.WEIGHTS['volume']:.1f}",
                'momentum': f"{momentum_score:.0f}% × {self.WEIGHTS['momentum']:.0%} = {momentum_score * self.WEIGHTS['momentum']:.1f}",
            }
        }
    
    def _score_pattern(self, data: Dict) -> float:
        """Pattern doğruluk oranına göre puan ver"""
        patterns = data.get('candle_patterns', [])
        if not patterns:
            return 40.0  # Varsayılan skor
        
        scores = []
        for pattern in patterns:
            pattern_name = pattern.get('pattern', '')
            base_accuracy = self.PATTERN_ACCURACY.get(pattern_name, 0.50)
            confidence = pattern.get('confidence', 0.5)
            score = base_accuracy * 100 * confidence
            scores.append(score)
        
        return sum(scores) / len(scores) if scores else 40.0
    
    def _score_trend(self, data: Dict) -> float:
        """Trend yönü ve kuvvetine göre puan"""
        trend = data.get('trend', {})
        direction = trend.get('direction', 'NEUTRAL').upper()
        strength = trend.get('strength', 0.5)
        
        base_score = {
            'BULLISH': 70,
            'BEARISH': 30,
            'NEUTRAL': 50,
            'STRONG_BULLISH': 85,
            'STRONG_BEARISH': 15,
        }.get(direction, 50)
        
        return base_score * strength + 50 * (1 - strength)
    
    def _score_volume(self, data: Dict) -> float:
        """Hacim sinyaline göre puan"""
        volume = data.get('volume_signal', {})
        signal = volume.get('signal', 'NORMAL').upper()
        
        score_map = {
            'HIGH': 80,
            'INCREASING': 70,
            'NORMAL': 50,
            'DECREASING': 30,
            'LOW': 20,
        }
        
        return score_map.get(signal, 50)
    
    def _score_momentum(self, data: Dict) -> float:
        """Momentum göstergelerine göre puan"""
        rsi = data.get('rsi_zone', {}).get('value', 50)
        macd = data.get('macd_signals', {}).get('signal', 'NEUTRAL')
        
        # RSI puan (50 = neutral, 30 altı = oversold/AL, 70 üstü = overbought/SAT)
        rsi_score = 50
        if 20 <= rsi <= 30:
            rsi_score = 80  # Oversold - AL sinyali
        elif 70 <= rsi <= 80:
            rsi_score = 20  # Overbought - SAT sinyali
        
        # MACD puan
        macd_score = {
            'BULLISH_CROSS': 80,
            'BULLISH': 70,
            'BEARISH_CROSS': 20,
            'BEARISH': 30,
            'NEUTRAL': 50,
        }.get(macd, 50)
        
        return (rsi_score * 0.6 + macd_score * 0.4)
    
    def _determine_signal(self, score: float) -> str:
        """Final skora göre sinyal türü belirle"""
        if score >= 80:
            return 'GÜÇLÜ AL 🟢'
        elif score >= 65:
            return 'AL 🟢'
        elif score >= 50:
            return 'TUT ⚪'
        elif score >= 35:
            return 'SAT 🔴'
        else:
            return 'GÜÇLÜ SAT 🔴'
    
    def get_scoring_report(self, analysis_data: Dict) -> str:
        """Detaylı puanlama raporu"""
        result = self.calculate_signal_score(analysis_data)
        
        msg = f"⚖️  AĞIRLIKLANDIRILMIŞ PUANLAMA\n"
        msg += f"{'='*45}\n"
        msg += f"📊 Pattern Skoru: {result['pattern_score']:.0f}/100\n"
        msg += f"📈 Trend Skoru: {result['trend_score']:.0f}/100\n"
        msg += f"📦 Hacim Skoru: {result['volume_score']:.0f}/100\n"
        msg += f"⚡ Momentum Skoru: {result['momentum_score']:.0f}/100\n"
        msg += f"\n{'FINAL SKOR':-^45}\n"
        msg += f"🎯 {result['final_score']:.0f}/100\n"
        msg += f"📍 Sinyal: {result['signal_type']}\n"
        msg += f"💪 Güven: {result['confidence']:.0%}\n"
        msg += f"\n{'DETAYLI HESAP':-^45}\n"
        for key, val in result['breakdown'].items():
            msg += f"{key.upper()}: {val}\n"
        
        return msg
