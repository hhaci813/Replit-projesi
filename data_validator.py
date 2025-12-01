"""Data Validation & Integrity - Çöp veri yok, her şey kontrol edilir"""
import logging
from datetime import datetime

class DataValidator:
    """Tüm veri kontrol - Çöp data filtreleme"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.valid_count = 0
        self.invalid_count = 0
    
    def validate_price(self, symbol, price, source=""):
        """Fiyat validasyonu"""
        try:
            price = float(price)
            
            # Kontroller
            if price <= 0:
                self.invalid_count += 1
                return None, f"❌ {symbol}: Fiyat negatif/sıfır ({price})"
            
            if price > 10_000_000:  # Max limit
                self.invalid_count += 1
                return None, f"❌ {symbol}: Fiyat çok yüksek ({price})"
            
            self.valid_count += 1
            return price, f"✅ {symbol}: ${price:.2f} ({source})"
        
        except (ValueError, TypeError):
            self.invalid_count += 1
            return None, f"❌ {symbol}: Fiyat parse edilemedi"
    
    def validate_analysis(self, analysis_result):
        """Analiz sonucu validasyonu"""
        if not analysis_result:
            return False, "❌ Analiz None döndü"
        
        required_keys = ['price', 'signal', 'rsi']
        for key in required_keys:
            if key not in analysis_result:
                return False, f"❌ {key} eksik"
        
        price = analysis_result.get('price', 0)
        if price <= 0:
            return False, f"❌ Geçersiz fiyat: {price}"
        
        rsi = analysis_result.get('rsi', 50)
        if not (0 <= rsi <= 100):
            return False, f"❌ RSI invalid: {rsi}"
        
        signal = analysis_result.get('signal', '')
        valid_signals = ['🟢', '⚪', '🔴', '❓']
        if not any(s in signal for s in valid_signals):
            return False, f"❌ Geçersiz sinyal: {signal}"
        
        return True, "✅ Analiz geçerli"
    
    def validate_portfolio(self, portfolio_data):
        """Portföy validasyonu"""
        if not portfolio_data:
            return False, "❌ Portföy boş"
        
        if 'total_budget' not in portfolio_data:
            return False, "❌ Budget eksik"
        
        budget = portfolio_data.get('total_budget', 0)
        if budget <= 0 or budget > 1_000_000:
            return False, f"❌ Budget invalid: {budget}"
        
        allocations = portfolio_data.get('allocations', [])
        if not allocations:
            return False, "❌ Allocation yokok"
        
        total_allocated = sum(a.get('amount', 0) for a in allocations)
        
        if abs(total_allocated - budget) > 1:  # Tolerance for rounding
            return False, f"❌ Toplam hata: {total_allocated} vs {budget}"
        
        return True, "✅ Portföy geçerli"
    
    def sanitize_data(self, data, data_type='generic'):
        """Veri temizle - Güvenlik"""
        if data_type == 'symbol':
            # Sadece harf ve rakam
            return ''.join(c for c in str(data).upper() if c.isalnum())
        
        elif data_type == 'text':
            # Script injection protection
            dangerous = ['<', '>', '"', "'", ';', '&', '|']
            text = str(data)
            for char in dangerous:
                text = text.replace(char, '')
            return text[:500]  # Max length
        
        return str(data)[:1000]
    
    def get_stats(self):
        """Validasyon istatistikleri"""
        total = self.valid_count + self.invalid_count
        success_rate = (self.valid_count / total * 100) if total > 0 else 0
        
        return {
            'valid': self.valid_count,
            'invalid': self.invalid_count,
            'success_rate_pct': success_rate,
            'timestamp': datetime.now()
        }
