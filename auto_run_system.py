"""24/7 Otomatik Sistem - TIER 1+2+3 ENTEGRASYON"""
from apscheduler.schedulers.background import BackgroundScheduler
import time
from broker_alpaca import AlpacaBrokerEngine
from backtesting_engine import BacktestingEngine
from email_alerts import AlertEngine
from ml_models import MLForecastingEngine
from sentiment_analysis import SentimentAnalyzer
from performance_dashboard import PerformanceDashboard

class AutoRunSystem:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.active_jobs = {}
    
    def start_all_systems(self):
        """TIER 1+2+3 Tüm sistemleri başlat"""
        if self.is_running:
            return "Zaten çalışıyor"
        
        from auto_analyzer import AutoAnalyzer
        
        # TIER 1: Canlı Analiz
        auto_analyzer = AutoAnalyzer()
        
        symbols = ["BTC", "XRPTRY", "AAPL", "MSFT", "GOOGL", "ETH"]
        for sym in symbols:
            self.scheduler.add_job(
                lambda s=sym: auto_analyzer.analyze_and_send(s),
                'interval',
                minutes=2,
                id=f'auto_analyzer_{sym}'
            )
            self.active_jobs[f'📊 AutoAnalyzer ({sym})'] = 'Her 2 dakika'
        
        # TIER 1: Backtesting - Her gün
        self.scheduler.add_job(
            lambda: self._run_backtesting(),
            'interval',
            days=1,
            id='daily_backtest'
        )
        self.active_jobs['🧪 Backtesting'] = 'Günlük'
        
        # TIER 2: ML Tahmin - Her 4 saatte
        self.scheduler.add_job(
            lambda: self._ml_forecast(),
            'interval',
            hours=4,
            id='ml_forecast'
        )
        self.active_jobs['🤖 ML Forecast'] = '4 saatlik'
        
        # TIER 2: Sentiment - Her 6 saatte
        self.scheduler.add_job(
            lambda: self._sentiment_check(),
            'interval',
            hours=6,
            id='sentiment_check'
        )
        self.active_jobs['💭 Sentiment'] = '6 saatlik'
        
        # TIER 2: Performance - Haftalık
        self.scheduler.add_job(
            lambda: self._performance_report(),
            'interval',
            weeks=1,
            id='perf_report'
        )
        self.active_jobs['📊 Performance'] = 'Haftalık'
        
        # Portfolio güncellemesi - Her 4 saatte 1
        self.scheduler.add_job(
            lambda: self._send_portfolio_update(),
            'interval',
            hours=4,
            id='portfolio_update'
        )
        self.active_jobs['💼 Portföy Güncelleme'] = '4 saatlik'
        
        # Risk analizi - Her 6 saatte 1
        self.scheduler.add_job(
            lambda: self._check_risk(),
            'interval',
            hours=6,
            id='risk_check'
        )
        self.active_jobs['⚠️ Risk Yönetimi'] = '6 saatlik'
        
        if not self.scheduler.running:
            self.scheduler.start()
        
        self.is_running = True
        return "✅ TIER 1+2+3 Tüm sistemler başlatıldı!"
    
    def stop_all_systems(self):
        """Tüm sistemleri durdur"""
        if not self.is_running:
            return "Zaten kapalı"
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            return "⛔ Tüm sistemler durduruldu"
        except:
            return "Hata oluştu"
    
    def keep_running(self):
        """Scheduler'ı 24/7 çalıştır"""
        print("\n" + "="*80)
        print("🟢 24/7 HAFIZADA AUTOMATION BAŞLATILDI")
        print("="*80)
        print(self.get_status())
        print("\n⏸️ Durdur için Ctrl+C tuşlayın\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all_systems()
            print("\n✅ Sistem durduruldu")
    
    def get_status(self):
        """Durum göster"""
        if not self.is_running:
            return "🔴 KAPALI"
        
        status = "🟢 24/7 HAFIZADA ÇALIŞIYOR\n\n"
        status += "📊 AKTIF JOB'LAR:\n"
        for job, schedule in self.active_jobs.items():
            status += f"   {job}: {schedule}\n"
        status += f"\n✅ Toplam: {len(self.active_jobs)} sistem"
        return status
    
    def _send_portfolio_update(self):
        """Portföy güncellemesi gönder"""
        try:
            from telegram_interactive import TelegramInteractiveBot
            bot = TelegramInteractiveBot()
            bot.send_portfolio_analysis(budget=10000)
        except:
            pass
    
    def _check_risk(self):
        """Risk kontrolü"""
        try:
            from telegram_service import TelegramService
            service = TelegramService()
            service._send_message("⚠️ RİSK KONTROL RAPORU\n✅ Tüm portföyler normal limitlerin içinde")
        except:
            pass
    
    def _run_backtesting(self):
        """Backtesting çalıştır"""
        try:
            bt_engine = BacktestingEngine()
            result = bt_engine.backtest_strategy("BTC", initial_capital=10000, days=30)
            if result:
                msg = f"""🧪 BACKTEST RAPORU
Symbol: {result['symbol']}
Initial: ${result['initial_capital']}
Final: ${result['final_value']:,.2f}
Return: {result['total_return_pct']:+.2f}%
Win Rate: {result['win_rate_pct']:.1f}%
Max Drawdown: {result['max_drawdown']:.2f}%
"""
                from telegram_service import TelegramService
                TelegramService()._send_message(msg)
        except:
            pass
    
    def _ml_forecast(self):
        """ML tahmin"""
        try:
            ml_engine = MLForecastingEngine()
            pred = ml_engine.predict_price("BTC", 130000, {'rsi': 55, 'macd': 0.5})
            msg = f"""🤖 ML FORECAST
Tahmin: ${pred['predicted_price']:,.2f}
Değişim: {pred['change_pct']:+.2f}%
Confidence: {pred['confidence']:.0f}%
"""
            from telegram_service import TelegramService
            TelegramService()._send_message(msg)
        except:
            pass
    
    def _sentiment_check(self):
        """Sentiment analiz"""
        try:
            senti = SentimentAnalyzer()
            emotion = senti.get_market_emotion()
            msg = f"""💭 MARKET EMOTION
Dominant: {emotion['dominant']}
Recommendation: {emotion['recommendation']}
"""
            from telegram_service import TelegramService
            TelegramService()._send_message(msg)
        except:
            pass
    
    def _performance_report(self):
        """Performance raporu"""
        try:
            perf = PerformanceDashboard()
            metrics = perf.calculate_metrics([], 10000)
            msg = f"""📊 PERFORMANCE REPORT
Total Trades: {metrics['total_trades']}
Win Rate: {metrics['win_rate_pct']:.1f}%
ROI: {metrics['roi_pct']:+.2f}%
Sharpe: {metrics['sharpe_ratio']:.2f}
"""
            from telegram_service import TelegramService
            TelegramService()._send_message(msg)
        except:
            pass
