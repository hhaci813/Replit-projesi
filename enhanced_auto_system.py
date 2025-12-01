"""🚀 Enhanced Auto System - Email, Discord, Pump Detection"""
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime

class EnhancedAutoSystem:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.active_jobs = {}
    
    def start_all_enhanced(self):
        """Tüm enhanced özellikleri başlat"""
        if self.is_running:
            return "Zaten çalışıyor"
        
        # Email Digest - Günlük 09:00
        self.scheduler.add_job(
            self._send_email_digest,
            'cron',
            hour=9,
            minute=0,
            id='email_digest'
        )
        self.active_jobs['📧 Email Digest'] = 'Günlük 09:00'
        
        # Pump Detection - Her 15 dakika
        self.scheduler.add_job(
            self._detect_pumps,
            'interval',
            minutes=15,
            id='pump_detection'
        )
        self.active_jobs['🚀 Pump Detection'] = 'Her 15 dakika'
        
        # Discord Alerts - Her saat başı
        self.scheduler.add_job(
            self._send_discord_alert,
            'interval',
            hours=1,
            id='discord_alerts'
        )
        self.active_jobs['🎮 Discord Alerts'] = 'Her 1 saat'
        
        # Sentiment Analysis - Günlük 08:00
        self.scheduler.add_job(
            self._analyze_sentiment,
            'cron',
            hour=8,
            minute=0,
            id='sentiment_analysis'
        )
        self.active_jobs['🎯 Sentiment Analysis'] = 'Günlük 08:00'
        
        if not self.scheduler.running:
            self.scheduler.start()
        
        self.is_running = True
        return "✅ Enhanced sistemler başlatıldı"
    
    def _send_email_digest(self):
        """Günlük email raporu"""
        try:
            from email_alerts_service import EmailAlertsService
            from btcturk_market_scanner import BTCTurkMarketScanner
            
            scanner = BTCTurkMarketScanner()
            data = scanner.analyze_all()
            
            # Assets'i rising/falling'e ayır
            assets = data if isinstance(data, list) else []
            rising = [a for a in assets if a.get('change', 0) > 0]
            falling = [a for a in assets if a.get('change', 0) < 0]
            
            analysis_data = {
                'rising': sorted(rising, key=lambda x: x.get('change', 0), reverse=True),
                'falling': sorted(falling, key=lambda x: x.get('change', 0))
            }
            
            # Email hala config'e ihtiyaç var, ama template hazır
            print(f"✅ Email digest hazırlandı: {len(rising)} up, {len(falling)} down")
        except Exception as e:
            print(f"❌ Email digest hatası: {e}")
    
    def _detect_pumps(self):
        """Pump detection algıla"""
        try:
            from pump_detector import PumpDetector
            from btcturk_market_scanner import BTCTurkMarketScanner
            
            scanner = BTCTurkMarketScanner()
            data = scanner.analyze_all()
            
            detector = PumpDetector()
            assets = data if isinstance(data, list) else []
            
            pumps_detected = []
            for asset in assets:
                change = asset.get('change', 0)
                volume = asset.get('volume', 0)
                
                # Basit pump detection
                if change > 3:  # 3% dan fazla yükseliş
                    pumps_detected.append({
                        'symbol': asset.get('symbol'),
                        'change': change,
                        'price': asset.get('price')
                    })
            
            if pumps_detected:
                print(f"🚀 Pump Detected: {len(pumps_detected)} coins")
                for pump in pumps_detected[:3]:
                    print(f"   - {pump['symbol']}: +{pump['change']:.2f}%")
        
        except Exception as e:
            print(f"❌ Pump detection hatası: {e}")
    
    def _send_discord_alert(self):
        """Discord alert gönder"""
        try:
            # Discord token olmazsa skip
            import os
            if not os.getenv('DISCORD_BOT_TOKEN'):
                print("⚠️ Discord token ayarlanmamış")
                return
            
            print("✅ Discord alert hazırlıklı (token gerekli)")
        except Exception as e:
            print(f"❌ Discord alert hatası: {e}")
    
    def _analyze_sentiment(self):
        """Sentiment analysis yap"""
        try:
            from advanced_sentiment_analyzer import AdvancedSentimentAnalyzer
            
            analyzer = AdvancedSentimentAnalyzer()
            
            # Bitcoin, Ethereum, Crypto haberlerini analiz et
            for query in ["Bitcoin", "Ethereum", "Cryptocurrency"]:
                result = analyzer.analyze_news_sentiment(query)
                if result.get('total_articles', 0) > 0:
                    print(f"📰 {query}: {result.get('overall_sentiment')} ({result.get('total_articles')} articles)")
        
        except Exception as e:
            print(f"❌ Sentiment analysis hatası: {e}")
    
    def get_status(self):
        """Durum göster"""
        if not self.is_running:
            return "🔴 KAPALI"
        
        status = "🟢 ENHANCED SISTEM ÇALIŞIYOR\n\n"
        status += "📊 AKTIF JOB'LAR:\n"
        for job, schedule in self.active_jobs.items():
            status += f"   {job}: {schedule}\n"
        status += f"\n✅ Toplam: {len(self.active_jobs)} sistem"
        return status

if __name__ == "__main__":
    system = EnhancedAutoSystem()
    print(system.start_all_enhanced())
    print(system.get_status())
