"""
MAKRO EKONOMİK VERİ MODÜLü - TÜRKİYE
Dolar/TL, Euro/TL, Altın, Faiz, Enflasyon, BIST Endeksleri
Ücretsiz API'ler ve Web Scraping
"""

import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import logging
import re

logger = logging.getLogger(__name__)

class StockMacroData:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 dakika
    
    def get_cached(self, key: str, fetch_func, duration: int = None):
        """Cache mekanizması"""
        duration = duration or self.cache_duration
        now = time.time()
        if key in self.cache:
            if now - self.cache[key]['time'] < duration:
                return self.cache[key]['data']
        data = fetch_func()
        self.cache[key] = {'data': data, 'time': now}
        return data
    
    def get_currency_rates(self) -> Dict:
        """Döviz kurları - USD/TRY, EUR/TRY"""
        def fetch():
            try:
                # YFinance ile
                usd_try = yf.Ticker("USDTRY=X")
                eur_try = yf.Ticker("EURTRY=X")
                gbp_try = yf.Ticker("GBPTRY=X")
                
                usd_hist = usd_try.history(period="5d")
                eur_hist = eur_try.history(period="5d")
                gbp_hist = gbp_try.history(period="5d")
                
                usd_rate = float(usd_hist['Close'].iloc[-1]) if len(usd_hist) > 0 else 0
                eur_rate = float(eur_hist['Close'].iloc[-1]) if len(eur_hist) > 0 else 0
                gbp_rate = float(gbp_hist['Close'].iloc[-1]) if len(gbp_hist) > 0 else 0
                
                # Değişim hesapla
                usd_prev = float(usd_hist['Close'].iloc[-2]) if len(usd_hist) > 1 else usd_rate
                eur_prev = float(eur_hist['Close'].iloc[-2]) if len(eur_hist) > 1 else eur_rate
                
                usd_change = ((usd_rate - usd_prev) / usd_prev * 100) if usd_prev > 0 else 0
                eur_change = ((eur_rate - eur_prev) / eur_prev * 100) if eur_prev > 0 else 0
                
                return {
                    'USD_TRY': {
                        'rate': round(usd_rate, 4),
                        'change': round(usd_change, 2),
                        'trend': 'YÜKSELEN' if usd_change > 0 else 'DÜŞEN'
                    },
                    'EUR_TRY': {
                        'rate': round(eur_rate, 4),
                        'change': round(eur_change, 2),
                        'trend': 'YÜKSELEN' if eur_change > 0 else 'DÜŞEN'
                    },
                    'GBP_TRY': {
                        'rate': round(gbp_rate, 4),
                        'change': 0,
                        'trend': 'N/A'
                    },
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Döviz kuru hatası: {e}")
                return {
                    'USD_TRY': {'rate': 0, 'change': 0, 'trend': 'N/A'},
                    'EUR_TRY': {'rate': 0, 'change': 0, 'trend': 'N/A'},
                    'GBP_TRY': {'rate': 0, 'change': 0, 'trend': 'N/A'}
                }
        
        return self.get_cached('currency_rates', fetch, 300)
    
    def get_gold_price(self) -> Dict:
        """Altın fiyatları - Gram, Ons"""
        def fetch():
            try:
                # Ons altın (USD)
                gold_usd = yf.Ticker("GC=F")
                gold_hist = gold_usd.history(period="5d")
                
                ons_usd = float(gold_hist['Close'].iloc[-1]) if len(gold_hist) > 0 else 0
                ons_prev = float(gold_hist['Close'].iloc[-2]) if len(gold_hist) > 1 else ons_usd
                ons_change = ((ons_usd - ons_prev) / ons_prev * 100) if ons_prev > 0 else 0
                
                # USD/TRY al
                currency = self.get_currency_rates()
                usd_try = currency.get('USD_TRY', {}).get('rate', 34.5)
                
                # Gram altın hesapla (1 ons = 31.1 gram)
                gram_tl = (ons_usd / 31.1) * usd_try
                
                return {
                    'ons_usd': round(ons_usd, 2),
                    'ons_change': round(ons_change, 2),
                    'gram_tl': round(gram_tl, 2),
                    'trend': 'YÜKSELEN' if ons_change > 0 else 'DÜŞEN',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Altın fiyatı hatası: {e}")
                return {'ons_usd': 0, 'gram_tl': 0, 'ons_change': 0, 'trend': 'N/A'}
        
        return self.get_cached('gold_price', fetch, 300)
    
    def get_bist_indices(self) -> Dict:
        """BIST Endeksleri - XU100, XU030, XBANK, XUSIN"""
        def fetch():
            try:
                indices = {
                    'XU100': 'XU100.IS',  # BIST 100
                    'XU030': 'XU030.IS',  # BIST 30
                    'XBANK': 'XBANK.IS',  # Banka Endeksi
                    'XUSIN': 'XUSIN.IS',  # Sınai Endeksi
                    'XHOLD': 'XHOLD.IS',  # Holding Endeksi
                    'XILTM': 'XILTM.IS',  # İletişim Endeksi
                }
                
                result = {}
                
                for name, ticker in indices.items():
                    try:
                        idx = yf.Ticker(ticker)
                        hist = idx.history(period="5d")
                        
                        if len(hist) > 0:
                            current = float(hist['Close'].iloc[-1])
                            prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
                            change = ((current - prev) / prev * 100) if prev > 0 else 0
                            
                            result[name] = {
                                'value': round(current, 2),
                                'change': round(change, 2),
                                'trend': 'YÜKSELEN' if change > 0 else 'DÜŞEN'
                            }
                    except:
                        result[name] = {'value': 0, 'change': 0, 'trend': 'N/A'}
                
                result['timestamp'] = datetime.now().isoformat()
                return result
                
            except Exception as e:
                logger.error(f"BIST endeks hatası: {e}")
                return {}
        
        return self.get_cached('bist_indices', fetch, 300)
    
    def get_interest_rates(self) -> Dict:
        """Faiz oranları (TCMB politika faizi tahmini)"""
        def fetch():
            try:
                # US Treasury 10Y yield (global referans)
                tnx = yf.Ticker("^TNX")
                tnx_hist = tnx.history(period="5d")
                us_10y = float(tnx_hist['Close'].iloc[-1]) if len(tnx_hist) > 0 else 0
                
                # Türkiye 10Y bond yield (yaklaşık - USD bazlı)
                # TCMB politika faizi şu an %50 civarı (2024)
                tcmb_policy = 50.0  # Manuel güncellenmeli
                
                return {
                    'TCMB_policy': tcmb_policy,
                    'US_10Y': round(us_10y, 2),
                    'spread': round(tcmb_policy - us_10y, 2),
                    'environment': 'YÜKSEK FAİZ' if tcmb_policy > 30 else 'NORMAL',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Faiz oranı hatası: {e}")
                return {'TCMB_policy': 50.0, 'US_10Y': 0, 'environment': 'N/A'}
        
        return self.get_cached('interest_rates', fetch, 600)
    
    def get_full_macro_summary(self) -> Dict:
        """Tüm makro verilerin özeti"""
        currency = self.get_currency_rates()
        gold = self.get_gold_price()
        bist = self.get_bist_indices()
        interest = self.get_interest_rates()
        
        # Genel piyasa durumu
        bist100_change = bist.get('XU100', {}).get('change', 0)
        usd_change = currency.get('USD_TRY', {}).get('change', 0)
        
        if bist100_change > 1 and usd_change < 0.5:
            market_mood = 'RİSK İŞTAHI'
        elif bist100_change < -1 or usd_change > 1:
            market_mood = 'RİSK KAÇINMASI'
        else:
            market_mood = 'NÖTR'
        
        return {
            'currency': currency,
            'gold': gold,
            'bist': bist,
            'interest': interest,
            'market_mood': market_mood,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_macro_report(self) -> str:
        """Telegram için makro rapor"""
        data = self.get_full_macro_summary()
        
        currency = data.get('currency', {})
        gold = data.get('gold', {})
        bist = data.get('bist', {})
        interest = data.get('interest', {})
        
        usd = currency.get('USD_TRY', {})
        eur = currency.get('EUR_TRY', {})
        xu100 = bist.get('XU100', {})
        xu030 = bist.get('XU030', {})
        xbank = bist.get('XBANK', {})
        
        mood_emoji = "🟢" if data['market_mood'] == 'RİSK İŞTAHI' else "🔴" if data['market_mood'] == 'RİSK KAÇINMASI' else "⚪"
        
        report = f"""🌍 <b>MAKRO EKONOMİK DURUM</b>
━━━━━━━━━━━━━━━━━━━━━

{mood_emoji} <b>Piyasa:</b> {data['market_mood']}

💱 <b>DÖVİZ</b>
   💵 USD/TRY: ₺{usd.get('rate', 0):.4f} ({usd.get('change', 0):+.2f}%)
   💶 EUR/TRY: ₺{eur.get('rate', 0):.4f} ({eur.get('change', 0):+.2f}%)

🥇 <b>ALTIN</b>
   📊 Ons: ${gold.get('ons_usd', 0):.2f} ({gold.get('ons_change', 0):+.2f}%)
   📊 Gram: ₺{gold.get('gram_tl', 0):.2f}

📈 <b>BIST ENDEKSLERİ</b>
   🔹 XU100: {xu100.get('value', 0):,.0f} ({xu100.get('change', 0):+.2f}%)
   🔹 XU030: {xu030.get('value', 0):,.0f} ({xu030.get('change', 0):+.2f}%)
   🏦 XBANK: {xbank.get('value', 0):,.0f} ({xbank.get('change', 0):+.2f}%)

💰 <b>FAİZ</b>
   🇹🇷 TCMB: %{interest.get('TCMB_policy', 0):.1f}
   🇺🇸 US 10Y: %{interest.get('US_10Y', 0):.2f}

━━━━━━━━━━━━━━━━━━━━━
🤖 <i>Makro Ekonomik Analiz</i>
"""
        return report
