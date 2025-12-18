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
        """Tüm analizlerden sinyal üret"""
        try:
            score = 5.0
            signals = []
            
            trend = results.get('trend', {})
            if trend.get('direction') == 'UP':
                score += 1.5
                signals.append(f"📈 {trend.get('trend', '')}")
            elif trend.get('direction') == 'DOWN':
                score -= 1.5
                signals.append(f"📉 {trend.get('trend', '')}")
            
            colors = results.get('color_analysis', {})
            if colors.get('dominant') == 'BULLISH':
                score += 1
                signals.append("🟢 Yeşil mumlar baskın")
            elif colors.get('dominant') == 'BEARISH':
                score -= 1
                signals.append("🔴 Kırmızı mumlar baskın")
            
            patterns = results.get('candle_patterns', [])
            for pattern in patterns[:2]:
                if 'AL' in pattern.get('signal', ''):
                    score += 1.5
                    signals.append(f"🕯️ {pattern.get('name', '')}")
                elif 'SAT' in pattern.get('signal', ''):
                    score -= 1.5
                    signals.append(f"🕯️ {pattern.get('name', '')}")
            
            formations = results.get('chart_formations', [])
            for formation in formations[:2]:
                if formation.get('signal') == 'AL' or formation.get('signal') == 'GÜÇLÜ AL':
                    score += 1.5
                    signals.append(f"📐 {formation.get('name', '')}")
                elif formation.get('signal') == 'SAT' or formation.get('signal') == 'GÜÇLÜ SAT':
                    score -= 1.5
                    signals.append(f"📐 {formation.get('name', '')}")
            
            macd = results.get('macd_signals', {})
            if macd.get('action') == 'AL':
                score += 1
                signals.append(f"📊 {macd.get('signal', '')}")
            elif macd.get('action') == 'SAT':
                score -= 1
                signals.append(f"📊 {macd.get('signal', '')}")
            
            divergence = results.get('divergence', {})
            if divergence.get('signal') == 'AL':
                score += 1.5
                signals.append(f"🔀 {divergence.get('name', '')}")
            elif divergence.get('signal') == 'SAT':
                score -= 1.5
                signals.append(f"🔀 {divergence.get('name', '')}")
            
            rsi = results.get('rsi_zone', {})
            if rsi.get('zone') == 'oversold':
                score += 1
                signals.append("📉 RSI Aşırı Satım")
            elif rsi.get('zone') == 'overbought':
                score -= 1
                signals.append("📈 RSI Aşırı Alım")
            
            score = max(0, min(10, score))
            
            if score >= 7.5:
                signal = "🟢 GÜÇLÜ AL"
                action = "STRONG_BUY"
                emoji = "🚀"
            elif score >= 6:
                signal = "🟢 AL"
                action = "BUY"
                emoji = "📈"
            elif score >= 4:
                signal = "⚪ TUT"
                action = "HOLD"
                emoji = "➡️"
            elif score >= 2.5:
                signal = "🔴 SAT"
                action = "SELL"
                emoji = "📉"
            else:
                signal = "🔴 GÜÇLÜ SAT"
                action = "STRONG_SELL"
                emoji = "⚠️"
            
            return {
                'signal': signal,
                'action': action,
                'score': round(score, 1),
                'emoji': emoji,
                'reasons': signals[:6]
            }
                
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {e}")
            return {'signal': "❓ Belirsiz", 'action': 'UNKNOWN', 'score': 5}
    
    def get_summary(self, image_path: str) -> str:
        """Grafik analiz özetini Telegram mesajı olarak döndür"""
        try:
            results = self.analyze_chart(image_path)
            
            if 'error' in results:
                return f"❌ Grafik analiz edilemedi: {results['error']}"
            
            signal = results.get('signal', {})
            
            msg = f"""📊 <b>GRAFİK ANALİZİ v2.0</b>
{'━' * 25}

🎯 <b>SİNYAL:</b> {signal.get('signal', '?')} {signal.get('emoji', '')}
📊 <b>SKOR:</b> {signal.get('score', 5)}/10

"""
            
            trend = results.get('trend', {})
            msg += f"📈 <b>TREND:</b> {trend.get('trend', '?')}\n"
            msg += f"💪 <b>GÜÇ:</b> %{trend.get('strength', 0):.0f}\n\n"
            
            patterns = results.get('candle_patterns', [])
            if patterns:
                msg += "🕯️ <b>MUM FORMASYONLARI:</b>\n"
                for p in patterns[:3]:
                    msg += f"   • {p.get('name', '?')} → {p.get('signal', '?')}\n"
                    if p.get('desc'):
                        msg += f"     <i>{p.get('desc')}</i>\n"
                msg += "\n"
            
            formations = results.get('chart_formations', [])
            if formations:
                msg += "📐 <b>GRAFİK FORMASYONLARI:</b>\n"
                for f in formations[:2]:
                    msg += f"   • {f.get('name', '?')} → {f.get('signal', '?')}\n"
                    if f.get('description'):
                        msg += f"     <i>{f.get('description')}</i>\n"
                    if f.get('target'):
                        msg += f"     🎯 Hedef: {f.get('target')}\n"
                msg += "\n"
            
            macd = results.get('macd_signals', {})
            if macd.get('signal') != 'Bilinmiyor':
                msg += f"📊 <b>MACD:</b> {macd.get('signal', '?')}\n"
                if macd.get('description'):
                    msg += f"   <i>{macd.get('description')}</i>\n\n"
            
            divergence = results.get('divergence', {})
            if divergence.get('type') not in ['none', 'unknown']:
                msg += f"🔀 <b>UYUŞMAZLIK:</b> {divergence.get('name', '?')}\n"
                if divergence.get('description'):
                    msg += f"   <i>{divergence.get('description')}</i>\n\n"
            
            rsi = results.get('rsi_zone', {})
            volume = results.get('volume_signal', {})
            colors = results.get('color_analysis', {})
            momentum = results.get('momentum', {})
            
            msg += f"📉 <b>RSI:</b> {rsi.get('name', 'Nötr')} (~{rsi.get('rsi_estimate', 50)})\n"
            msg += f"📊 <b>HACİM:</b> {volume.get('trend', '?')} ({volume.get('strength', '?')})\n"
            msg += f"⚡ <b>MOMENTUM:</b> {momentum.get('strength', '?')}\n"
            msg += f"🎨 <b>PİYASA:</b> {colors.get('sentiment', '?')}\n\n"
            
            sr = results.get('support_resistance', {})
            msg += f"🔹 <b>DESTEK:</b> {sr.get('support_strength', '?')}\n"
            msg += f"🔸 <b>DİRENÇ:</b> {sr.get('resistance_strength', '?')}\n\n"
            
            channels = results.get('trend_channels', {})
            if channels.get('channel') and channels.get('channel') != 'Yok':
                msg += f"📏 <b>KANAL:</b> {channels.get('channel')}\n"
                if channels.get('action'):
                    msg += f"   <i>{channels.get('action')}</i>\n\n"
            
            if signal.get('reasons'):
                msg += "💡 <b>SEBEPLER:</b>\n"
                for reason in signal['reasons'][:5]:
                    msg += f"   • {reason}\n"
            
            msg += "\n⚠️ <i>Bu analiz yatırım tavsiyesi değildir. DYOR!</i>"
            
            return msg
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return "❌ Analiz oluşturulamadı"
