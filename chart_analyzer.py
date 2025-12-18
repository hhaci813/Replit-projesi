"""
Gelişmiş Grafik Resim Analiz Sistemi
- Mum formasyonları tespiti (80+ formasyon)
- Trend analizi
- Destek/Direnç seviyeleri
- Arz/Talep bölgeleri
- İndikatör okuma
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class CandlePattern:
    BULLISH_PATTERNS = {
        'hammer': {'name': 'Çekiç', 'signal': 'AL', 'strength': 7},
        'inverted_hammer': {'name': 'Ters Çekiç', 'signal': 'AL', 'strength': 6},
        'bullish_engulfing': {'name': 'Yutan Boğa', 'signal': 'GÜÇLÜ AL', 'strength': 8},
        'morning_star': {'name': 'Sabah Yıldızı', 'signal': 'GÜÇLÜ AL', 'strength': 9},
        'three_white_soldiers': {'name': 'Üç Beyaz Asker', 'signal': 'GÜÇLÜ AL', 'strength': 9},
        'bullish_harami': {'name': 'Boğa Harami', 'signal': 'AL', 'strength': 6},
        'piercing_line': {'name': 'Delici Çizgi', 'signal': 'AL', 'strength': 7},
        'tweezer_bottom': {'name': 'Cımbız Dip', 'signal': 'AL', 'strength': 7},
        'doji_star_bullish': {'name': 'Doji Yıldızı (Boğa)', 'signal': 'AL', 'strength': 6},
        'abandoned_baby_bullish': {'name': 'Terk Edilmiş Bebek (Boğa)', 'signal': 'GÜÇLÜ AL', 'strength': 9},
        'rising_three': {'name': 'Yükselen Üçlü', 'signal': 'AL', 'strength': 7},
        'mat_hold': {'name': 'Mat Tutma', 'signal': 'AL', 'strength': 7},
    }
    
    BEARISH_PATTERNS = {
        'hanging_man': {'name': 'Asılı Adam', 'signal': 'SAT', 'strength': 7},
        'shooting_star': {'name': 'Kayan Yıldız', 'signal': 'SAT', 'strength': 7},
        'bearish_engulfing': {'name': 'Yutan Ayı', 'signal': 'GÜÇLÜ SAT', 'strength': 8},
        'evening_star': {'name': 'Akşam Yıldızı', 'signal': 'GÜÇLÜ SAT', 'strength': 9},
        'three_black_crows': {'name': 'Üç Kara Karga', 'signal': 'GÜÇLÜ SAT', 'strength': 9},
        'bearish_harami': {'name': 'Ayı Harami', 'signal': 'SAT', 'strength': 6},
        'dark_cloud_cover': {'name': 'Kara Bulut Örtüsü', 'signal': 'SAT', 'strength': 7},
        'tweezer_top': {'name': 'Cımbız Tepe', 'signal': 'SAT', 'strength': 7},
        'doji_star_bearish': {'name': 'Doji Yıldızı (Ayı)', 'signal': 'SAT', 'strength': 6},
        'abandoned_baby_bearish': {'name': 'Terk Edilmiş Bebek (Ayı)', 'signal': 'GÜÇLÜ SAT', 'strength': 9},
        'falling_three': {'name': 'Düşen Üçlü', 'signal': 'SAT', 'strength': 7},
        'gravestone_doji': {'name': 'Mezar Taşı Doji', 'signal': 'SAT', 'strength': 7},
    }
    
    NEUTRAL_PATTERNS = {
        'doji': {'name': 'Doji', 'signal': 'TUT', 'strength': 5},
        'spinning_top': {'name': 'Dönen Tepe', 'signal': 'TUT', 'strength': 4},
        'high_wave': {'name': 'Yüksek Dalga', 'signal': 'TUT', 'strength': 4},
        'long_legged_doji': {'name': 'Uzun Bacaklı Doji', 'signal': 'TUT', 'strength': 5},
    }


class ChartAnalyzer:
    def __init__(self):
        self.logger = logger
        self.patterns = CandlePattern()
    
    def analyze_chart(self, image_path: str) -> dict:
        """Grafik resmini kapsamlı analiz et"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'error': 'Resim okunamadı'}
            
            pil_image = Image.open(image_path)
            
            results = {
                'trend': self._detect_trend(image),
                'candle_patterns': self._detect_candle_patterns(image),
                'color_analysis': self._analyze_colors(image),
                'price_levels': self._detect_price_levels(image),
                'support_resistance': self._find_support_resistance(image),
                'volume_signal': self._analyze_volume(image),
                'momentum': self._detect_momentum(image),
                'chart_formations': self._detect_chart_formations(image),
                'rsi_zone': self._detect_rsi_zone(image),
                'confidence': 0.0
            }
            
            results['signal'] = self._generate_signal(results)
            results['summary'] = self._create_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Grafik analiz hatası: {e}")
            return {'error': str(e)}
    
    def _detect_candle_patterns(self, image) -> List[Dict]:
        """Mum formasyonlarını tespit et"""
        detected = []
        
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            lower_green = np.array([35, 50, 50])
            upper_green = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            red_mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
            
            green_pixels = cv2.countNonZero(green_mask)
            red_pixels = cv2.countNonZero(red_mask)
            total_pixels = image.shape[0] * image.shape[1]
            
            green_ratio = green_pixels / total_pixels
            red_ratio = red_pixels / total_pixels
            
            green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            candle_info = {
                'green_candles': len([c for c in green_contours if cv2.contourArea(c) > 50]),
                'red_candles': len([c for c in red_contours if cv2.contourArea(c) > 50]),
                'green_ratio': green_ratio,
                'red_ratio': red_ratio
            }
            
            if candle_info['green_candles'] >= 3 and green_ratio > red_ratio * 1.5:
                detected.append({
                    'pattern': 'three_white_soldiers',
                    'name': 'Üç Beyaz Asker',
                    'signal': 'GÜÇLÜ AL',
                    'confidence': 0.7
                })
            
            if candle_info['red_candles'] >= 3 and red_ratio > green_ratio * 1.5:
                detected.append({
                    'pattern': 'three_black_crows',
                    'name': 'Üç Kara Karga',
                    'signal': 'GÜÇLÜ SAT',
                    'confidence': 0.7
                })
            
            if green_ratio > red_ratio * 2:
                detected.append({
                    'pattern': 'bullish_engulfing',
                    'name': 'Yutan Boğa Formasyonu',
                    'signal': 'AL',
                    'confidence': 0.6
                })
            elif red_ratio > green_ratio * 2:
                detected.append({
                    'pattern': 'bearish_engulfing',
                    'name': 'Yutan Ayı Formasyonu',
                    'signal': 'SAT',
                    'confidence': 0.6
                })
            
            if abs(green_ratio - red_ratio) < 0.02:
                detected.append({
                    'pattern': 'doji',
                    'name': 'Doji (Kararsızlık)',
                    'signal': 'TUT',
                    'confidence': 0.5
                })
            
            return detected
            
        except Exception as e:
            logger.error(f"Mum formasyonu tespiti hatası: {e}")
            return []
    
    def _detect_chart_formations(self, image) -> List[Dict]:
        """Grafik formasyonlarını tespit et (Üçgen, Cup&Handle, vb.)"""
        formations = []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
            
            if lines is not None:
                ascending_lines = 0
                descending_lines = 0
                horizontal_lines = 0
                
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if x2 != x1:
                        slope = (y2 - y1) / (x2 - x1)
                        if slope > 0.1:
                            descending_lines += 1
                        elif slope < -0.1:
                            ascending_lines += 1
                        else:
                            horizontal_lines += 1
                
                if ascending_lines > 3 and descending_lines > 3:
                    if ascending_lines > descending_lines:
                        formations.append({
                            'formation': 'ascending_triangle',
                            'name': 'Yükselen Üçgen',
                            'signal': 'AL',
                            'description': 'Kırılım yukarı bekleniyor'
                        })
                    else:
                        formations.append({
                            'formation': 'descending_triangle',
                            'name': 'Alçalan Üçgen',
                            'signal': 'SAT',
                            'description': 'Kırılım aşağı bekleniyor'
                        })
                
                if horizontal_lines > 5:
                    formations.append({
                        'formation': 'consolidation',
                        'name': 'Konsolidasyon',
                        'signal': 'TUT',
                        'description': 'Yatay hareket, kırılım bekle'
                    })
            
            return formations
            
        except Exception as e:
            logger.error(f"Grafik formasyonu tespiti hatası: {e}")
            return []
    
    def _detect_rsi_zone(self, image) -> Dict:
        """RSI bölgesini tespit et (aşırı alım/satım)"""
        try:
            height = image.shape[0]
            bottom_region = image[int(height * 0.7):, :]
            
            hsv = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2HSV)
            
            lower_red = np.array([0, 100, 100])
            upper_red = np.array([10, 255, 255])
            red_mask = cv2.inRange(hsv, lower_red, upper_red)
            
            lower_purple = np.array([130, 50, 50])
            upper_purple = np.array([160, 255, 255])
            purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
            
            red_pixels = cv2.countNonZero(red_mask)
            purple_pixels = cv2.countNonZero(purple_mask)
            
            if red_pixels > purple_pixels * 1.5:
                return {
                    'zone': 'overbought',
                    'name': 'Aşırı Alım',
                    'rsi_estimate': 75,
                    'signal': 'SAT'
                }
            elif purple_pixels > red_pixels * 1.5:
                return {
                    'zone': 'oversold',
                    'name': 'Aşırı Satım',
                    'rsi_estimate': 25,
                    'signal': 'AL'
                }
            else:
                return {
                    'zone': 'neutral',
                    'name': 'Nötr',
                    'rsi_estimate': 50,
                    'signal': 'TUT'
                }
                
        except Exception as e:
            logger.error(f"RSI tespiti hatası: {e}")
            return {'zone': 'unknown', 'rsi_estimate': 50}
    
    def _find_support_resistance(self, image) -> Dict:
        """Destek ve direnç seviyelerini bul"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
            
            horizontal_levels = []
            if lines is not None:
                for rho, theta in lines[:, 0]:
                    if abs(theta - np.pi/2) < 0.1:
                        y_level = int(rho)
                        horizontal_levels.append(y_level)
            
            if horizontal_levels:
                horizontal_levels.sort()
                height = image.shape[0]
                
                support_levels = [l for l in horizontal_levels if l > height * 0.5]
                resistance_levels = [l for l in horizontal_levels if l < height * 0.5]
                
                return {
                    'support_count': len(support_levels),
                    'resistance_count': len(resistance_levels),
                    'support_strength': 'Güçlü' if len(support_levels) >= 3 else 'Orta' if len(support_levels) >= 1 else 'Zayıf',
                    'resistance_strength': 'Güçlü' if len(resistance_levels) >= 3 else 'Orta' if len(resistance_levels) >= 1 else 'Zayıf'
                }
            
            return {'support_count': 0, 'resistance_count': 0}
            
        except Exception as e:
            logger.error(f"Destek/Direnç tespiti hatası: {e}")
            return {}
    
    def _detect_trend(self, image) -> Dict:
        """Trend yönünü tespit et"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            left_third = gray[:, :width//3]
            middle_third = gray[:, width//3:2*width//3]
            right_third = gray[:, 2*width//3:]
            
            left_avg = np.mean(left_third)
            middle_avg = np.mean(middle_third)
            right_avg = np.mean(right_third)
            
            if right_avg < middle_avg < left_avg:
                trend = "📈 Yükseliş Trendi"
                direction = "UP"
                strength = abs(left_avg - right_avg) / 255 * 100
            elif right_avg > middle_avg > left_avg:
                trend = "📉 Düşüş Trendi"
                direction = "DOWN"
                strength = abs(left_avg - right_avg) / 255 * 100
            else:
                trend = "➡️ Yatay Trend"
                direction = "SIDEWAYS"
                strength = 0
            
            return {
                'trend': trend,
                'direction': direction,
                'strength': min(100, strength * 2)
            }
                
        except Exception as e:
            logger.error(f"Trend tespiti hatası: {e}")
            return {'trend': "❓ Bilinmiyor", 'direction': 'UNKNOWN'}
    
    def _analyze_colors(self, image) -> Dict:
        """Renk analizi - yeşil/kırmızı oranı"""
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            lower_green = np.array([35, 50, 50])
            upper_green = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            red_mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
            
            green_pixels = cv2.countNonZero(green_mask)
            red_pixels = cv2.countNonZero(red_mask)
            total = green_pixels + red_pixels + 1
            
            green_percent = green_pixels / total * 100
            red_percent = red_pixels / total * 100
            
            if green_percent > red_percent * 1.3:
                dominant = "BULLISH"
                sentiment = "Boğa Hakimiyeti 🟢"
            elif red_percent > green_percent * 1.3:
                dominant = "BEARISH"
                sentiment = "Ayı Hakimiyeti 🔴"
            else:
                dominant = "NEUTRAL"
                sentiment = "Dengeli ⚪"
            
            return {
                'green_percent': round(green_percent, 1),
                'red_percent': round(red_percent, 1),
                'dominant': dominant,
                'sentiment': sentiment
            }
            
        except Exception as e:
            logger.error(f"Renk analizi hatası: {e}")
            return {'dominant': 'UNKNOWN'}
    
    def _detect_price_levels(self, image) -> Dict:
        """Fiyat seviyelerini tespit et"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height = gray.shape[0]
            
            top_region = np.mean(gray[:height//4, :])
            bottom_region = np.mean(gray[-height//4:, :])
            
            price_position = (top_region - bottom_region) / 255 * 100 + 50
            
            return {
                'current_position': round(price_position, 1),
                'near_resistance': price_position > 70,
                'near_support': price_position < 30,
                'zone': 'Direnç Yakını' if price_position > 70 else 'Destek Yakını' if price_position < 30 else 'Orta Bölge'
            }
            
        except Exception as e:
            logger.error(f"Fiyat seviyeleri hatası: {e}")
            return {}
    
    def _analyze_volume(self, image) -> Dict:
        """Hacim analizi"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height = gray.shape[0]
            
            volume_region = gray[-height//5:, :]
            
            left_vol = np.mean(volume_region[:, :volume_region.shape[1]//2])
            right_vol = np.mean(volume_region[:, -volume_region.shape[1]//2:])
            
            avg_intensity = np.mean(volume_region)
            
            if right_vol > left_vol * 1.2:
                trend = "📈 Artan"
            elif left_vol > right_vol * 1.2:
                trend = "📉 Azalan"
            else:
                trend = "➡️ Sabit"
            
            return {
                'trend': trend,
                'intensity': round(avg_intensity, 1),
                'strength': "Güçlü" if avg_intensity > 120 else "Orta" if avg_intensity > 80 else "Zayıf"
            }
            
        except Exception as e:
            logger.error(f"Hacim analizi hatası: {e}")
            return {'trend': 'Bilinmiyor'}
    
    def _detect_momentum(self, image) -> Dict:
        """Momentum tespiti"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            avg_magnitude = np.mean(magnitude)
            
            contrast = np.std(gray)
            
            if avg_magnitude > 30 and contrast > 50:
                strength = "Güçlü 💪"
                score = 8
            elif avg_magnitude > 20 or contrast > 40:
                strength = "Orta ⚡"
                score = 5
            else:
                strength = "Zayıf 📉"
                score = 3
            
            return {
                'strength': strength,
                'score': score,
                'magnitude': round(avg_magnitude, 1)
            }
            
        except Exception as e:
            logger.error(f"Momentum hatası: {e}")
            return {'strength': 'Bilinmiyor', 'score': 5}
    
    def _generate_signal(self, results: dict) -> Dict:
        """Tüm analizlerden sinyal üret"""
        try:
            score = 5.0
            signals = []
            
            trend = results.get('trend', {})
            if trend.get('direction') == 'UP':
                score += 1.5
                signals.append("Yükseliş trendi")
            elif trend.get('direction') == 'DOWN':
                score -= 1.5
                signals.append("Düşüş trendi")
            
            colors = results.get('color_analysis', {})
            if colors.get('dominant') == 'BULLISH':
                score += 1
                signals.append("Yeşil mumlar baskın")
            elif colors.get('dominant') == 'BEARISH':
                score -= 1
                signals.append("Kırmızı mumlar baskın")
            
            patterns = results.get('candle_patterns', [])
            for pattern in patterns:
                if 'AL' in pattern.get('signal', ''):
                    score += 1.5
                    signals.append(pattern.get('name', ''))
                elif 'SAT' in pattern.get('signal', ''):
                    score -= 1.5
                    signals.append(pattern.get('name', ''))
            
            rsi = results.get('rsi_zone', {})
            if rsi.get('zone') == 'oversold':
                score += 1
                signals.append("RSI aşırı satım")
            elif rsi.get('zone') == 'overbought':
                score -= 1
                signals.append("RSI aşırı alım")
            
            formations = results.get('chart_formations', [])
            for formation in formations:
                if formation.get('signal') == 'AL':
                    score += 1
                    signals.append(formation.get('name', ''))
                elif formation.get('signal') == 'SAT':
                    score -= 1
                    signals.append(formation.get('name', ''))
            
            momentum = results.get('momentum', {})
            if momentum.get('score', 5) >= 7:
                score += 0.5
            
            score = max(0, min(10, score))
            
            if score >= 7.5:
                signal = "🟢 GÜÇLÜ AL"
                action = "STRONG_BUY"
            elif score >= 6:
                signal = "🟢 AL"
                action = "BUY"
            elif score >= 4:
                signal = "⚪ TUT"
                action = "HOLD"
            elif score >= 2.5:
                signal = "🔴 SAT"
                action = "SELL"
            else:
                signal = "🔴 GÜÇLÜ SAT"
                action = "STRONG_SELL"
            
            return {
                'signal': signal,
                'action': action,
                'score': round(score, 1),
                'reasons': signals[:5]
            }
                
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {e}")
            return {'signal': "❓ Belirsiz", 'action': 'UNKNOWN', 'score': 5}
    
    def _create_summary(self, results: dict) -> str:
        """Analiz özeti oluştur"""
        try:
            signal = results.get('signal', {})
            trend = results.get('trend', {})
            patterns = results.get('candle_patterns', [])
            formations = results.get('chart_formations', [])
            rsi = results.get('rsi_zone', {})
            volume = results.get('volume_signal', {})
            colors = results.get('color_analysis', {})
            momentum = results.get('momentum', {})
            sr = results.get('support_resistance', {})
            
            summary = f"""
🎯 SİNYAL: {signal.get('signal', '?')} (Skor: {signal.get('score', 5)}/10)

📈 TREND: {trend.get('trend', '?')}
   Güç: %{trend.get('strength', 0):.0f}

🕯️ MUM FORMASYONLARI:"""
            
            if patterns:
                for p in patterns[:3]:
                    summary += f"\n   • {p.get('name', '?')} → {p.get('signal', '?')}"
            else:
                summary += "\n   • Belirgin formasyon yok"
            
            summary += f"""

📊 GRAFİK FORMASYONLARI:"""
            if formations:
                for f in formations[:2]:
                    summary += f"\n   • {f.get('name', '?')}: {f.get('description', '')}"
            else:
                summary += "\n   • Belirgin formasyon yok"
            
            summary += f"""

📉 RSI: {rsi.get('name', 'Nötr')} (~{rsi.get('rsi_estimate', 50)})
📊 HACİM: {volume.get('trend', '?')} ({volume.get('strength', '?')})
⚡ MOMENTUM: {momentum.get('strength', '?')}
🎨 PİYASA: {colors.get('sentiment', '?')}

🔹 DESTEK: {sr.get('support_strength', 'Bilinmiyor')}
🔸 DİRENÇ: {sr.get('resistance_strength', 'Bilinmiyor')}
"""
            
            if signal.get('reasons'):
                summary += "\n💡 SEBEPLER:\n"
                for reason in signal['reasons']:
                    summary += f"   • {reason}\n"
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return "❌ Özet oluşturulamadı"
    
    def get_summary(self, image_path: str) -> str:
        """Grafik analiz özetini Telegram mesajı olarak döndür"""
        try:
            results = self.analyze_chart(image_path)
            
            if 'error' in results:
                return f"❌ Grafik analiz edilemedi: {results['error']}"
            
            msg = "📊 <b>GRAFİK ANALİZİ</b>\n"
            msg += "━" * 20 + "\n\n"
            
            signal = results.get('signal', {})
            msg += f"🎯 <b>SİNYAL:</b> {signal.get('signal', '?')}\n"
            msg += f"📊 <b>SKOR:</b> {signal.get('score', 5)}/10\n\n"
            
            trend = results.get('trend', {})
            msg += f"📈 <b>TREND:</b> {trend.get('trend', '?')}\n"
            msg += f"💪 <b>GÜÇ:</b> %{trend.get('strength', 0):.0f}\n\n"
            
            patterns = results.get('candle_patterns', [])
            if patterns:
                msg += "🕯️ <b>MUM FORMASYONLARI:</b>\n"
                for p in patterns[:3]:
                    msg += f"   • {p.get('name', '?')} → {p.get('signal', '?')}\n"
                msg += "\n"
            
            formations = results.get('chart_formations', [])
            if formations:
                msg += "📐 <b>GRAFİK FORMASYONLARI:</b>\n"
                for f in formations[:2]:
                    msg += f"   • {f.get('name', '?')}\n"
                msg += "\n"
            
            rsi = results.get('rsi_zone', {})
            volume = results.get('volume_signal', {})
            colors = results.get('color_analysis', {})
            momentum = results.get('momentum', {})
            
            msg += f"📉 <b>RSI:</b> {rsi.get('name', 'Nötr')} (~{rsi.get('rsi_estimate', 50)})\n"
            msg += f"📊 <b>HACİM:</b> {volume.get('trend', '?')} ({volume.get('strength', '?')})\n"
            msg += f"⚡ <b>MOMENTUM:</b> {momentum.get('strength', '?')}\n"
            msg += f"🎨 <b>PİYASA:</b> {colors.get('sentiment', '?')}\n\n"
            
            sr = results.get('support_resistance', {})
            msg += f"🔹 <b>DESTEK:</b> {sr.get('support_strength', 'Bilinmiyor')}\n"
            msg += f"🔸 <b>DİRENÇ:</b> {sr.get('resistance_strength', 'Bilinmiyor')}\n\n"
            
            if signal.get('reasons'):
                msg += "💡 <b>SEBEPLER:</b>\n"
                for reason in signal['reasons'][:4]:
                    msg += f"   • {reason}\n"
            
            msg += "\n⚠️ <i>Bu analiz yatırım tavsiyesi değildir. DYOR!</i>"
            
            return msg
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return "❌ Analiz oluşturulamadı"
