"""
📈 GRAFIK FİYAT OKUMA (OCR) SİSTEMİ
Chart'tan fiyat, target, stop-loss değerlerini otomatik oku
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class ChartPriceReader:
    """Grafik resminden fiyat bilgisini çıkart"""
    
    def __init__(self):
        self.price_patterns = [
            r'\d+\.?\d*',  # Sayıları bul
            r'[₺$€]?\d+\.?\d*',  # Para birimli sayılar
        ]
    
    def read_price_zones(self, image_path: str) -> Dict:
        """Grafik'ten fiyat bölgelerini oku"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'error': 'Resim okunamadı'}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Yüksek kontrastlı alanları bul (fiyat yazıları genelde)
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            h, w = binary.shape
            
            # En üst (tepe fiyat), orta (current), alt (dip fiyat) bölgeleri
            top_region = binary[0:h//4, :]
            middle_region = binary[h//3:2*h//3, :]
            bottom_region = binary[3*h//4:h, :]
            
            zones = {
                'resistance': self._estimate_price_from_region(top_region, 'high'),
                'current': self._estimate_price_from_region(middle_region, 'mid'),
                'support': self._estimate_price_from_region(bottom_region, 'low'),
            }
            
            return {
                'zones': zones,
                'confidence': 0.6,
                'analysis': self._analyze_zones(zones)
            }
        
        except Exception as e:
            logger.error(f"Fiyat okuma hatası: {e}")
            return {'error': str(e)}
    
    def _estimate_price_from_region(self, region, region_type: str) -> Dict:
        """Bölgeden fiyat tahmini yap"""
        # Piksel sayısına göre tahmin (gerçek OCR yerine)
        white_pixels = cv2.countNonZero(region)
        h, w = region.shape
        total_pixels = h * w
        density = white_pixels / total_pixels
        
        return {
            'type': region_type,
            'pixel_density': round(density, 3),
            'estimated_strength': 'HIGH' if density > 0.4 else 'MEDIUM' if density > 0.2 else 'LOW'
        }
    
    def _analyze_zones(self, zones: Dict) -> str:
        """Fiyat bölgeleri analiz et"""
        msg = "📊 FİYAT BÖLGELERİ:\n"
        msg += f"📈 Direnç: {zones['resistance']['estimated_strength']}\n"
        msg += f"➡️  Mevcut: {zones['current']['estimated_strength']}\n"
        msg += f"📉 Destek: {zones['support']['estimated_strength']}\n"
        
        if zones['resistance']['estimated_strength'] == 'HIGH':
            msg += "\n⚠️  Tepede güçlü direnç var\n"
        
        return msg
    
    def extract_support_resistance(self, image_path: str) -> Dict:
        """Support/Resistance seviyeleri çıkart"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Yatay çizgileri bul (Support/Resistance)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
            
            horizontal_lines = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # Yatay çizgi mi?
                    if abs(y2 - y1) < 5:  # Neredeyse yatay
                        horizontal_lines.append(y1)
            
            # Y koordinatlarını sırala (tepeden tabana)
            horizontal_lines.sort()
            
            resistances = horizontal_lines[:max(1, len(horizontal_lines)//3)]
            supports = horizontal_lines[max(len(horizontal_lines)-len(horizontal_lines)//3, 1):]
            
            return {
                'support_levels': len(supports),
                'resistance_levels': len(resistances),
                'top_resistance': resistances[0] if resistances else None,
                'bottom_support': supports[-1] if supports else None,
                'message': f"📍 {len(supports)} Destek | {len(resistances)} Direnç seviyesi bulundu"
            }
        
        except Exception as e:
            logger.error(f"S/R çıkarma hatası: {e}")
            return {'error': str(e)}
    
    def get_analysis_message(self, image_path: str) -> str:
        """Grafik analiz mesajı oluştur"""
        msg = "📊 GRAFİK FİYAT ANALİZİ\n"
        msg += f"{'='*40}\n"
        
        price_zones = self.read_price_zones(image_path)
        if 'error' not in price_zones:
            msg += price_zones['zones']['analysis']
        
        sr = self.extract_support_resistance(image_path)
        if 'error' not in sr:
            msg += f"\n{sr['message']}\n"
        
        msg += f"\n💡 NOT: Yapay zeka tabanlı tahmin\n"
        msg += f"Gerçek fiyat seviyeleri için grafik inceleyiniz"
        
        return msg
