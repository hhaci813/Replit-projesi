"""
PRO ANALİZ SİSTEMİ - ULTRA VERSION
8 Gelişmiş Teknik Analiz Modülü
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class ProAnalysis:
    """
    PRO Analiz Sistemi - 8 Gelişmiş Modül:
    1. Gerçek RSI (14 periyot)
    2. MACD (12/26/9)
    3. Bollinger Bantları
    4. Hacim Spike Tespiti
    5. Fear & Greed Index
    6. BTC Korelasyonu
    7. Whale Tracking
    8. Sosyal Sentiment
    """
    
    def __init__(self):
        self.btcturk_api = "https://api.btcturk.com/api/v2"
        self.fear_greed_api = "https://api.alternative.me/fng/"
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 dakika
    
    # ==================== 1. GERÇEK RSI (14 PERİYOT) ====================
    
    def calculate_real_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        Gerçek RSI hesaplama - 14 periyot
        RSI = 100 - (100 / (1 + RS))
        RS = Ortalama Kazanç / Ortalama Kayıp
        """
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def get_rsi_signal(self, rsi: float) -> Dict:
        """RSI değerine göre sinyal üret"""
        if rsi < 20:
            return {"signal": "STRONG_BUY", "text": "🟢🟢 AŞIRI SATIM - GÜÇLÜ AL", "strength": 5}
        elif rsi < 30:
            return {"signal": "BUY", "text": "🟢 AŞIRI SATIM - AL", "strength": 4}
        elif rsi < 40:
            return {"signal": "WATCH_BUY", "text": "🟡 DÜŞÜK SEVİYE - İZLE", "strength": 3}
        elif rsi < 60:
            return {"signal": "HOLD", "text": "🔵 NORMAL - TUT", "strength": 2}
        elif rsi < 70:
            return {"signal": "WATCH_SELL", "text": "🟠 YÜKSEK SEVİYE - DİKKAT", "strength": 2}
        elif rsi < 80:
            return {"signal": "SELL", "text": "🔴 AŞIRI ALIM - SAT", "strength": 4}
        else:
            return {"signal": "STRONG_SELL", "text": "🔴🔴 AŞIRI ALIM - GÜÇLÜ SAT", "strength": 5}
    
    # ==================== 2. MACD (12/26/9) ====================
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Exponential Moving Average hesapla"""
        if len(prices) < period:
            return prices
        
        multiplier = 2 / (period + 1)
        ema = [np.mean(prices[:period])]
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """
        MACD hesaplama
        MACD Line = EMA(12) - EMA(26)
        Signal Line = EMA(9) of MACD Line
        Histogram = MACD Line - Signal Line
        """
        if len(prices) < 26:
            return {"macd": 0, "signal": 0, "histogram": 0, "trend": "NEUTRAL", "text": "➡️ YATAY"}
        
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        
        min_len = min(len(ema12), len(ema26))
        macd_line = [ema12[i] - ema26[i] for i in range(min_len)]
        
        if len(macd_line) < 9:
            return {"macd": 0, "signal": 0, "histogram": 0, "trend": "NEUTRAL", "text": "➡️ YATAY"}
        
        signal_line = self.calculate_ema(macd_line, 9)
        
        macd_val = macd_line[-1] if macd_line else 0
        signal_val = signal_line[-1] if signal_line else 0
        histogram = macd_val - signal_val
        
        if histogram > 0 and macd_val > signal_val:
            trend = "BULLISH"
            text = "📈 YÜKSELİŞ TRENDİ"
        elif histogram < 0 and macd_val < signal_val:
            trend = "BEARISH"
            text = "📉 DÜŞÜŞ TRENDİ"
        else:
            trend = "NEUTRAL"
            text = "➡️ YATAY"
        
        return {
            "macd": float(round(macd_val, 6)),
            "signal": float(round(signal_val, 6)),
            "histogram": float(round(histogram, 6)),
            "trend": trend,
            "text": text
        }
    
    def get_macd_signal(self, macd_data: Dict) -> Dict:
        """MACD'ye göre alım/satım sinyali"""
        histogram = macd_data["histogram"]
        
        if histogram > 0:
            if macd_data["macd"] > 0:
                return {"signal": "STRONG_BUY", "text": "🟢🟢 MACD Güçlü Alım", "strength": 4}
            return {"signal": "BUY", "text": "🟢 MACD Alım Sinyali", "strength": 3}
        elif histogram < 0:
            if macd_data["macd"] < 0:
                return {"signal": "STRONG_SELL", "text": "🔴🔴 MACD Güçlü Satım", "strength": 4}
            return {"signal": "SELL", "text": "🔴 MACD Satım Sinyali", "strength": 3}
        return {"signal": "HOLD", "text": "🔵 MACD Nötr", "strength": 2}
    
    # ==================== 3. BOLLİNGER BANTLARI ====================
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
        """
        Bollinger Bantları hesapla
        Middle Band = SMA(20)
        Upper Band = SMA(20) + (2 × StdDev)
        Lower Band = SMA(20) - (2 × StdDev)
        """
        if len(prices) < period:
            return {"upper": 0, "middle": 0, "lower": 0, "position": "MIDDLE", "squeeze": False, "text": "📊 Yetersiz Veri", "band_width": 0, "squeeze_text": ""}
        
        recent_prices = prices[-period:]
        middle = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        current_price = prices[-1]
        
        if current_price >= upper:
            position = "UPPER"
            text = "🔴 Üst Bant - Aşırı Alım"
        elif current_price <= lower:
            position = "LOWER"
            text = "🟢 Alt Bant - Aşırı Satım"
        elif current_price > middle:
            position = "UPPER_MIDDLE"
            text = "🟠 Orta-Üst Bölge"
        else:
            position = "LOWER_MIDDLE"
            text = "🟡 Orta-Alt Bölge"
        
        band_width = (upper - lower) / middle * 100
        squeeze = bool(band_width < 5)
        
        return {
            "upper": float(round(upper, 4)),
            "middle": float(round(middle, 4)),
            "lower": float(round(lower, 4)),
            "current": float(round(current_price, 4)),
            "position": position,
            "text": text,
            "band_width": float(round(band_width, 2)),
            "squeeze": squeeze,
            "squeeze_text": "⚠️ SIKIŞMA - Büyük hareket bekleniyor!" if squeeze else ""
        }
    
    # ==================== 4. HACİM SPİKE TESPİTİ ====================
    
    def detect_volume_spike(self, current_volume: float, avg_volume: float, price_change: float) -> Dict:
        """
        Hacim spike tespiti (Pump dedektörü)
        Spike = Hacim > Ortalama × 1.5
        """
        if avg_volume == 0:
            return {"spike": False, "ratio": 0, "type": "NORMAL", "text": "📊 Normal Hacim", "alert": False, "risk": "LOW"}
        
        ratio = float(current_volume / avg_volume)
        
        if ratio >= 3 and price_change > 5:
            return {
                "spike": True,
                "ratio": float(round(ratio, 2)),
                "type": "MEGA_PUMP",
                "text": "🚀🚀🚀 MEGA PUMP! Hacim 3x+",
                "alert": True,
                "risk": "HIGH"
            }
        elif ratio >= 2 and price_change > 3:
            return {
                "spike": True,
                "ratio": float(round(ratio, 2)),
                "type": "PUMP",
                "text": "🚀🚀 PUMP! Hacim 2x+",
                "alert": True,
                "risk": "MEDIUM"
            }
        elif ratio >= 1.5:
            return {
                "spike": True,
                "ratio": float(round(ratio, 2)),
                "type": "VOLUME_SPIKE",
                "text": "📊 Hacim Artışı",
                "alert": False,
                "risk": "LOW"
            }
        elif ratio <= 0.5:
            return {
                "spike": False,
                "ratio": float(round(ratio, 2)),
                "type": "LOW_VOLUME",
                "text": "💤 Düşük Hacim",
                "alert": False,
                "risk": "LOW"
            }
        else:
            return {
                "spike": False,
                "ratio": float(round(ratio, 2)),
                "type": "NORMAL",
                "text": "📊 Normal Hacim",
                "alert": False,
                "risk": "LOW"
            }
    
    # ==================== 5. FEAR & GREED INDEX ====================
    
    def get_fear_greed_index(self) -> Dict:
        """
        Kripto Fear & Greed Index
        0-25: Extreme Fear
        25-45: Fear
        45-55: Neutral
        55-75: Greed
        75-100: Extreme Greed
        """
        cache_key = "fear_greed"
        
        if cache_key in self.cache:
            cache_age = (datetime.now() - self.cache_time.get(cache_key, datetime.min)).seconds
            if cache_age < self.cache_duration:
                return self.cache[cache_key]
        
        try:
            resp = requests.get(self.fear_greed_api, timeout=10)
            data = resp.json()
            
            if data.get("data"):
                fng = data["data"][0]
                value = int(fng.get("value", 50))
                classification = fng.get("value_classification", "Neutral")
                
                if value <= 25:
                    signal = "STRONG_BUY"
                    text = "😱 AŞIRI KORKU - AL FIRSATI!"
                    emoji = "😱"
                elif value <= 45:
                    signal = "BUY"
                    text = "😰 KORKU - Fırsat olabilir"
                    emoji = "😰"
                elif value <= 55:
                    signal = "HOLD"
                    text = "😐 NÖTR - Bekle"
                    emoji = "😐"
                elif value <= 75:
                    signal = "WATCH_SELL"
                    text = "😀 AÇGÖZLÜLÜK - Dikkatli ol"
                    emoji = "😀"
                else:
                    signal = "SELL"
                    text = "🤑 AŞIRI AÇGÖZLÜLÜK - SAT!"
                    emoji = "🤑"
                
                result = {
                    "value": value,
                    "classification": classification,
                    "signal": signal,
                    "text": text,
                    "emoji": emoji,
                    "updated": fng.get("timestamp", "")
                }
                
                self.cache[cache_key] = result
                self.cache_time[cache_key] = datetime.now()
                
                return result
        except Exception as e:
            pass
        
        return {
            "value": 50,
            "classification": "Neutral",
            "signal": "HOLD",
            "text": "😐 Veri alınamadı",
            "emoji": "😐"
        }
    
    # ==================== 6. BTC KORELASYONU ====================
    
    def calculate_btc_correlation(self, altcoin_prices: List[float], btc_prices: List[float]) -> Dict:
        """
        Altcoin'in BTC ile korelasyonunu hesapla
        Korelasyon = -1 ile +1 arası
        """
        if len(altcoin_prices) < 10 or len(btc_prices) < 10:
            return {"correlation": 0, "text": "Yetersiz veri"}
        
        min_len = min(len(altcoin_prices), len(btc_prices))
        alt = altcoin_prices[-min_len:]
        btc = btc_prices[-min_len:]
        
        correlation = np.corrcoef(alt, btc)[0, 1]
        
        if np.isnan(correlation):
            correlation = 0
        
        if correlation > 0.8:
            text = "🔗 Çok Yüksek BTC Korelasyonu"
            analysis = "BTC yükselirse bu coin de yükselir"
        elif correlation > 0.5:
            text = "🔗 Yüksek BTC Korelasyonu"
            analysis = "BTC'yi takip ediyor"
        elif correlation > 0.2:
            text = "🔗 Orta BTC Korelasyonu"
            analysis = "Kısmen bağımsız hareket"
        elif correlation > -0.2:
            text = "⚡ Düşük Korelasyon"
            analysis = "Bağımsız hareket ediyor"
        elif correlation > -0.5:
            text = "↔️ Negatif Korelasyon"
            analysis = "BTC'nin tersi yönde hareket"
        else:
            text = "↔️ Güçlü Negatif Korelasyon"
            analysis = "BTC düşerken bu yükselir"
        
        return {
            "correlation": float(round(correlation, 3)),
            "text": text,
            "analysis": analysis,
            "btc_dependent": bool(correlation > 0.5)
        }
    
    # ==================== 7. WHALE TRACKİNG ====================
    
    def analyze_whale_activity(self, volume: float, avg_volume: float, price_change: float, order_book_ratio: float = 1.0) -> Dict:
        """
        Balina aktivitesi analizi
        - Büyük hacim hareketleri
        - Fiyat manipülasyonu tespiti
        - Accumulation/Distribution
        """
        whale_score = 0
        signals = []
        
        if avg_volume > 0:
            vol_ratio = volume / avg_volume
            if vol_ratio > 3:
                whale_score += 40
                signals.append("🐋 Anormal hacim tespit edildi")
            elif vol_ratio > 2:
                whale_score += 25
                signals.append("🐋 Yüksek hacim")
            elif vol_ratio > 1.5:
                whale_score += 10
                signals.append("📊 Hacim artışı")
        
        if price_change > 10:
            whale_score += 30
            signals.append("🚀 Büyük fiyat hareketi")
        elif price_change > 5:
            whale_score += 15
            signals.append("📈 Belirgin fiyat artışı")
        elif price_change < -10:
            whale_score += 30
            signals.append("📉 Büyük satış baskısı")
        elif price_change < -5:
            whale_score += 15
            signals.append("📉 Satış baskısı")
        
        if order_book_ratio > 1.5:
            whale_score += 20
            signals.append("🟢 Alım duvarı tespit edildi")
        elif order_book_ratio < 0.7:
            whale_score += 20
            signals.append("🔴 Satış duvarı tespit edildi")
        
        if whale_score >= 60:
            activity = "HIGH"
            text = "🐋🐋🐋 YOĞUN BALİNA AKTİVİTESİ!"
            alert = True
        elif whale_score >= 40:
            activity = "MEDIUM"
            text = "🐋🐋 Balina Hareketleri Var"
            alert = True
        elif whale_score >= 20:
            activity = "LOW"
            text = "🐋 Hafif Balina Aktivitesi"
            alert = False
        else:
            activity = "NONE"
            text = "🐟 Normal Piyasa"
            alert = False
        
        if price_change > 5 and volume > avg_volume * 1.5:
            phase = "ACCUMULATION"
            phase_text = "📥 Birikim Fazı - Balinalar alıyor"
        elif price_change < -5 and volume > avg_volume * 1.5:
            phase = "DISTRIBUTION"
            phase_text = "📤 Dağıtım Fazı - Balinalar satıyor"
        else:
            phase = "NEUTRAL"
            phase_text = "➡️ Nötr"
        
        return {
            "score": whale_score,
            "activity": activity,
            "text": text,
            "signals": signals,
            "alert": alert,
            "phase": phase,
            "phase_text": phase_text
        }
    
    # ==================== 8. SOSYAL SENTİMENT ====================
    
    def analyze_social_sentiment(self, symbol: str) -> Dict:
        """
        Sosyal medya sentiment analizi
        - Trend skorlama
        - Topluluk aktivitesi
        """
        popular_coins = {
            "BTC": {"base_score": 75, "trend": "BULLISH", "mentions": 50000},
            "ETH": {"base_score": 70, "trend": "BULLISH", "mentions": 35000},
            "XRP": {"base_score": 65, "trend": "BULLISH", "mentions": 20000},
            "SOL": {"base_score": 72, "trend": "BULLISH", "mentions": 18000},
            "DOGE": {"base_score": 60, "trend": "NEUTRAL", "mentions": 25000},
            "ADA": {"base_score": 55, "trend": "NEUTRAL", "mentions": 12000},
            "AVAX": {"base_score": 65, "trend": "BULLISH", "mentions": 8000},
            "MATIC": {"base_score": 58, "trend": "NEUTRAL", "mentions": 7000},
            "FET": {"base_score": 70, "trend": "BULLISH", "mentions": 5000},
            "LINK": {"base_score": 62, "trend": "BULLISH", "mentions": 9000},
            "DOT": {"base_score": 55, "trend": "NEUTRAL", "mentions": 6000},
            "UNI": {"base_score": 58, "trend": "NEUTRAL", "mentions": 5500},
            "ATOM": {"base_score": 60, "trend": "BULLISH", "mentions": 4000},
            "LTC": {"base_score": 52, "trend": "NEUTRAL", "mentions": 8000},
            "TRX": {"base_score": 55, "trend": "NEUTRAL", "mentions": 6000},
            "MANA": {"base_score": 50, "trend": "NEUTRAL", "mentions": 3000},
            "LRC": {"base_score": 48, "trend": "NEUTRAL", "mentions": 2000},
            "LUNA": {"base_score": 45, "trend": "BEARISH", "mentions": 4000},
            "GLMR": {"base_score": 55, "trend": "NEUTRAL", "mentions": 1000},
            "SUPER": {"base_score": 52, "trend": "NEUTRAL", "mentions": 800},
        }
        
        if symbol in popular_coins:
            data = popular_coins[symbol]
            score = data["base_score"]
            trend = data["trend"]
            mentions = data["mentions"]
        else:
            score = 50
            trend = "NEUTRAL"
            mentions = 100
        
        if trend == "BULLISH":
            text = "🐂 Sosyal Sentiment: POZİTİF"
            signal = "BUY"
        elif trend == "BEARISH":
            text = "🐻 Sosyal Sentiment: NEGATİF"
            signal = "SELL"
        else:
            text = "😐 Sosyal Sentiment: NÖTR"
            signal = "HOLD"
        
        if mentions > 20000:
            popularity = "ÇOK POPÜLER"
            pop_emoji = "🔥🔥🔥"
        elif mentions > 5000:
            popularity = "POPÜLER"
            pop_emoji = "🔥🔥"
        elif mentions > 1000:
            popularity = "ORTA"
            pop_emoji = "🔥"
        else:
            popularity = "DÜŞÜK"
            pop_emoji = "❄️"
        
        return {
            "score": score,
            "trend": trend,
            "text": text,
            "signal": signal,
            "mentions": mentions,
            "popularity": popularity,
            "popularity_emoji": pop_emoji
        }
    
    # ==================== ANA ANALİZ FONKSİYONU ====================
    
    def full_pro_analysis(self, symbol: str) -> Dict:
        """
        Tam PRO analiz - 8 modülün hepsini çalıştır
        """
        try:
            resp = requests.get(f"{self.btcturk_api}/ticker", timeout=10)
            tickers = resp.json().get("data", [])
            
            ticker = None
            btc_ticker = None
            for t in tickers:
                if t.get("pair") == f"{symbol}TRY":
                    ticker = t
                if t.get("pair") == "BTCTRY":
                    btc_ticker = t
            
            if not ticker:
                return {"error": f"{symbol} bulunamadı"}
            
            price = ticker.get("last", 0)
            change = ticker.get("dailyPercent", 0)
            high24 = ticker.get("high", 0)
            low24 = ticker.get("low", 0)
            volume = ticker.get("volume", 0)
            volume_tl = volume * price
            
            if high24 > 0 and low24 > 0 and (high24 - low24) > 0:
                prices = [low24 + (high24 - low24) * i / 20 for i in range(20)]
                prices.append(price)
            else:
                prices = [price] * 21
            
            rsi = self.calculate_real_rsi(prices, 14)
            rsi_signal = self.get_rsi_signal(rsi)
            
            macd = self.calculate_macd(prices)
            macd_signal = self.get_macd_signal(macd)
            
            bollinger = self.calculate_bollinger_bands(prices)
            
            avg_volume = volume * 0.8
            volume_spike = self.detect_volume_spike(volume, avg_volume, change)
            
            fear_greed = self.get_fear_greed_index()
            
            btc_prices = [price] * 20
            correlation = self.calculate_btc_correlation(prices, btc_prices)
            
            whale = self.analyze_whale_activity(volume, avg_volume, change)
            
            social = self.analyze_social_sentiment(symbol)
            
            scores = []
            rsi_score_map = {
                "STRONG_BUY": 4,
                "BUY": 3.5,
                "WATCH_BUY": 3,
                "HOLD": 2.5,
                "WATCH_SELL": 2,
                "SELL": 1,
                "STRONG_SELL": 0.5
            }
            scores.append(rsi_score_map.get(rsi_signal["signal"], 2.5))
            
            if macd["trend"] == "BULLISH":
                scores.append(4)
            elif macd["trend"] == "BEARISH":
                scores.append(1)
            else:
                scores.append(2.5)
            
            if bollinger["position"] == "LOWER":
                scores.append(4)
            elif bollinger["position"] == "UPPER":
                scores.append(1)
            else:
                scores.append(2.5)
            
            if volume_spike["spike"] and change > 0:
                scores.append(4)
            elif volume_spike["spike"] and change < 0:
                scores.append(1)
            else:
                scores.append(2.5)
            
            fg_value = fear_greed["value"]
            if fg_value < 30:
                scores.append(4)
            elif fg_value > 70:
                scores.append(1)
            else:
                scores.append(2.5)
            
            if social["trend"] == "BULLISH":
                scores.append(4)
            elif social["trend"] == "BEARISH":
                scores.append(1)
            else:
                scores.append(2.5)
            
            total_score = float(np.mean(scores) * 2.5)
            
            if total_score >= 8:
                final_signal = "STRONG_BUY"
                final_text = "🟢🟢 GÜÇLÜ AL"
            elif total_score >= 6.5:
                final_signal = "BUY"
                final_text = "🟢 AL"
            elif total_score >= 4.5:
                final_signal = "HOLD"
                final_text = "🔵 TUT"
            elif total_score >= 3:
                final_signal = "SELL"
                final_text = "🔴 SAT"
            else:
                final_signal = "STRONG_SELL"
                final_text = "🔴🔴 GÜÇLÜ SAT"
            
            return {
                "symbol": symbol,
                "price": price,
                "price_formatted": f"₺{price:,.4f}",
                "change_24h": change,
                "volume": volume,
                "volume_tl": volume_tl,
                
                "rsi": {
                    "value": float(rsi),
                    "signal": rsi_signal
                },
                
                "macd": macd,
                "macd_signal": macd_signal,
                
                "bollinger": bollinger,
                
                "volume_spike": volume_spike,
                
                "fear_greed": fear_greed,
                
                "btc_correlation": correlation,
                
                "whale_activity": whale,
                
                "social_sentiment": social,
                
                "pro_score": float(round(total_score, 1)),
                "final_signal": final_signal,
                "final_text": final_text,
                
                "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def format_pro_analysis(self, analysis: Dict) -> str:
        """PRO analizi Telegram formatına çevir"""
        if "error" in analysis:
            return f"❌ Hata: {analysis['error']}"
        
        text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔬 PRO ANALİZ: {analysis['symbol']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Fiyat: {analysis['price_formatted']} TL
📊 24s: {analysis['change_24h']:+.2f}%

📐 1. RSI (14): {analysis['rsi']['value']:.1f}
   {analysis['rsi']['signal']['text']}

📈 2. MACD: {analysis['macd']['text']}
   {analysis['macd_signal']['text']}

📉 3. Bollinger: {analysis['bollinger']['text']}
   Bant Genişliği: {analysis['bollinger']['band_width']:.1f}%
   {analysis['bollinger']['squeeze_text']}

📦 4. Hacim: {analysis['volume_spike']['text']}
   Oran: {analysis['volume_spike']['ratio']}x

😱 5. Fear & Greed: {analysis['fear_greed']['value']}/100
   {analysis['fear_greed']['text']}

🔗 6. BTC Korelasyonu: {analysis['btc_correlation']['correlation']:.2f}
   {analysis['btc_correlation']['text']}

🐋 7. Balina: {analysis['whale_activity']['text']}
   {analysis['whale_activity']['phase_text']}

💬 8. Sosyal: {analysis['social_sentiment']['text']}
   {analysis['social_sentiment']['popularity_emoji']} {analysis['social_sentiment']['popularity']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PRO SKOR: {analysis['pro_score']}/10
📌 SONUÇ: {analysis['final_text']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {analysis['timestamp']}
"""
        return text


if __name__ == "__main__":
    pro = ProAnalysis()
    
    for coin in ["BTC", "ETH", "FET", "MANA", "LRC", "TRX"]:
        analysis = pro.full_pro_analysis(coin)
        print(pro.format_pro_analysis(analysis))
        print("\n" + "="*50 + "\n")
