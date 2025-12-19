"""
🚀 MEGA ANALİZ SİSTEMİ
Tüm analiz modüllerini bir araya getirir:
- Pump tespiti
- Derin analiz
- Grafik analizi
- Tarihsel karşılaştırma
- Sniper tarama
- Hacim analizi
TEK MESAJDA özet çıkarır
"""

import logging
from typing import Dict, List, Optional
import requests
import numpy as np

logger = logging.getLogger(__name__)

class MegaAnalyzer:
    """Tüm analiz sistemlerini birleştiren süper analiz motoru"""
    
    def __init__(self):
        self.pump_validator = None
        self.historical_matcher = None
        
        try:
            from pump_validator import PumpValidator
            self.pump_validator = PumpValidator()
        except:
            pass
        
        try:
            from historical_pattern_matcher import HistoricalPatternMatcher
            self.historical_matcher = HistoricalPatternMatcher()
        except:
            pass
    
    def get_btcturk_data(self) -> List[Dict]:
        """BTCTurk verilerini al"""
        try:
            resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=15)
            return resp.json().get('data', [])
        except:
            return []
    
    def get_technical_indicators(self, symbol: str) -> Dict:
        """Teknik göstergeleri hesapla"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}-USD")
            hist = ticker.history(period="30d")
            
            if len(hist) < 14:
                return {}
            
            closes = hist['Close'].values
            
            delta = np.diff(closes)
            gains = np.where(delta > 0, delta, 0)
            losses = np.where(delta < 0, -delta, 0)
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            rsi = 100 - (100 / (1 + rs))
            
            ema12 = self._ema(closes, 12)
            ema26 = self._ema(closes, 26)
            macd = ema12 - ema26
            signal = self._ema(np.array([macd]), 9) if len([macd]) >= 9 else macd
            
            sma20 = np.mean(closes[-20:])
            std20 = np.std(closes[-20:])
            bb_upper = sma20 + 2 * std20
            bb_lower = sma20 - 2 * std20
            
            current_price = closes[-1]
            
            if current_price < bb_lower:
                bb_signal = "AŞIRI SATIM"
            elif current_price > bb_upper:
                bb_signal = "AŞIRI ALIM"
            else:
                bb_signal = "NORMAL"
            
            change_24h = ((closes[-1] - closes[-2]) / closes[-2]) * 100 if len(closes) >= 2 else 0
            change_7d = ((closes[-1] - closes[-7]) / closes[-7]) * 100 if len(closes) >= 7 else 0
            
            volumes = hist['Volume'].values
            avg_vol = np.mean(volumes[-7:])
            current_vol = volumes[-1]
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
            
            return {
                'rsi': round(rsi, 1),
                'macd': round(macd, 4),
                'bb_signal': bb_signal,
                'change_24h': round(change_24h, 2),
                'change_7d': round(change_7d, 2),
                'volume_ratio': round(vol_ratio, 2),
                'current_price_usd': round(current_price, 4)
            }
        except Exception as e:
            logger.warning(f"Teknik gösterge hatası {symbol}: {e}")
            return {}
    
    def _ema(self, data: np.ndarray, period: int) -> float:
        """EMA hesapla"""
        if len(data) < period:
            return data[-1] if len(data) > 0 else 0
        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()
        return np.convolve(data, weights, mode='valid')[-1]
    
    def analyze_single_coin(self, symbol: str, current_price_tl: float = 0) -> Dict:
        """Tek coin için mega analiz"""
        result = {
            'symbol': symbol,
            'price_tl': current_price_tl,
            'score': 5.0,
            'signal': 'TUT',
            'reasons_buy': [],
            'reasons_avoid': [],
            'technical': {},
            'historical': {},
            'pump_status': {},
            'target': 0,
            'stop_loss': 0
        }
        
        tech = self.get_technical_indicators(symbol)
        result['technical'] = tech
        
        if tech:
            rsi = tech.get('rsi', 50)
            change_24h = tech.get('change_24h', 0)
            vol_ratio = tech.get('volume_ratio', 1)
            bb_signal = tech.get('bb_signal', 'NORMAL')
            
            if rsi < 30:
                result['score'] += 1.5
                result['reasons_buy'].append(f"🟢 RSI aşırı satım ({rsi}) - Toparlanma beklenir")
            elif rsi < 40:
                result['score'] += 0.5
                result['reasons_buy'].append(f"🟢 RSI düşük ({rsi}) - Alım fırsatı")
            elif rsi > 70:
                result['score'] -= 1.5
                result['reasons_avoid'].append(f"🔴 RSI aşırı alım ({rsi}) - Düşüş riski")
            elif rsi > 60:
                result['score'] -= 0.5
                result['reasons_avoid'].append(f"🟡 RSI yüksek ({rsi}) - Dikkatli ol")
            
            if change_24h > 10:
                result['score'] += 1.0
                result['reasons_buy'].append(f"🚀 24s +%{change_24h:.1f} momentum")
            elif change_24h > 5:
                result['score'] += 0.5
                result['reasons_buy'].append(f"📈 24s +%{change_24h:.1f} yükseliş")
            elif change_24h < -10:
                result['score'] -= 1.0
                result['reasons_avoid'].append(f"📉 24s %{change_24h:.1f} düşüş")
            elif change_24h < -5:
                result['score'] -= 0.5
                result['reasons_avoid'].append(f"⚠️ 24s %{change_24h:.1f} kayıp")
            
            if vol_ratio > 3:
                result['score'] += 1.0
                result['reasons_buy'].append(f"📊 Hacim {vol_ratio:.1f}x artmış - İlgi var")
            elif vol_ratio < 0.5:
                result['score'] -= 0.5
                result['reasons_avoid'].append(f"📉 Hacim düşük ({vol_ratio:.1f}x) - İlgi az")
            
            if bb_signal == "AŞIRI SATIM":
                result['score'] += 1.0
                result['reasons_buy'].append("🟢 Bollinger alt bandı - Dipte")
            elif bb_signal == "AŞIRI ALIM":
                result['score'] -= 1.0
                result['reasons_avoid'].append("🔴 Bollinger üst bandı - Zirvede")
        
        if self.historical_matcher:
            try:
                hist_result = self.historical_matcher.analyze_and_compare(symbol)
                if 'historical_data' in hist_result:
                    hist_data = hist_result['historical_data']
                    result['historical'] = hist_data
                    
                    win_rate = hist_data.get('win_rate', 50)
                    total_occ = hist_data.get('total_occurrences', 0)
                    prediction = hist_data.get('prediction', 'NEUTRAL')
                    
                    if win_rate > 60 and total_occ >= 5:
                        result['score'] += 1.0
                        result['reasons_buy'].append(f"📜 Tarihsel %{win_rate:.0f} başarı ({total_occ} örnek)")
                    elif win_rate < 40 and total_occ >= 5:
                        result['score'] -= 1.0
                        result['reasons_avoid'].append(f"📜 Tarihsel %{win_rate:.0f} başarı - Riskli")
                    
                    if prediction == 'BULLISH':
                        result['score'] += 0.5
                    elif prediction == 'BEARISH':
                        result['score'] -= 0.5
            except:
                pass
        
        if self.pump_validator:
            try:
                pump_analysis = self.pump_validator.calculate_pump_reliability_score(symbol)
                result['pump_status'] = pump_analysis
                
                reliability = pump_analysis.get('reliability_score', 50)
                is_fake = pump_analysis.get('likely_fake_pump', False)
                
                if is_fake:
                    result['score'] -= 2.0
                    result['reasons_avoid'].append("🔴 SAHTE PUMP TESPİTİ - UZAK DUR!")
                elif reliability > 70:
                    result['score'] += 1.0
                    result['reasons_buy'].append(f"✅ Pump güvenilir (%{reliability})")
                elif reliability < 30:
                    result['score'] -= 0.5
                    result['reasons_avoid'].append(f"⚠️ Pump güvenilirliği düşük (%{reliability})")
            except:
                pass
        
        result['score'] = max(0, min(10, result['score']))
        
        if result['score'] >= 8:
            result['signal'] = 'GÜÇLÜ AL'
        elif result['score'] >= 6.5:
            result['signal'] = 'AL'
        elif result['score'] >= 4:
            result['signal'] = 'TUT'
        elif result['score'] >= 2.5:
            result['signal'] = 'SAT'
        else:
            result['signal'] = 'GÜÇLÜ SAT'
        
        if current_price_tl > 0:
            if result['signal'] in ['GÜÇLÜ AL', 'AL']:
                target_pct = 15 if result['signal'] == 'GÜÇLÜ AL' else 10
                stop_pct = 5 if result['signal'] == 'GÜÇLÜ AL' else 7
            else:
                target_pct = 5
                stop_pct = 10
            
            result['target'] = current_price_tl * (1 + target_pct/100)
            result['stop_loss'] = current_price_tl * (1 - stop_pct/100)
        
        return result
    
    def find_rising_coins(self, limit: int = 10) -> List[Dict]:
        """Yükselen coinleri bul ve mega analiz yap"""
        tickers = self.get_btcturk_data()
        
        try_pairs = [t for t in tickers if t.get('pair', '').endswith('TRY')]
        
        rising = []
        for t in try_pairs:
            change = float(t.get('dailyPercent', 0))
            if change > 0:
                symbol = t.get('pair', '').replace('TRY', '')
                price = float(t.get('last', 0))
                rising.append({
                    'symbol': symbol,
                    'price': price,
                    'change': change,
                    'volume': float(t.get('volume', 0))
                })
        
        rising.sort(key=lambda x: x['change'], reverse=True)
        
        results = []
        for coin in rising[:limit]:
            analysis = self.analyze_single_coin(coin['symbol'], coin['price'])
            analysis['change_24h_btcturk'] = coin['change']
            results.append(analysis)
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def find_potential_risers(self, limit: int = 10) -> List[Dict]:
        """Yükselecek potansiyeli olan coinleri bul"""
        tickers = self.get_btcturk_data()
        
        try_pairs = [t for t in tickers if t.get('pair', '').endswith('TRY')]
        
        potential = []
        for t in try_pairs:
            symbol = t.get('pair', '').replace('TRY', '')
            price = float(t.get('last', 0))
            change = float(t.get('dailyPercent', 0))
            
            if -5 < change < 5:
                analysis = self.analyze_single_coin(symbol, price)
                if analysis['score'] >= 6:
                    potential.append(analysis)
        
        potential.sort(key=lambda x: x['score'], reverse=True)
        return potential[:limit]
    
    def format_mega_message(self, coins: List[Dict], title: str) -> str:
        """Mega analiz mesajı formatla"""
        if not coins:
            return f"❌ {title} için sonuç bulunamadı"
        
        msg = f"🚀 <b>{title}</b>\n"
        msg += f"{'═' * 35}\n\n"
        
        for i, coin in enumerate(coins[:7], 1):
            symbol = coin['symbol']
            score = coin['score']
            signal = coin['signal']
            price = coin.get('price_tl', 0)
            
            if signal == 'GÜÇLÜ AL':
                signal_emoji = "🟢🟢"
            elif signal == 'AL':
                signal_emoji = "🟢"
            elif signal == 'TUT':
                signal_emoji = "⏸️"
            elif signal == 'SAT':
                signal_emoji = "🔴"
            else:
                signal_emoji = "🔴🔴"
            
            msg += f"<b>{i}. {signal_emoji} {symbol}</b> - Skor: {score:.1f}/10\n"
            
            if price > 0:
                msg += f"   💰 ₺{price:,.2f}"
                change = coin.get('change_24h_btcturk', coin.get('technical', {}).get('change_24h', 0))
                if change:
                    msg += f" | 24s: {'+' if change > 0 else ''}{change:.1f}%"
                msg += "\n"
            
            tech = coin.get('technical', {})
            if tech:
                rsi = tech.get('rsi', 0)
                vol = tech.get('volume_ratio', 1)
                msg += f"   📊 RSI: {rsi} | Hacim: {vol:.1f}x\n"
            
            hist = coin.get('historical', {})
            if hist:
                win_rate = hist.get('win_rate', 0)
                total = hist.get('total_occurrences', 0)
                if total > 0:
                    msg += f"   📜 Tarihsel: %{win_rate:.0f} başarı ({total} örnek)\n"
            
            if coin.get('target', 0) > 0:
                msg += f"   🎯 Hedef: ₺{coin['target']:,.2f} | 🛑 Stop: ₺{coin['stop_loss']:,.2f}\n"
            
            reasons_buy = coin.get('reasons_buy', [])[:2]
            reasons_avoid = coin.get('reasons_avoid', [])[:2]
            
            if signal in ['GÜÇLÜ AL', 'AL'] and reasons_buy:
                msg += f"   ✅ <b>NEDEN AL:</b>\n"
                for r in reasons_buy:
                    msg += f"      • {r}\n"
            
            if signal in ['GÜÇLÜ SAT', 'SAT'] and reasons_avoid:
                msg += f"   ❌ <b>NEDEN UZAK DUR:</b>\n"
                for r in reasons_avoid:
                    msg += f"      • {r}\n"
            
            if signal == 'TUT':
                if reasons_buy:
                    msg += f"   ✅ {reasons_buy[0]}\n"
                if reasons_avoid:
                    msg += f"   ⚠️ {reasons_avoid[0]}\n"
            
            msg += "\n"
        
        msg += f"{'═' * 35}\n"
        msg += "⚠️ <i>Yatırım tavsiyesi değildir. DYOR!</i>"
        
        return msg
    
    def get_rising_message(self) -> str:
        """Yükselen coinler mega analiz mesajı"""
        coins = self.find_rising_coins(7)
        return self.format_mega_message(coins, "YÜKSELEN KRİPTOLAR (MEGA ANALİZ)")
    
    def get_potential_message(self) -> str:
        """Yükselecek coinler mega analiz mesajı"""
        coins = self.find_potential_risers(7)
        return self.format_mega_message(coins, "YÜKSELECEK POTANSİYELİ (MEGA ANALİZ)")


mega_analyzer = MegaAnalyzer()
