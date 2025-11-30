"""Telegram İnteraktif Bot - Kullanıcı sorusuna analiz ve tavsiye"""
from telegram_service import TelegramService
from universal_portfolio_engine import UniversalPortfolioEngine
import json

class TelegramInteractiveBot:
    def __init__(self):
        self.telegram = TelegramService()
        self.engine = UniversalPortfolioEngine()
    
    def handle_investment_query(self, budget):
        """Yatırım sorusuna cevap ver"""
        
        # Portföy oluştur
        portfolio = self.engine.recommend_portfolio(budget)
        
        # Projeksiyonlar
        projections = self.engine.calculate_projection(portfolio, months=12)
        final_value = projections[-1]['value']
        profit_12m = projections[-1]['profit']
        
        # Telegram mesajı
        message = f"""
╔══════════════════════════════════════╗
║ 💰 KİŞİSEL PORTFÖY ANALİZİ & TAVSİYESİ
╚══════════════════════════════════════╝

💵 Bütçe: ${budget:,.0f}

📊 PORTFÖY DAĞILIMI:
"""
        
        for alloc in portfolio['allocations']:
            message += f"\n  • {alloc['symbol']}: ${alloc['amount']:,.0f} ({alloc['amount']/budget*100:.0f}%)"
            if alloc['shares'] > 0:
                message += f" → {alloc['shares']} hisse"
        
        message += f"""

📈 BEKLENTİ (12 Ay):
  • Başlangıç: ${budget:,.0f}
  • Hedef: ${final_value:,.0f}
  • Tahmini Kar: ${profit_12m:,.0f}
  • ROI: {(profit_12m/budget)*100:.1f}%
  
⚠️ Risk Seviyesi: {portfolio['risk_level']}

🎯 STRATEJİ:
  1. Haftada 1 kontrol et
  2. Stop Loss: -5%
  3. Take Profit: +20%
  4. Zarar gördüğünde, az satarak düzelt

✅ AYLAR İTİBARİYLE GELİŞİM:
"""
        
        for proj in projections[::3]:  # Her 3 ayda bir
            message += f"\n  Ay {proj['month']}: ${proj['value']:,.0f} (Kar: ${proj['profit']:,.0f})"
        
        message += f"""

🔔 TELEGRAM ALARM:
  • Her gün analiz gönder
  • %10 fiyat değişiminde uyar
  • Yeni AL sinyalinde bildir
  
💡 TAVSIYE: Bu portföy LOW-MID risk seviyesindedir.
Agresif olmak istersen crypto oranını %50'ye çıkar.

⚠️ UYARI: Finansal tavsiye değildir. Riski kendin al.
"""
        
        return message
    
    def send_portfolio_analysis(self, budget):
        """Portföyü Telegram'a gönder"""
        msg = self.handle_investment_query(budget)
        self.telegram._send_message(msg)
        return msg
