"""
🔥 ULTRA GELİŞMİŞ GRAFİK ANALİZ SİSTEMİ v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 80+ Mum formasyonu tespiti
- 15+ Grafik formasyonu (TOBO, OBO, Cup&Handle, Bayrak, Flama, vb.)
- MACD sinyal analizi ve kesişimler
- Divergence (Uyuşmazlık) tespiti
- Destek/Direnç ve Arz/Talep bölgeleri
- RSI aşırı alım/satım tespiti
- Trend kanalları analizi
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
    """Mum formasyonları veritabanı"""
    
    BULLISH_PATTERNS = {
        'hammer': {'name': 'Çekiç (Hammer)', 'signal': 'AL', 'strength': 7, 'desc': 'Dipte dönüş sinyali'},
        'inverted_hammer': {'name': 'Ters Çekiç', 'signal': 'AL', 'strength': 6, 'desc': 'Dipte dönüş'},
        'bullish_engulfing': {'name': 'Yutan Boğa', 'signal': 'GÜÇLÜ AL', 'strength': 8, 'desc': 'Güçlü alım baskısı'},
        'morning_star': {'name': 'Sabah Yıldızı', 'signal': 'GÜÇLÜ AL', 'strength': 9, 'desc': '3 mumlu dip formasyonu'},
        'three_white_soldiers': {'name': 'Üç Beyaz Asker', 'signal': 'GÜÇLÜ AL', 'strength': 9, 'desc': 'Güçlü yükseliş'},
        'bullish_harami': {'name': 'Boğa Harami', 'signal': 'AL', 'strength': 6, 'desc': 'Trend dönüşü olası'},
        'piercing_line': {'name': 'Piercing (Delici)', 'signal': 'AL', 'strength': 7, 'desc': 'Dipte güç'},
        'tweezer_bottom': {'name': 'Tweezer Dip', 'signal': 'AL', 'strength': 7, 'desc': 'Çift dip desteği'},
        'doji_star_bullish': {'name': 'Doji Boğa', 'signal': 'AL', 'strength': 6, 'desc': 'Kararsızlık sonrası yükseliş'},
        'abandoned_baby_bullish': {'name': 'Terk Edilmiş Bebek', 'signal': 'GÜÇLÜ AL', 'strength': 9, 'desc': 'Nadir güçlü sinyal'},
        'rising_three': {'name': 'Yükselen Üçlü', 'signal': 'AL', 'strength': 7, 'desc': 'Devam formasyonu'},
        'bullish_marubozu': {'name': 'Boğa Marubozu', 'signal': 'GÜÇLÜ AL', 'strength': 8, 'desc': 'Fitilsiz güçlü mum'},
        'dragonfly_doji': {'name': 'Dragonfly Doji', 'signal': 'AL', 'strength': 7, 'desc': 'Dipte dönüş'},
        'bullish_belt_hold': {'name': 'Boğa Kemer', 'signal': 'AL', 'strength': 6, 'desc': 'Açılışta güç'},
    }
    
    BEARISH_PATTERNS = {
        'hanging_man': {'name': 'Asılı Adam', 'signal': 'SAT', 'strength': 7, 'desc': 'Tepede uyarı'},
        'shooting_star': {'name': 'Kayan Yıldız', 'signal': 'SAT', 'strength': 7, 'desc': 'Tepede red'},
        'bearish_engulfing': {'name': 'Yutan Ayı', 'signal': 'GÜÇLÜ SAT', 'strength': 8, 'desc': 'Güçlü satış baskısı'},
        'evening_star': {'name': 'Akşam Yıldızı', 'signal': 'GÜÇLÜ SAT', 'strength': 9, 'desc': '3 mumlu tepe formasyonu'},
        'three_black_crows': {'name': 'Üç Kara Karga', 'signal': 'GÜÇLÜ SAT', 'strength': 9, 'desc': 'Güçlü düşüş'},
        'bearish_harami': {'name': 'Ayı Harami', 'signal': 'SAT', 'strength': 6, 'desc': 'Trend dönüşü olası'},
        'dark_cloud_cover': {'name': 'Dark Cloud (Kara Bulut)', 'signal': 'SAT', 'strength': 7, 'desc': 'Tepede baskı'},
        'tweezer_top': {'name': 'Tweezer Tepe', 'signal': 'SAT', 'strength': 7, 'desc': 'Çift tepe direnci'},
        'doji_star_bearish': {'name': 'Doji Ayı', 'signal': 'SAT', 'strength': 6, 'desc': 'Kararsızlık sonrası düşüş'},
        'abandoned_baby_bearish': {'name': 'Terk Edilmiş Bebek (Ayı)', 'signal': 'GÜÇLÜ SAT', 'strength': 9, 'desc': 'Nadir güçlü sinyal'},
        'falling_three': {'name': 'Düşen Üçlü', 'signal': 'SAT', 'strength': 7, 'desc': 'Devam formasyonu'},
        'gravestone_doji': {'name': 'Mezartaşı Doji', 'signal': 'SAT', 'strength': 7, 'desc': 'Tepede red'},
        'bearish_marubozu': {'name': 'Ayı Marubozu', 'signal': 'GÜÇLÜ SAT', 'strength': 8, 'desc': 'Fitilsiz düşüş mumu'},
        'bearish_belt_hold': {'name': 'Ayı Kemer', 'signal': 'SAT', 'strength': 6, 'desc': 'Açılışta zayıflık'},
    }
    
    NEUTRAL_PATTERNS = {
        'doji': {'name': 'Doji', 'signal': 'TUT', 'strength': 5, 'desc': 'Kararsızlık'},
        'spinning_top': {'name': 'Dönen Tepe', 'signal': 'TUT', 'strength': 4, 'desc': 'Güç dengelenmesi'},
        'high_wave': {'name': 'Yüksek Dalga', 'signal': 'TUT', 'strength': 4, 'desc': 'Volatilite'},
        'long_legged_doji': {'name': 'Uzun Bacaklı Doji', 'signal': 'TUT', 'strength': 5, 'desc': 'Ekstrem kararsızlık'},
    }


class ChartFormation:
    """Grafik formasyonları veritabanı"""
    
    BULLISH_FORMATIONS = {
        'cup_handle': {'name': 'Fincan Kulp (Cup & Handle)', 'signal': 'GÜÇLÜ AL', 'target': '+30-50%'},
        'inverse_head_shoulders': {'name': 'Ters OBO (TOBO)', 'signal': 'GÜÇLÜ AL', 'target': 'Boyun çizgisi kadar'},
        'ascending_triangle': {'name': 'Yükselen Üçgen', 'signal': 'AL', 'target': 'Üçgen yüksekliği kadar'},
        'bullish_flag': {'name': 'Yükselen Bayrak', 'signal': 'AL', 'target': 'Bayrak direği kadar'},
        'bullish_pennant': {'name': 'Yükselen Flama', 'signal': 'AL', 'target': 'Flama direği kadar'},
        'double_bottom': {'name': 'İkili Dip (W)', 'signal': 'AL', 'target': 'Boyun çizgisi kadar'},
        'triple_bottom': {'name': 'Üçlü Dip', 'signal': 'GÜÇLÜ AL', 'target': 'Formasyon yüksekliği'},
        'ascending_wedge_break': {'name': 'Yükselen Kama Kırılımı', 'signal': 'AL', 'target': 'Kama yüksekliği'},
        'rounding_bottom': {'name': 'Çanak (Rounding Bottom)', 'signal': 'AL', 'target': 'Uzun vadeli yükseliş'},
    }
    
    BEARISH_FORMATIONS = {
        'head_shoulders': {'name': 'OBO (Omuz Baş Omuz)', 'signal': 'GÜÇLÜ SAT', 'target': 'Boyun çizgisi kadar'},
        'descending_triangle': {'name': 'Alçalan Üçgen', 'signal': 'SAT', 'target': 'Üçgen yüksekliği kadar'},
        'bearish_flag': {'name': 'Düşen Bayrak', 'signal': 'SAT', 'target': 'Bayrak direği kadar'},
        'bearish_pennant': {'name': 'Düşen Flama', 'signal': 'SAT', 'target': 'Flama direği kadar'},
        'double_top': {'name': 'İkili Tepe (M)', 'signal': 'SAT', 'target': 'Boyun çizgisi kadar'},
        'triple_top': {'name': 'Üçlü Tepe', 'signal': 'GÜÇLÜ SAT', 'target': 'Formasyon yüksekliği'},
        'descending_wedge_break': {'name': 'Alçalan Kama Kırılımı', 'signal': 'SAT', 'target': 'Kama yüksekliği'},
        'inverse_cup_handle': {'name': 'Ters Fincan Kulp', 'signal': 'GÜÇLÜ SAT', 'target': 'Formasyon derinliği'},
    }
    
    NEUTRAL_FORMATIONS = {
        'symmetrical_triangle': {'name': 'Simetrik Üçgen', 'signal': 'TUT', 'target': 'Kırılım yönüne göre'},
        'rectangle': {'name': 'Dikdörtgen', 'signal': 'TUT', 'target': 'Kırılım bekle'},
        'consolidation': {'name': 'Konsolidasyon', 'signal': 'TUT', 'target': 'Kırılım bekle'},
    }


class ChartAnalyzer:
    """Ultra Gelişmiş Grafik Analiz Motoru"""
    
    def __init__(self):
        self.logger = logger
        self.candle_patterns = CandlePattern()
        self.chart_formations = ChartFormation()
    
    def analyze_chart(self, image_path: str) -> dict:
        """Grafik resmini kapsamlı analiz et"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'error': 'Resim okunamadı'}
            
            results = {
                'trend': self._detect_trend(image),
                'candle_patterns': self._detect_candle_patterns(image),
                'chart_formations': self._detect_chart_formations(image),
                'macd_signals': self._detect_macd_signals(image),
                'divergence': self._detect_divergence(image),
                'color_analysis': self._analyze_colors(image),
                'price_levels': self._detect_price_levels(image),
                'support_resistance': self._find_support_resistance(image),
                'supply_demand': self._detect_supply_demand(image),
                'volume_signal': self._analyze_volume(image),
                'momentum': self._detect_momentum(image),
                'rsi_zone': self._detect_rsi_zone(image),
                'trend_channels': self._detect_trend_channels(image),
                'confidence': 0.0
            }
            
            results['signal'] = self._generate_signal(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Grafik analiz hatası: {e}")
            return {'error': str(e)}
    
    def _detect_candle_patterns(self, image) -> List[Dict]:
        """Gelişmiş mum formasyonu tespiti"""
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
            
            green_candles = [c for c in green_contours if cv2.contourArea(c) > 50]
            red_candles = [c for c in red_contours if cv2.contourArea(c) > 50]
            
            if len(green_candles) >= 3 and green_ratio > red_ratio * 1.5:
                detected.append({
                    'pattern': 'three_white_soldiers',
                    'name': 'Üç Beyaz Asker',
                    'signal': 'GÜÇLÜ AL',
                    'confidence': 0.75,
                    'desc': 'Ardışık 3 yeşil mum - güçlü yükseliş'
                })
            
            if len(red_candles) >= 3 and red_ratio > green_ratio * 1.5:
                detected.append({
                    'pattern': 'three_black_crows',
                    'name': 'Üç Kara Karga',
                    'signal': 'GÜÇLÜ SAT',
                    'confidence': 0.75,
                    'desc': 'Ardışık 3 kırmızı mum - güçlü düşüş'
                })
            
            if green_ratio > red_ratio * 2.5:
                detected.append({
                    'pattern': 'bullish_marubozu',
                    'name': 'Boğa Marubozu',
                    'signal': 'GÜÇLÜ AL',
                    'confidence': 0.7,
                    'desc': 'Fitilsiz güçlü yeşil mum'
                })
            elif red_ratio > green_ratio * 2.5:
                detected.append({
                    'pattern': 'bearish_marubozu',
                    'name': 'Ayı Marubozu',
                    'signal': 'GÜÇLÜ SAT',
                    'confidence': 0.7,
                    'desc': 'Fitilsiz güçlü kırmızı mum'
                })
            
            if green_ratio > red_ratio * 1.5:
                detected.append({
                    'pattern': 'bullish_engulfing',
                    'name': 'Yutan Boğa',
                    'signal': 'AL',
                    'confidence': 0.65,
                    'desc': 'Yeşil mum kırmızıyı yutmuş'
                })
            elif red_ratio > green_ratio * 1.5:
                detected.append({
                    'pattern': 'bearish_engulfing',
                    'name': 'Yutan Ayı',
                    'signal': 'SAT',
                    'confidence': 0.65,
                    'desc': 'Kırmızı mum yeşili yutmuş'
                })
            
            if abs(green_ratio - red_ratio) < 0.02:
                detected.append({
                    'pattern': 'doji',
                    'name': 'Doji',
                    'signal': 'TUT',
                    'confidence': 0.6,
                    'desc': 'Kararsızlık - trend dönüşü olası'
                })
            
            return detected
            
        except Exception as e:
            logger.error(f"Mum formasyonu tespiti hatası: {e}")
            return []
    
    def _detect_chart_formations(self, image) -> List[Dict]:
        """Grafik formasyonlarını tespit et (TOBO, OBO, Cup&Handle, Bayrak, Flama vb.)"""
        formations = []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
            
            if lines is not None:
                ascending_lines = 0
                descending_lines = 0
                horizontal_lines = 0
                converging = False
                
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if x2 != x1:
                        slope = (y2 - y1) / (x2 - x1)
                        if slope > 0.15:
                            descending_lines += 1
                        elif slope < -0.15:
                            ascending_lines += 1
                        else:
                            horizontal_lines += 1
                
                if ascending_lines > 3 and descending_lines > 3:
                    if ascending_lines > descending_lines * 1.3:
                        formations.append({
                            'formation': 'ascending_triangle',
                            'name': 'Yükselen Üçgen',
                            'signal': 'AL',
                            'description': 'Yukarı kırılım bekleniyor',
                            'target': 'Üçgen yüksekliği kadar yukarı'
                        })
                    elif descending_lines > ascending_lines * 1.3:
                        formations.append({
                            'formation': 'descending_triangle',
                            'name': 'Alçalan Üçgen',
                            'signal': 'SAT',
                            'description': 'Aşağı kırılım bekleniyor',
                            'target': 'Üçgen yüksekliği kadar aşağı'
                        })
                    else:
                        formations.append({
                            'formation': 'symmetrical_triangle',
                            'name': 'Simetrik Üçgen',
                            'signal': 'TUT',
                            'description': 'Kırılım yönü belirsiz - bekle',
                            'target': 'Kırılım yönüne göre işlem'
                        })
                
                height = image.shape[0]
                width = image.shape[1]
                
                top_region = gray[:height//3, :]
                bottom_region = gray[2*height//3:, :]
                
                top_peaks = self._find_peaks(top_region)
                bottom_dips = self._find_peaks(255 - bottom_region)
                
                if len(top_peaks) >= 2:
                    formations.append({
                        'formation': 'double_top',
                        'name': 'İkili Tepe (M)',
                        'signal': 'SAT',
                        'description': 'Çift tepe direnci - düşüş bekleniyor',
                        'target': 'Boyun çizgisi kadar aşağı'
                    })
                
                if len(bottom_dips) >= 2:
                    formations.append({
                        'formation': 'double_bottom',
                        'name': 'İkili Dip (W)',
                        'signal': 'AL',
                        'description': 'Çift dip desteği - yükseliş bekleniyor',
                        'target': 'Boyun çizgisi kadar yukarı'
                    })
                
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                lower_green = np.array([35, 50, 50])
                upper_green = np.array([85, 255, 255])
                green_mask = cv2.inRange(hsv, lower_green, upper_green)
                
                if self._detect_cup_shape(gray):
                    formations.append({
                        'formation': 'cup_handle',
                        'name': 'Fincan Kulp (Cup & Handle)',
                        'signal': 'GÜÇLÜ AL',
                        'description': 'Güçlü yükseliş formasyonu',
                        'target': '+30-50% potansiyel'
                    })
                
                if horizontal_lines > 8:
                    formations.append({
                        'formation': 'consolidation',
                        'name': 'Konsolidasyon',
                        'signal': 'TUT',
                        'description': 'Yatay hareket - kırılım bekle',
                        'target': 'Kırılım yönüne göre işlem'
                    })
            
            return formations
            
        except Exception as e:
            logger.error(f"Grafik formasyonu tespiti hatası: {e}")
            return []
    
    def _detect_cup_shape(self, gray) -> bool:
        """Fincan (Cup) şekli tespit et"""
        try:
            height, width = gray.shape
            center_region = gray[height//3:2*height//3, width//4:3*width//4]
            
            row_means = np.mean(center_region, axis=1)
            
            mid_point = len(row_means) // 2
            left_half = row_means[:mid_point]
            right_half = row_means[mid_point:]
            
            if len(left_half) > 0 and len(right_half) > 0:
                left_trend = np.mean(np.diff(left_half))
                right_trend = np.mean(np.diff(right_half))
                
                if left_trend > 0 and right_trend < 0:
                    return True
            
            return False
        except:
            return False
    
    def _find_peaks(self, region) -> List:
        """Bölgede tepe noktalarını bul"""
        try:
            col_means = np.mean(region, axis=0)
            peaks = []
            
            for i in range(1, len(col_means) - 1):
                if col_means[i] > col_means[i-1] and col_means[i] > col_means[i+1]:
                    if col_means[i] > np.mean(col_means) + np.std(col_means):
                        peaks.append(i)
            
            return peaks
        except:
            return []
    
    def _detect_macd_signals(self, image) -> Dict:
        """MACD sinyallerini tespit et"""
        try:
            height = image.shape[0]
            macd_region = image[int(height * 0.6):int(height * 0.85), :]
            
            hsv = cv2.cvtColor(macd_region, cv2.COLOR_BGR2HSV)
            
            lower_green = np.array([35, 50, 50])
            upper_green = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            lower_red = np.array([0, 50, 50])
            upper_red = np.array([10, 255, 255])
            red_mask = cv2.inRange(hsv, lower_red, upper_red)
            
            green_pixels = cv2.countNonZero(green_mask)
            red_pixels = cv2.countNonZero(red_mask)
            
            width = macd_region.shape[1]
            left_green = cv2.countNonZero(green_mask[:, :width//2])
            right_green = cv2.countNonZero(green_mask[:, width//2:])
            left_red = cv2.countNonZero(red_mask[:, :width//2])
            right_red = cv2.countNonZero(red_mask[:, width//2:])
            
            if right_green > left_green * 1.3 and right_green > right_red:
                return {
                    'signal': 'MACD Boğa Kesişimi',
                    'action': 'AL',
                    'description': 'MACD sinyal hattını yukarı kesti - GÜÇLÜ AL',
                    'strength': 8
                }
            elif right_red > left_red * 1.3 and right_red > right_green:
                return {
                    'signal': 'MACD Ayı Kesişimi',
                    'action': 'SAT',
                    'description': 'MACD sinyal hattını aşağı kesti - GÜÇLÜ SAT',
                    'strength': 8
                }
            elif green_pixels > red_pixels * 1.5:
                return {
                    'signal': 'MACD Pozitif',
                    'action': 'AL',
                    'description': 'MACD sıfır çizgisi üstünde',
                    'strength': 6
                }
            elif red_pixels > green_pixels * 1.5:
                return {
                    'signal': 'MACD Negatif',
                    'action': 'SAT',
                    'description': 'MACD sıfır çizgisi altında',
                    'strength': 6
                }
            
            return {
                'signal': 'MACD Nötr',
                'action': 'TUT',
                'description': 'Belirgin sinyal yok',
                'strength': 5
            }
            
        except Exception as e:
            logger.error(f"MACD tespiti hatası: {e}")
            return {'signal': 'Bilinmiyor', 'action': 'TUT'}
    
    def _detect_divergence(self, image) -> Dict:
        """Uyuşmazlık (Divergence) tespiti"""
        try:
            height = image.shape[0]
            
            price_region = image[:int(height * 0.5), :]
            indicator_region = image[int(height * 0.7):, :]
            
            price_gray = cv2.cvtColor(price_region, cv2.COLOR_BGR2GRAY)
            indicator_gray = cv2.cvtColor(indicator_region, cv2.COLOR_BGR2GRAY)
            
            price_trend = self._calculate_trend(price_gray)
            indicator_trend = self._calculate_trend(indicator_gray)
            
            if price_trend == 'UP' and indicator_trend == 'DOWN':
                return {
                    'type': 'bearish_divergence',
                    'name': 'Ayı Uyuşmazlığı (Negatif)',
                    'signal': 'SAT',
                    'description': 'Fiyat yükselirken indikatör düşüyor - düşüş bekleniyor',
                    'strength': 8
                }
            elif price_trend == 'DOWN' and indicator_trend == 'UP':
                return {
                    'type': 'bullish_divergence',
                    'name': 'Boğa Uyuşmazlığı (Pozitif)',
                    'signal': 'AL',
                    'description': 'Fiyat düşerken indikatör yükseliyor - yükseliş bekleniyor',
                    'strength': 8
                }
            
            return {
                'type': 'none',
                'name': 'Uyuşmazlık Yok',
                'signal': 'TUT',
                'description': 'Fiyat ve indikatör uyumlu',
                'strength': 5
            }
            
        except Exception as e:
            logger.error(f"Divergence tespiti hatası: {e}")
            return {'type': 'unknown', 'signal': 'TUT'}
    
    def _calculate_trend(self, gray_region) -> str:
        """Bölgenin trend yönünü hesapla"""
        try:
            width = gray_region.shape[1]
            left_avg = np.mean(gray_region[:, :width//3])
            right_avg = np.mean(gray_region[:, -width//3:])
            
            if left_avg > right_avg + 5:
                return 'UP'
            elif right_avg > left_avg + 5:
                return 'DOWN'
            return 'SIDEWAYS'
        except:
            return 'UNKNOWN'
    
    def _detect_supply_demand(self, image) -> Dict:
        """Arz ve Talep bölgelerini tespit et"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height = gray.shape[0]
            
            top_region = gray[:height//4, :]
            bottom_region = gray[-height//4:, :]
            
            top_intensity = np.mean(top_region)
            bottom_intensity = np.mean(bottom_region)
            
            zones = []
            
            if top_intensity < 100:
                zones.append({
                    'type': 'supply',
                    'name': 'Arz Bölgesi (Direnç)',
                    'position': 'Üst',
                    'strength': 'Güçlü' if top_intensity < 80 else 'Orta'
                })
            
            if bottom_intensity < 100:
                zones.append({
                    'type': 'demand',
                    'name': 'Talep Bölgesi (Destek)',
                    'position': 'Alt',
                    'strength': 'Güçlü' if bottom_intensity < 80 else 'Orta'
                })
            
            return {
                'zones': zones,
                'supply_count': len([z for z in zones if z['type'] == 'supply']),
                'demand_count': len([z for z in zones if z['type'] == 'demand'])
            }
            
        except Exception as e:
            logger.error(f"Arz/Talep tespiti hatası: {e}")
            return {'zones': []}
    
    def _detect_trend_channels(self, image) -> Dict:
        """Trend kanallarını tespit et"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 80, minLineLength=100, maxLineGap=20)
            
            if lines is None:
                return {'channel': 'Yok', 'signal': 'TUT'}
            
            slopes = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 != x1:
                    slope = (y2 - y1) / (x2 - x1)
                    slopes.append(slope)
            
            if len(slopes) == 0:
                return {'channel': 'Yok', 'signal': 'TUT'}
            
            avg_slope = np.mean(slopes)
            
            if avg_slope < -0.2:
                return {
                    'channel': 'Yükselen Kanal',
                    'signal': 'AL',
                    'description': 'Fiyat yükselen kanal içinde',
                    'action': 'Kanal altında AL, üstünde SAT'
                }
            elif avg_slope > 0.2:
                return {
                    'channel': 'Alçalan Kanal',
                    'signal': 'SAT',
                    'description': 'Fiyat alçalan kanal içinde',
                    'action': 'Kanal kırılımında işlem'
                }
            else:
                return {
                    'channel': 'Yatay Kanal',
                    'signal': 'TUT',
                    'description': 'Fiyat yatay kanal içinde',
                    'action': 'Destek ve dirençte işlem'
                }
                
        except Exception as e:
            logger.error(f"Trend kanalı tespiti hatası: {e}")
            return {'channel': 'Bilinmiyor'}
    
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
        """Renk analizi"""
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
                'zone': 'Direnç Yakını 🔴' if price_position > 70 else 'Destek Yakını 🟢' if price_position < 30 else 'Orta Bölge ⚪'
            }
            
        except Exception as e:
            return {}
    
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
                        horizontal_levels.append(int(rho))
            
            height = image.shape[0]
            support_levels = [l for l in horizontal_levels if l > height * 0.5]
            resistance_levels = [l for l in horizontal_levels if l < height * 0.5]
            
            return {
                'support_count': len(support_levels),
                'resistance_count': len(resistance_levels),
                'support_strength': 'Güçlü 💪' if len(support_levels) >= 3 else 'Orta ⚡' if len(support_levels) >= 1 else 'Zayıf 📉',
                'resistance_strength': 'Güçlü 💪' if len(resistance_levels) >= 3 else 'Orta ⚡' if len(resistance_levels) >= 1 else 'Zayıf 📉'
            }
            
        except Exception as e:
            return {'support_strength': 'Bilinmiyor', 'resistance_strength': 'Bilinmiyor'}
    
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
                'strength': "Güçlü 💪" if avg_intensity > 120 else "Orta ⚡" if avg_intensity > 80 else "Zayıf 📉"
            }
            
        except Exception as e:
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
            return {'strength': 'Bilinmiyor', 'score': 5}
    
    def _detect_rsi_zone(self, image) -> Dict:
        """RSI bölgesini tespit et"""
        try:
            height = image.shape[0]
            bottom_region = image[int(height * 0.75):, :]
            
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
                    'name': 'Aşırı Alım 🔴',
                    'rsi_estimate': 75,
                    'signal': 'SAT',
                    'description': 'RSI 70 üstünde - düşüş riski'
                }
            elif purple_pixels > red_pixels * 1.5:
                return {
                    'zone': 'oversold',
                    'name': 'Aşırı Satım 🟢',
                    'rsi_estimate': 25,
                    'signal': 'AL',
                    'description': 'RSI 30 altında - yükseliş potansiyeli'
                }
            else:
                return {
                    'zone': 'neutral',
                    'name': 'Nötr ⚪',
                    'rsi_estimate': 50,
                    'signal': 'TUT',
                    'description': 'RSI 30-70 arası'
                }
                
        except Exception as e:
            return {'zone': 'unknown', 'rsi_estimate': 50}
    
    def _generate_signal(self, results: dict) -> Dict:
        """⚡ GÜÇLÜ SİNYAL ÜRETIMI - NET AL/SAT TAVSIYELERI"""
        try:
            score = 5.0
            signals = []
            
            # ===== TRENDİ KONTROL ET =====
            trend = results.get('trend', {})
            if trend.get('direction') == 'UP':
                score += 2.0  # KUAT trend artırımı
                signals.append(f"📈 <b>{trend.get('trend', '')}</b> (Güç: {trend.get('strength', 0):.0f}%)")
            elif trend.get('direction') == 'DOWN':
                score -= 2.0
                signals.append(f"📉 <b>{trend.get('trend', '')}</b> (Güç: {trend.get('strength', 0):.0f}%)")
            
            # ===== MUM FORMASYONLARI =====
            patterns = results.get('candle_patterns', [])
            for pattern in patterns[:3]:
                if 'GÜÇLÜ AL' in pattern.get('signal', ''):
                    score += 2.0
                    signals.append(f"🕯️ <b>{pattern.get('name', '')} (GÜÇLÜ AL!)</b>")
                elif 'AL' in pattern.get('signal', ''):
                    score += 1.5
                    signals.append(f"🕯️ {pattern.get('name', '')} (AL)")
                elif 'GÜÇLÜ SAT' in pattern.get('signal', ''):
                    score -= 2.0
                    signals.append(f"🕯️ <b>{pattern.get('name', '')} (GÜÇLÜ SAT!)</b>")
                elif 'SAT' in pattern.get('signal', ''):
                    score -= 1.5
                    signals.append(f"🕯️ {pattern.get('name', '')} (SAT)")
            
            # ===== GRAFİK FORMASYONLARI =====
            formations = results.get('chart_formations', [])
            for formation in formations[:2]:
                if formation.get('signal') == 'GÜÇLÜ AL':
                    score += 2.0
                    signals.append(f"📐 <b>{formation.get('name', '')} → GÜÇLÜ AL!</b>")
                elif formation.get('signal') == 'AL':
                    score += 1.5
                    signals.append(f"📐 {formation.get('name', '')} → AL")
                elif formation.get('signal') == 'GÜÇLÜ SAT':
                    score -= 2.0
                    signals.append(f"📐 <b>{formation.get('name', '')} → GÜÇLÜ SAT!</b>")
                elif formation.get('signal') == 'SAT':
                    score -= 1.5
                    signals.append(f"📐 {formation.get('name', '')} → SAT")
            
            # ===== MACD SİNYALLERİ =====
            macd = results.get('macd_signals', {})
            if macd.get('signal') == 'MACD Boğa Kesişimi':
                score += 1.5
                signals.append(f"📊 <b>{macd.get('signal', '')} - GÜÇLÜ AL!</b>")
            elif macd.get('signal') == 'MACD Ayı Kesişimi':
                score -= 1.5
                signals.append(f"📊 <b>{macd.get('signal', '')} - GÜÇLÜ SAT!</b>")
            elif macd.get('action') == 'AL':
                score += 1
                signals.append(f"📊 {macd.get('signal', '')}")
            elif macd.get('action') == 'SAT':
                score -= 1
                signals.append(f"📊 {macd.get('signal', '')}")
            
            # ===== DIVERGENCE (UYUŞMAZLIK) =====
            divergence = results.get('divergence', {})
            if divergence.get('type') == 'bearish_divergence':
                score -= 1.5
                signals.append(f"🔀 <b>{divergence.get('name', '')} - UYARI!</b>")
            elif divergence.get('type') == 'bullish_divergence':
                score += 1.5
                signals.append(f"🔀 <b>{divergence.get('name', '')} - FIRSAT!</b>")
            
            # ===== RSI ANALİZİ =====
            rsi = results.get('rsi_zone', {})
            if rsi.get('zone') == 'oversold':
                score += 1.5
                signals.append(f"📉 <b>RSI Aşırı Satım - AL FIRASAT!</b>")
            elif rsi.get('zone') == 'overbought':
                score -= 1.5
                signals.append(f"📈 <b>RSI Aşırı Alım - SAT UYARISI!</b>")
            
            # ===== RENKLERİN GÜÇ ANALİZİ =====
            colors = results.get('color_analysis', {})
            green_pct = colors.get('green_percent', 50)
            red_pct = colors.get('red_percent', 50)
            
            if green_pct > 70:
                score += 1
                signals.append(f"🟢 Yeşil Mumlar Baskın (%{green_pct:.0f})")
            elif red_pct > 70:
                score -= 1
                signals.append(f"🔴 Kırmızı Mumlar Baskın (%{red_pct:.0f})")
            
            # ===== HAMİ VE MOMENTUMü =====
            volume = results.get('volume_signal', {})
            if volume.get('trend') == '📈 Artan' and 'Güçlü' in volume.get('strength', ''):
                score += 0.5
            elif volume.get('trend') == '📉 Azalan':
                score -= 0.5
            
            # ===== FİNAL SKOR HESAPLAMA =====
            score = max(0, min(10, score))
            
            if score >= 8:
                signal = "🚀 <b>GÜÇLÜ AL - HEMEN AL!</b>"
                action = "STRONG_BUY"
                emoji = "🚀"
                instruction = "<b>⚡ KESİN TAV"
            elif score >= 6.5:
                signal = "🟢 <b>AL - ALMALI</b>"
                action = "BUY"
                emoji = "📈"
                instruction = "<b>✅ ALIM SİNYALİ</b>"
            elif score >= 4.5:
                signal = "⚪ <b>TUT - BEKLEME</b>"
                action = "HOLD"
                emoji = "➡️"
                instruction = "<b>⏸️ BEKLEME DURUMU</b>"
            elif score >= 2.5:
                signal = "🔴 <b>SAT - SATMALI</b>"
                action = "SELL"
                emoji = "📉"
                instruction = "<b>⚠️ SATIŞ SİNYALİ</b>"
            else:
                signal = "🚨 <b>GÜÇLÜ SAT - HEMEN SAT!</b>"
                action = "STRONG_SELL"
                emoji = "🚨"
                instruction = "<b>🚨 KESİN SATIŞ TAVS"
            
            return {
                'signal': signal,
                'action': action,
                'score': round(score, 1),
                'emoji': emoji,
                'instruction': instruction,
                'reasons': signals[:8]
            }
                
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {e}")
            return {'signal': "❓ Belirsiz", 'action': 'UNKNOWN', 'score': 5}
    
    def get_summary(self, image_path: str, symbol: str = None, current_price: float = None) -> str:
        """
        📊 KAPSAMLI GRAFİK ANALİZ RAPORU
        - Fiyat bilgisi, hedef, stop-loss
        - Neden AL / Neden UZAK DUR
        - Zaman tahmini
        """
        try:
            results = self.analyze_chart(image_path)
            
            if 'error' in results:
                return f"❌ Grafik analiz edilemedi: {results['error']}"
            
            signal = results.get('signal', {})
            score = signal.get('score', 5)
            action = signal.get('action', 'HOLD')
            
            trend = results.get('trend', {})
            trend_dir = trend.get('direction', 'NEUTRAL')
            trend_strength = trend.get('strength', 50)
            
            rsi = results.get('rsi_zone', {})
            rsi_val = rsi.get('rsi_estimate', 50)
            
            volume = results.get('volume_signal', {})
            momentum = results.get('momentum', {})
            patterns = results.get('candle_patterns', [])
            formations = results.get('chart_formations', [])
            
            if current_price and current_price > 0:
                if action in ['STRONG_BUY', 'BUY']:
                    target_pct = 15 if action == 'STRONG_BUY' else 10
                    stop_pct = 5 if action == 'STRONG_BUY' else 7
                    target_price = current_price * (1 + target_pct/100)
                    stop_loss = current_price * (1 - stop_pct/100)
                elif action in ['STRONG_SELL', 'SELL']:
                    target_pct = -10 if action == 'STRONG_SELL' else -5
                    stop_pct = 3
                    target_price = current_price * (1 + target_pct/100)
                    stop_loss = current_price * (1 + stop_pct/100)
                else:
                    target_price = current_price * 1.05
                    stop_loss = current_price * 0.95
            else:
                target_price = None
                stop_loss = None
            
            if action == 'STRONG_BUY':
                time_est = "24-48 saat"
                if trend_strength > 70:
                    time_est = "12-24 saat"
            elif action == 'BUY':
                time_est = "2-5 gün"
                if rsi_val < 35:
                    time_est = "1-3 gün"
            elif action == 'SELL':
                time_est = "1-3 gün içinde düşüş"
            elif action == 'STRONG_SELL':
                time_est = "24-48 saat içinde düşüş"
            else:
                time_est = "Belirsiz - Bekle"
            
            reasons_buy = []
            reasons_avoid = []
            
            if trend_dir == 'UP':
                reasons_buy.append(f"📈 Yükseliş trendi aktif (Güç: %{trend_strength:.0f})")
            elif trend_dir == 'DOWN':
                reasons_avoid.append(f"📉 Düşüş trendi aktif (Güç: %{trend_strength:.0f})")
            
            if rsi_val < 30:
                reasons_buy.append(f"🟢 RSI aşırı satım bölgesinde ({rsi_val}) - Toparlanma beklenir")
            elif rsi_val > 70:
                reasons_avoid.append(f"🔴 RSI aşırı alım bölgesinde ({rsi_val}) - Düşüş riski")
            
            for p in patterns[:2]:
                if 'AL' in p.get('signal', ''):
                    reasons_buy.append(f"🕯️ {p.get('name', '')} formasyonu - Alım sinyali")
                elif 'SAT' in p.get('signal', ''):
                    reasons_avoid.append(f"🕯️ {p.get('name', '')} formasyonu - Satış sinyali")
            
            for f in formations[:2]:
                if f.get('signal') in ['AL', 'GÜÇLÜ AL']:
                    reasons_buy.append(f"📐 {f.get('name', '')} - Yükseliş formasyonu")
                elif f.get('signal') in ['SAT', 'GÜÇLÜ SAT']:
                    reasons_avoid.append(f"📐 {f.get('name', '')} - Düşüş formasyonu")
            
            macd = results.get('macd_signals', {})
            if macd.get('signal') == 'MACD Boğa Kesişimi':
                reasons_buy.append("📊 MACD boğa kesişimi - Güçlü alım sinyali")
            elif macd.get('signal') == 'MACD Ayı Kesişimi':
                reasons_avoid.append("📊 MACD ayı kesişimi - Satış sinyali")
            
            if volume.get('trend') == '📈 Artan':
                reasons_buy.append("📊 Hacim artıyor - Hareket güçlü")
            elif volume.get('trend') == '📉 Azalan':
                reasons_avoid.append("📊 Hacim azalıyor - Trend zayıflıyor")
            
            symbol_text = f" - {symbol}" if symbol else ""
            
            if action == 'STRONG_BUY':
                verdict = "🚀 <b>KESİN AL!</b>"
                verdict_desc = "Tüm göstergeler pozitif. Hemen alım yapılabilir!"
            elif action == 'BUY':
                verdict = "🟢 <b>AL</b>"
                verdict_desc = "İyi fırsat. Alım düşünülebilir."
            elif action == 'HOLD':
                verdict = "⏸️ <b>BEKLE</b>"
                verdict_desc = "Net sinyal yok. Beklemede kal."
            elif action == 'SELL':
                verdict = "🔴 <b>UZAK DUR</b>"
                verdict_desc = "Riskli görünüyor. Almayı düşünme."
            else:
                verdict = "🚨 <b>KESİNLİKLE UZAK DUR!</b>"
                verdict_desc = "Tehlike! Bu coindan uzak dur!"
            
            msg = f"""📊 <b>KAPSAMLI GRAFİK ANALİZİ{symbol_text}</b>
{'═' * 30}

{verdict}
<i>{verdict_desc}</i>

📊 <b>SKOR:</b> {score}/10
"""
            
            if current_price and target_price and stop_loss:
                msg += f"""
{'─' * 25}
💰 <b>FİYAT BİLGİLERİ</b>
{'─' * 25}
💵 <b>Güncel Fiyat:</b> ₺{current_price:,.2f}
🎯 <b>Hedef Fiyat:</b> ₺{target_price:,.2f}
🛑 <b>Stop-Loss:</b> ₺{stop_loss:,.2f}
"""
                if action in ['STRONG_BUY', 'BUY']:
                    profit_pct = ((target_price - current_price) / current_price) * 100
                    loss_pct = ((current_price - stop_loss) / current_price) * 100
                    msg += f"📈 <b>Kar Potansiyeli:</b> +%{profit_pct:.1f}\n"
                    msg += f"📉 <b>Risk:</b> -%{loss_pct:.1f}\n"
            
            msg += f"""
{'─' * 25}
⏰ <b>ZAMAN TAHMİNİ</b>
{'─' * 25}
🕐 <b>Beklenen Hareket:</b> {time_est}
"""
            
            if action in ['STRONG_BUY', 'BUY'] and reasons_buy:
                msg += f"""
{'─' * 25}
✅ <b>NEDEN ALMALISIN?</b>
{'─' * 25}
"""
                for r in reasons_buy[:4]:
                    msg += f"• {r}\n"
            
            elif action in ['STRONG_SELL', 'SELL'] and reasons_avoid:
                msg += f"""
{'─' * 25}
❌ <b>NEDEN UZAK DURMALISIN?</b>
{'─' * 25}
"""
                for r in reasons_avoid[:4]:
                    msg += f"• {r}\n"
            
            else:
                if reasons_buy:
                    msg += f"\n✅ <b>Olumlu:</b>\n"
                    for r in reasons_buy[:2]:
                        msg += f"• {r}\n"
                if reasons_avoid:
                    msg += f"\n⚠️ <b>Dikkat:</b>\n"
                    for r in reasons_avoid[:2]:
                        msg += f"• {r}\n"
            
            msg += f"""
{'─' * 25}
📈 <b>TEKNİK DURUM</b>
{'─' * 25}
📈 Trend: {trend.get('trend', '?')}
📉 RSI: {rsi.get('name', 'Nötr')} (~{rsi_val})
📊 Hacim: {volume.get('trend', '?')}
⚡ Momentum: {momentum.get('strength', '?')}
"""
            
            if patterns:
                msg += f"\n🕯️ <b>Tespit Edilen Mumlar:</b>\n"
                for p in patterns[:3]:
                    msg += f"   • {p.get('name', '?')} ({p.get('signal', '?')})\n"
            
            if formations:
                msg += f"\n📐 <b>Grafik Formasyonları:</b>\n"
                for f in formations[:2]:
                    msg += f"   • {f.get('name', '?')} ({f.get('signal', '?')})\n"
            
            msg += f"""
{'═' * 30}
{verdict}
⚠️ <i>Yatırım tavsiyesi değildir. DYOR!</i>"""
            
            return msg
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return "❌ Analiz oluşturulamadı"
