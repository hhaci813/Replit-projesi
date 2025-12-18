"""
Grafik Resim Analiz Sistemi
- Mum grafikleri analizi
- Trend tespiti
- Destek/Direnç seviyeleri
- İndikatörleri okuma
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ChartAnalyzer:
    def __init__(self):
        self.logger = logger
    
    def analyze_chart(self, image_path: str) -> dict:
        """
        Grafik resmini analiz et
        Fiyat trendi, destek/direnç, momentum vb. çıkar
        """
        try:
            # Resmi oku
            image = cv2.imread(image_path)
            if image is None:
                return {'error': 'Resim okunamadı'}
            
            pil_image = Image.open(image_path)
            
            # Analiz sonuçları
            results = {
                'trend': self._detect_trend(image),
                'color_analysis': self._analyze_colors(pil_image),
                'price_levels': self._detect_price_levels(image),
                'volume_signal': self._analyze_volume(image),
                'momentum': self._detect_momentum(image),
                'confidence': 0.0
            }
            
            # Genel sinyal
            results['signal'] = self._generate_signal(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Grafik analiz hatası: {e}")
            return {'error': str(e)}
    
    def _detect_trend(self, image) -> str:
        """Grafikteki trend yönü tespit et"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height = gray.shape[0]
            
            # Sol ve sağ tarafa bak
            left_avg = np.mean(gray[:, :gray.shape[1]//3])
            right_avg = np.mean(gray[:, -gray.shape[1]//3:])
            
            # Açık ve koyu alanları karşılaştır
            if left_avg > right_avg + 10:
                return "📉 Düşüş Trendi"
            elif right_avg > left_avg + 10:
                return "📈 Yükseliş Trendi"
            else:
                return "➡️ Yatay Trend"
                
        except Exception as e:
            logger.error(f"Trend tespiti hatası: {e}")
            return "❓ Bilinmiyor"
    
    def _analyze_colors(self, pil_image) -> dict:
        """Resim rengini analiz et"""
        try:
            img_array = np.array(pil_image)
            
            # RGB ortalamaları
            if len(img_array.shape) == 3:
                red = np.mean(img_array[:,:,0])
                green = np.mean(img_array[:,:,1])
                blue = np.mean(img_array[:,:,2])
                
                # Hangi renk baskın
                colors = {'red': red, 'green': green, 'blue': blue}
                dominant = max(colors, key=colors.get)
                
                return {
                    'dominant': dominant,
                    'red_avg': float(red),
                    'green_avg': float(green),
                    'blue_avg': float(blue)
                }
            return {}
        except Exception as e:
            logger.error(f"Renk analizi hatası: {e}")
            return {}
    
    def _detect_price_levels(self, image) -> dict:
        """Destek/direnç seviyelerini tespit et"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Yatay çizgileri bul
            lines = cv2.HoughLines(edges, 1, np.pi/180, 50)
            
            horizontal_lines = []
            if lines is not None:
                for rho, theta in lines[:10]:
                    if abs(np.sin(theta)) < 0.1:  # Yatay çizgiler
                        horizontal_lines.append(rho)
            
            # Normalleştir (0-100 arası)
            if len(horizontal_lines) > 0:
                min_level = min(horizontal_lines) / image.shape[0] * 100
                max_level = max(horizontal_lines) / image.shape[0] * 100
            else:
                min_level = 30
                max_level = 70
            
            return {
                'resistance': float(max_level),
                'support': float(min_level),
                'midpoint': float((min_level + max_level) / 2),
                'detected_lines': len(horizontal_lines)
            }
            
        except Exception as e:
            logger.error(f"Fiyat seviyeleri hatası: {e}")
            return {'support': 30, 'resistance': 70}
    
    def _analyze_volume(self, image) -> dict:
        """Hacim analizi"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Alttaki hacim bölgesini kontrol et (genelde grafiklerin altında)
            volume_region = gray[-gray.shape[0]//4:, :]
            
            # Ortalama yoğunluk = hacim tahmini
            volume_intensity = np.mean(volume_region)
            
            # Sağa doğru hacim artıyor mu
            left_vol = np.mean(volume_region[:, :volume_region.shape[1]//2])
            right_vol = np.mean(volume_region[:, -volume_region.shape[1]//2:])
            
            vol_trend = "Artan" if right_vol > left_vol else "Azalan"
            
            return {
                'intensity': float(volume_intensity),
                'trend': vol_trend,
                'strength': "Güçlü" if volume_intensity > 100 else "Zayıf"
            }
            
        except Exception as e:
            logger.error(f"Hacim analizi hatası: {e}")
            return {'intensity': 128, 'trend': 'Neutral'}
    
    def _detect_momentum(self, image) -> dict:
        """Momentum tespiti"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Yüksek kontrastlı alanlar = güçlü momentum
            contrast = np.std(gray)
            
            # Açık ve koyu bölgelerin sayısı
            threshold = np.mean(gray)
            dark_pixels = np.count_nonzero(gray < threshold - 30)
            light_pixels = np.count_nonzero(gray > threshold + 30)
            
            extreme_pixels = (dark_pixels + light_pixels) / (gray.size) * 100
            
            return {
                'contrast': float(contrast),
                'extreme_percentage': float(extreme_pixels),
                'strength': "Güçlü" if extreme_pixels > 20 else "Orta" if extreme_pixels > 10 else "Zayıf"
            }
            
        except Exception as e:
            logger.error(f"Momentum analizi hatası: {e}")
            return {'contrast': 50, 'strength': 'Orta'}
    
    def _generate_signal(self, results: dict) -> str:
        """Analiz sonuçlarından sinyal üret"""
        try:
            trend = results.get('trend', '')
            colors = results.get('color_analysis', {})
            momentum = results.get('momentum', {})
            
            signal_score = 5  # 0-10 skala
            
            # Trend etkisi
            if '📈' in trend:
                signal_score += 2
            elif '📉' in trend:
                signal_score -= 2
            
            # Renk etkisi
            if colors.get('dominant') == 'green':
                signal_score += 1
            elif colors.get('dominant') == 'red':
                signal_score -= 1
            
            # Momentum etkisi
            if momentum.get('strength') == 'Güçlü':
                signal_score += 1
            
            # Sınırla
            signal_score = max(0, min(10, signal_score))
            
            if signal_score >= 7:
                return "🟢 GÜÇLÜ AL"
            elif signal_score >= 6:
                return "🟢 AL"
            elif signal_score >= 4:
                return "⚪ TUT"
            elif signal_score >= 2:
                return "🔴 SAT"
            else:
                return "🔴 GÜÇLÜ SAT"
                
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {e}")
            return "❓ Belirsiz"
    
    def get_summary(self, image_path: str) -> str:
        """Grafik analiz özetini Telegram mesajı olarak döndür"""
        try:
            results = self.analyze_chart(image_path)
            
            if 'error' in results:
                return f"❌ Grafik analiz edilemedi: {results['error']}"
            
            summary = "📊 <b>GRAFIK ANALİZİ</b>\n\n"
            summary += f"🎯 <b>Sinyal:</b> {results.get('signal', '?')}\n"
            summary += f"📈 <b>Trend:</b> {results.get('trend', '?')}\n\n"
            
            levels = results.get('price_levels', {})
            summary += f"🆙 <b>Direnç:</b> %{levels.get('resistance', 70):.0f}\n"
            summary += f"🆙 <b>Destek:</b> %{levels.get('support', 30):.0f}\n"
            summary += f"📍 <b>Orta:</b> %{levels.get('midpoint', 50):.0f}\n\n"
            
            vol = results.get('volume_signal', {})
            summary += f"📊 <b>Hacim:</b> {vol.get('trend', '?')} ({vol.get('strength', '?')})\n"
            
            mom = results.get('momentum', {})
            summary += f"⚡ <b>Momentum:</b> {mom.get('strength', '?')}\n"
            
            colors = results.get('color_analysis', {})
            if colors.get('dominant'):
                summary += f"🎨 <b>Baskın Renk:</b> {colors['dominant']}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return "❌ Analiz oluşturulamadı"
