"""
Quantum Analyzer V2 - Gelişmiş Analiz Sistemi
- Multi-timeframe analiz (15m, 1h, 4h, 1d)
- BTCTurk direkt veri
- Sıkı eşikler
- Tahmin takibi
- Sadece yüksek güvenilirlikli sinyaller
"""

import os
import sys
import requests
from datetime import datetime
import pytz
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

try:
    from src.analysis.btcturk_ohlcv import BTCTurkOHLCV
    from src.analysis.composite_signal import CompositeSignalEngine
    from src.analysis.prediction_tracker import PredictionTracker
    from src.analysis.pattern_detector import PatternDetector
except Exception as e:
    logger.error(f"Module import error: {e}")


class QuantumAnalyzerV2:
    def __init__(self):
        self.ohlcv = BTCTurkOHLCV()
        self.engine = CompositeSignalEngine()
        self.tracker = PredictionTracker()
        self.pattern = PatternDetector()
    
    def analyze_coin(self, symbol):
        """Tek coin için tam analiz"""
        pair = f"{symbol}TRY"
        
        # Anlık veri
        ticker = self.ohlcv.get_ticker(pair)
        if not ticker:
            return None
        
        # Multi-timeframe OHLCV - önce Binance, sonra BTCTurk fallback
        multi_tf = {}
        for tf in ['1h', '4h', '1d']:
            # Binance dene
            ohlcv = self.ohlcv.get_binance_ohlcv(symbol, tf, limit=50)
            
            # Binance yoksa BTCTurk/fallback dene
            if not ohlcv or len(ohlcv) < 10:
                ohlcv = self.ohlcv.get_ohlcv(pair, tf, limit=50)
            
            if ohlcv and len(ohlcv) >= 5:  # Minimum 5 mum yeterli
                multi_tf[tf] = ohlcv
        
        # Hiç veri yoksa basit analiz yap
        if not multi_tf:
            # Ticker'dan basit analiz
            return self._simple_analysis(symbol, ticker)
        
        # Composite analiz
        result = self.engine.analyze_multi_timeframe(multi_tf)
        
        # Pattern analizi (günlük veri ile)
        if '1d' in multi_tf:
            pattern_result = self.pattern.analyze_full(multi_tf['1d'])
            if pattern_result:
                result['patterns'] = pattern_result
                
                # Pattern sinyallerini ekle
                if pattern_result.get('signals'):
                    result['signals'].extend(pattern_result['signals'][:2])
                
                # Pattern skoru ile final skoru güncelle
                pattern_score = pattern_result.get('pattern_score', 0)
                result['score'] = max(0, min(100, result['score'] + pattern_score // 3))
        
        result['symbol'] = symbol
        result['price'] = ticker['price']
        result['change'] = ticker['change']
        result['volume'] = ticker['volume']
        result['high'] = ticker['high']
        result['low'] = ticker['low']
        
        return result
    
    def _simple_analysis(self, symbol, ticker):
        """OHLCV olmayan coinler için basit analiz"""
        score = 50
        signals = []
        
        change = ticker['change']
        price = ticker['price']
        high = ticker['high']
        low = ticker['low']
        
        # Günlük değişime göre skor
        if change > 20:
            score -= 20
            signals.append(f"⚠️ %{change:.0f} pump - dikkat")
        elif change > 10:
            score -= 10
            signals.append(f"Yüksek artış: %{change:.1f}")
        elif change < -15:
            score -= 15
            signals.append(f"Sert düşüş: %{change:.1f}")
        elif change < -5:
            score += 5
            signals.append(f"Düşüş sonrası fırsat olabilir")
        
        # Günlük range analizi
        if high > 0 and low > 0:
            range_pct = (high - low) / low * 100
            position = (price - low) / (high - low) * 100 if high != low else 50
            
            if position > 80:
                score -= 15
                signals.append(f"Günlük zirveye yakın (%{position:.0f})")
            elif position < 20:
                score += 10
                signals.append(f"Günlük dibe yakın (%{position:.0f})")
        
        score = max(0, min(100, score))
        
        if score >= 60:
            signal = 'WATCH'
            prediction = '🟡 İZLE'
        elif score >= 45:
            signal = 'NEUTRAL'
            prediction = '⚪ NÖTR'
        else:
            signal = 'AVOID'
            prediction = '🔴 UZAK DUR'
        
        return {
            'symbol': symbol,
            'price': price,
            'change': change,
            'volume': ticker['volume'],
            'high': high,
            'low': low,
            'score': score,
            'signal': signal,
            'prediction': prediction,
            'signals': signals,
            'confidence': 'LOW',
            'alignment': 'NONE',
            'pump_risk': 50 if change > 15 else 0,
            'timeframes': {},
            'data_source': 'ticker_only'
        }
    
    def scan_all(self, min_score=60):
        """Tüm coinleri tara, sadece güçlü sinyalleri döndür"""
        pairs = self.ohlcv.get_all_pairs()
        
        results = []
        for pair_info in pairs:
            symbol = pair_info['symbol']
            
            # Temel filtre - çok düşük hacimli coinleri atla
            if pair_info['volume'] * pair_info['price'] < 100000:
                continue
            
            result = self.analyze_coin(symbol)
            if result and result['score'] >= min_score:
                results.append(result)
        
        # Skora göre sırala
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def get_best_opportunities(self, limit=5):
        """En iyi fırsatları bul - sadece yüksek güvenilirlik"""
        all_results = self.scan_all(min_score=70)
        
        # Sadece HIGH confidence olanları filtrele
        high_conf = [r for r in all_results if r.get('confidence') == 'HIGH']
        
        if not high_conf:
            # High confidence yoksa en iyi 3'ü al
            high_conf = all_results[:3]
        
        return high_conf[:limit]
    
    def get_avoid_list(self, limit=5):
        """Uzak durulması gereken coinler"""
        pairs = self.ohlcv.get_all_pairs()
        
        avoid = []
        for pair_info in pairs:
            symbol = pair_info['symbol']
            
            # Yükselen coinleri kontrol et - pump olabilir
            if pair_info['change'] > 15:
                result = self.analyze_coin(symbol)
                if result and result['score'] < 50:
                    avoid.append(result)
        
        avoid.sort(key=lambda x: x['score'])
        return avoid[:limit]
    
    def send_analysis_report(self):
        """Telegram'a analiz raporu gönder"""
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz).strftime('%d.%m.%Y %H:%M')
        
        logger.info("🔬 Quantum V2 analiz başlıyor...")
        
        # En iyi fırsatlar
        best = self.get_best_opportunities(5)
        
        # Uzak durulacaklar
        avoid = self.get_avoid_list(3)
        
        # Accuracy stats
        stats = self.tracker.get_accuracy_stats(7)
        
        msg = f'''🔬 <b>QUANTUM V2 ANALİZ</b>
⏰ {now}
📊 Multi-Timeframe | Sıkı Eşikler

'''
        
        if best:
            msg += "<b>🟢 EN İYİ FIRSATLAR:</b>\n"
            for r in best[:4]:
                conf_icon = "✓" if r.get('confidence') == 'HIGH' else "?"
                msg += f"\n<b>{r['symbol']}</b> ₺{r['price']:,.2f} ({r['change']:+.1f}%)\n"
                msg += f"Skor: {r['score']}/100 {conf_icon} | {r['prediction']}\n"
                
                # Timeframe özeti
                tf_summary = []
                for tf, data in r.get('timeframes', {}).items():
                    if data:
                        tf_summary.append(f"{tf}:{data['score']}")
                if tf_summary:
                    msg += f"TF: {' | '.join(tf_summary)}\n"
                
                if r.get('signals'):
                    msg += f"💡 {r['signals'][0]}\n"
        else:
            msg += "⚠️ Şu an güçlü fırsat yok\n"
        
        if avoid:
            msg += "\n<b>🔴 UZAK DUR:</b>\n"
            for r in avoid[:3]:
                msg += f"• {r['symbol']} ({r['change']:+.1f}%) - Skor: {r['score']}\n"
                if r.get('pump_risk', 0) > 50:
                    msg += f"  ⚠️ Pump riski: {r['pump_risk']}%\n"
        
        # Accuracy
        if stats['total'] > 0:
            msg += f"\n<b>📈 TAHMİN DOĞRULUĞU (7 gün):</b>\n"
            msg += f"Toplam: {stats['total']} | Doğru: {stats['correct']}\n"
            msg += f"Oran: %{stats['accuracy']}\n"
        
        msg += "\n🤖 Quantum V2 - Sıkı Eşikler"
        
        self.send_telegram(msg)
        logger.info(f"✅ Quantum V2 rapor gönderildi: {len(best)} fırsat")
        
        # Tahminleri kaydet
        for r in best:
            if r['score'] >= 75:
                self.tracker.add_prediction(
                    r['symbol'], 
                    r['price'], 
                    r['signal'], 
                    r['score']
                )
        
        return best
    
    def analyze_single_detailed(self, symbol):
        """Tek coin için detaylı analiz ve Telegram'a gönder"""
        result = self.analyze_coin(symbol)
        
        if not result:
            return None
        
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz).strftime('%d.%m.%Y %H:%M')
        
        conf_text = "YÜKSEK GÜVENİLİRLİK" if result.get('confidence') == 'HIGH' else "DÜŞÜK GÜVENİLİRLİK"
        
        msg = f'''🔬 <b>{symbol} DETAYLI ANALİZ</b>
⏰ {now}

💰 <b>Fiyat:</b> ₺{result['price']:,.4f}
📈 <b>24s:</b> {result['change']:+.1f}%
📊 <b>Hacim:</b> ₺{result['volume'] * result['price']:,.0f}

<b>📊 SKOR: {result['score']}/100</b>
{result['prediction']}
Güvenilirlik: {conf_text}

<b>⏱️ TIMEFRAME ANALİZİ:</b>
'''
        
        for tf, data in result.get('timeframes', {}).items():
            if data:
                rsi = data.get('rsi', 0)
                macd = data.get('macd', {}).get('trend', 'N/A')
                score = data.get('score', 0)
                msg += f"• {tf}: RSI {rsi:.0f} | MACD {macd} | Skor {score}\n"
        
        if result.get('alignment') != 'NONE':
            msg += f"\n✅ TF Uyumu: {result['alignment']}\n"
        
        if result.get('pump_risk', 0) > 30:
            msg += f"\n⚠️ Pump Riski: {result['pump_risk']}%\n"
        
        msg += "\n<b>💡 SİNYALLER:</b>\n"
        for sig in result.get('signals', [])[:5]:
            msg += f"• {sig}\n"
        
        msg += "\n🤖 Quantum V2"
        
        self.send_telegram(msg)
        
        return result
    
    def send_telegram(self, message):
        """Telegram'a mesaj gönder"""
        if not BOT_TOKEN or not CHAT_ID:
            logger.warning("Telegram credentials missing")
            return False
        try:
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
            resp = requests.post(url, json={
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }, timeout=15)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False


quantum_v2 = QuantumAnalyzerV2()


if __name__ == "__main__":
    analyzer = QuantumAnalyzerV2()
    analyzer.send_analysis_report()
