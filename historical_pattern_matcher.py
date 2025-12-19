"""
📜 TARİHSEL PATTERN KARŞILAŞTIRMA SİSTEMİ
Geçmişte aynı pattern görüldüğünde ne olmuş? Kıyaslama yap!
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class HistoricalPatternMatcher:
    """Geçmiş verilerde pattern ara ve kıyasla"""
    
    def __init__(self):
        self.pattern_history = {}
        
    def fetch_historical_data(self, symbol: str, days: int = 365) -> List[Dict]:
        """yfinance ile tarihsel veri çek - TÜM COİNLER DESTEKLİ"""
        try:
            import yfinance as yf
            
            symbol_upper = symbol.upper().replace('TRY', '').replace('USDT', '').strip()
            
            yf_symbol = f"{symbol_upper}-USD"
            
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=f"{days}d")
            
            if df.empty:
                return []
            
            candles = []
            for idx, row in df.iterrows():
                candles.append({
                    'timestamp': int(idx.timestamp()),
                    'date': idx.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume']),
                })
            
            return candles
            
        except Exception as e:
            logger.error(f"Tarihsel veri hatası: {e}")
            return []
    
    def detect_pattern_in_candles(self, candles: List[Dict], window_size: int = 5) -> str:
        """Mum dizisinden pattern tespit et"""
        if len(candles) < window_size:
            return "UNKNOWN"
        
        last_candles = candles[-window_size:]
        
        bullish_count = sum(1 for c in last_candles if c['close'] > c['open'])
        bearish_count = window_size - bullish_count
        
        closes = [c['close'] for c in last_candles]
        price_change = ((closes[-1] - closes[0]) / closes[0]) * 100 if closes[0] > 0 else 0
        
        avg_body = np.mean([abs(c['close'] - c['open']) for c in last_candles])
        avg_range = np.mean([c['high'] - c['low'] for c in last_candles])
        body_ratio = avg_body / avg_range if avg_range > 0 else 0
        
        if bullish_count >= 4 and price_change > 5:
            return "STRONG_BULLISH_MOMENTUM"
        elif bullish_count >= 3 and price_change > 2:
            return "BULLISH_TREND"
        elif bearish_count >= 4 and price_change < -5:
            return "STRONG_BEARISH_MOMENTUM"
        elif bearish_count >= 3 and price_change < -2:
            return "BEARISH_TREND"
        elif body_ratio < 0.3:
            return "CONSOLIDATION"
        elif abs(price_change) < 1:
            return "SIDEWAYS"
        else:
            return "MIXED"
    
    def find_similar_patterns_in_history(self, symbol: str, current_pattern: str, 
                                         lookback_days: int = 365) -> List[Dict]:
        """Geçmişte benzer pattern'leri bul"""
        candles = self.fetch_historical_data(symbol, lookback_days)
        
        if len(candles) < 30:
            return []
        
        similar_instances = []
        window_size = 5
        
        for i in range(window_size, len(candles) - 10):
            window = candles[i-window_size:i]
            pattern = self.detect_pattern_in_candles(window, window_size)
            
            if pattern == current_pattern:
                future_candles = candles[i:i+10]
                if len(future_candles) >= 5:
                    start_price = future_candles[0]['close']
                    
                    max_price = max(c['high'] for c in future_candles)
                    min_price = min(c['low'] for c in future_candles)
                    end_price = future_candles[-1]['close']
                    
                    max_gain = ((max_price - start_price) / start_price) * 100
                    max_loss = ((min_price - start_price) / start_price) * 100
                    final_change = ((end_price - start_price) / start_price) * 100
                    
                    outcome = "BULLISH" if final_change > 2 else "BEARISH" if final_change < -2 else "NEUTRAL"
                    
                    similar_instances.append({
                        'date': candles[i]['date'],
                        'start_price': round(start_price, 2),
                        'max_gain_percent': round(max_gain, 2),
                        'max_loss_percent': round(max_loss, 2),
                        'final_change_percent': round(final_change, 2),
                        'outcome': outcome,
                        'days_analyzed': len(future_candles)
                    })
        
        return similar_instances
    
    def calculate_pattern_statistics(self, similar_instances: List[Dict]) -> Dict:
        """Pattern istatistiklerini hesapla"""
        if not similar_instances:
            return {'error': 'Yeterli veri yok'}
        
        total = len(similar_instances)
        bullish = sum(1 for i in similar_instances if i['outcome'] == 'BULLISH')
        bearish = sum(1 for i in similar_instances if i['outcome'] == 'BEARISH')
        neutral = total - bullish - bearish
        
        avg_max_gain = np.mean([i['max_gain_percent'] for i in similar_instances])
        avg_max_loss = np.mean([i['max_loss_percent'] for i in similar_instances])
        avg_final = np.mean([i['final_change_percent'] for i in similar_instances])
        
        best_case = max(similar_instances, key=lambda x: x['final_change_percent'])
        worst_case = min(similar_instances, key=lambda x: x['final_change_percent'])
        
        win_rate = (bullish / total) * 100 if total > 0 else 0
        
        return {
            'total_occurrences': total,
            'bullish_outcomes': bullish,
            'bearish_outcomes': bearish,
            'neutral_outcomes': neutral,
            'win_rate': round(win_rate, 1),
            'avg_max_gain': round(avg_max_gain, 2),
            'avg_max_loss': round(avg_max_loss, 2),
            'avg_final_change': round(avg_final, 2),
            'best_case': {
                'date': best_case['date'],
                'change': best_case['final_change_percent']
            },
            'worst_case': {
                'date': worst_case['date'],
                'change': worst_case['final_change_percent']
            },
            'prediction': 'BULLISH' if win_rate > 55 else 'BEARISH' if win_rate < 45 else 'NEUTRAL',
            'confidence': 'HIGH' if total >= 10 else 'MEDIUM' if total >= 5 else 'LOW'
        }
    
    def analyze_and_compare(self, symbol: str) -> Dict:
        """Tam analiz ve geçmiş karşılaştırması"""
        candles = self.fetch_historical_data(symbol, days=30)
        
        if len(candles) < 10:
            return {'error': f'{symbol} için yeterli veri yok'}
        
        current_pattern = self.detect_pattern_in_candles(candles, window_size=5)
        
        similar = self.find_similar_patterns_in_history(symbol, current_pattern, lookback_days=365)
        
        if not similar:
            return {
                'symbol': symbol,
                'current_pattern': current_pattern,
                'error': 'Geçmişte benzer pattern bulunamadı'
            }
        
        stats = self.calculate_pattern_statistics(similar)
        
        return {
            'symbol': symbol,
            'current_pattern': current_pattern,
            'current_price': candles[-1]['close'],
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'historical_data': stats,
            'similar_instances': similar[:5]
        }
    
    def get_comparison_message(self, symbol: str) -> str:
        """Telegram mesajı formatı"""
        result = self.analyze_and_compare(symbol)
        
        if 'error' in result:
            return f"❌ {result.get('error', 'Analiz hatası')}"
        
        stats = result.get('historical_data', {})
        pattern = result.get('current_pattern', 'UNKNOWN')
        price = result.get('current_price', 0)
        
        pattern_names = {
            'STRONG_BULLISH_MOMENTUM': '🚀 GÜÇLÜ YÜKSELİŞ MOMENTUMu',
            'BULLISH_TREND': '📈 YÜKSELİŞ TRENDİ',
            'STRONG_BEARISH_MOMENTUM': '💥 GÜÇLÜ DÜŞÜŞ MOMENTUMU',
            'BEARISH_TREND': '📉 DÜŞÜŞ TRENDİ',
            'CONSOLIDATION': '📦 KONSOLİDASYON',
            'SIDEWAYS': '➡️ YATAY SEYIR',
            'MIXED': '🔄 KARIŞIK SİNYALLER'
        }
        
        pattern_display = pattern_names.get(pattern, pattern)
        
        msg = f"📜 {result['symbol']} TARİHSEL KARŞILAŞTIRMA\n"
        msg += f"{'='*50}\n\n"
        
        msg += f"📊 MEVCUT DURUM:\n"
        msg += f"   Pattern: {pattern_display}\n"
        msg += f"   Fiyat: ₺{price:,.2f}\n"
        msg += f"   Tarih: {result['analysis_date']}\n\n"
        
        msg += f"📈 GEÇMİŞTE BU PATTERN:\n"
        msg += f"   Toplam görülme: {stats['total_occurrences']} kez\n"
        msg += f"   🟢 Yükseliş: {stats['bullish_outcomes']} kez\n"
        msg += f"   🔴 Düşüş: {stats['bearish_outcomes']} kez\n"
        msg += f"   ⚪ Nötr: {stats['neutral_outcomes']} kez\n\n"
        
        msg += f"📊 İSTATİSTİKLER:\n"
        msg += f"   ✅ Kazanma Oranı: %{stats['win_rate']}\n"
        msg += f"   📈 Ort. Max Kazanç: %{stats['avg_max_gain']:+.1f}\n"
        msg += f"   📉 Ort. Max Kayıp: %{stats['avg_max_loss']:.1f}\n"
        msg += f"   📌 Ort. Sonuç: %{stats['avg_final_change']:+.1f}\n\n"
        
        msg += f"🏆 EN İYİ SONUÇ:\n"
        msg += f"   {stats['best_case']['date']}: %{stats['best_case']['change']:+.1f}\n"
        msg += f"💥 EN KÖTÜ SONUÇ:\n"
        msg += f"   {stats['worst_case']['date']}: %{stats['worst_case']['change']:.1f}\n\n"
        
        prediction = stats.get('prediction', 'NEUTRAL')
        confidence = stats.get('confidence', 'LOW')
        
        if prediction == 'BULLISH':
            emoji = "🟢"
            action = "YÜKSELİŞ BEKLENİYOR"
        elif prediction == 'BEARISH':
            emoji = "🔴"
            action = "DÜŞÜŞ BEKLENİYOR"
        else:
            emoji = "⚪"
            action = "BELİRSİZ - BEKLEME YAP"
        
        msg += f"{'='*50}\n"
        msg += f"🎯 TARİHSEL TAHMİN: {emoji} {action}\n"
        msg += f"💪 Güvenilirlik: {confidence}\n"
        msg += f"{'='*50}\n"
        
        similar = result.get('similar_instances', [])[:3]
        if similar:
            msg += f"\n📅 BENZER DÖNEMLER:\n"
            for i, s in enumerate(similar, 1):
                outcome_emoji = "🟢" if s['outcome'] == 'BULLISH' else "🔴" if s['outcome'] == 'BEARISH' else "⚪"
                msg += f"   {i}. {s['date']}: {outcome_emoji} %{s['final_change_percent']:+.1f}\n"
        
        return msg
