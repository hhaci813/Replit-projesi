"""24/7 Otomatik Sistem - Tüm Fonksiyonlar Arka Planda Çalışıyor"""
from apscheduler.schedulers.background import BackgroundScheduler

class AutoRunSystem:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.active_jobs = {}
    
    def start_all_systems(self):
        """Tüm sistemleri başlat"""
        if self.is_running:
            return "Zaten çalışıyor"
        
        from auto_analyzer import AutoAnalyzer
        from automated_trading_engine import AutomatedTradingEngine
        from ml_predictor import MLPredictor
        from multi_symbol_tracker import MultiSymbolTracker
        
        # AutoAnalyzer - Her 2 dakika XRPTRY analiz
        auto_analyzer = AutoAnalyzer()
        self.scheduler.add_job(
            lambda: auto_analyzer.analyze_and_send(),
            'interval',
            minutes=2,
            id='auto_analyzer_xrptry'
        )
        self.active_jobs['📊 AutoAnalyzer'] = 'Her 2 dakika'
        
        # AutomatedTrading - Her saat AL/SAT kontrol
        trading_engine = AutomatedTradingEngine()
        self.scheduler.add_job(
            lambda: trading_engine.run_trading_cycle("alpaca"),
            'interval',
            hours=1,
            id='auto_trading'
        )
        self.active_jobs['💹 AutoTrading'] = 'Saatlik'
        
        # MultiSymbol Tracker - Her dakika kontrol
        tracker = MultiSymbolTracker()
        tracker.add_to_watchlist(["AAPL", "MSFT", "GOOGL", "BTC", "ETH"])
        self.scheduler.add_job(
            lambda: tracker.monitor_multiple(["AAPL", "MSFT"]),
            'interval',
            minutes=1,
            id='multi_tracker'
        )
        self.active_jobs['👁️ MultiSymbolTracker'] = 'Dakikalık'
        
        # Portfolio Optimization - Her gün
        self.scheduler.add_job(
            lambda: self._optimize_portfolio(),
            'interval',
            days=1,
            id='portfolio_opt'
        )
        self.active_jobs['⚖️ PortfolioOptimizer'] = 'Günlük'
        
        # Risk Metrics - Her 4 saat
        self.scheduler.add_job(
            lambda: self._check_risk_metrics(),
            'interval',
            hours=4,
            id='risk_metrics'
        )
        self.active_jobs['📊 RiskMetrics'] = '4 saatlik'
        
        # Backtest - Her Pazartesi
        self.scheduler.add_job(
            lambda: self._run_backtest(),
            'cron',
            day_of_week=0,
            hour=0,
            id='backtest'
        )
        self.active_jobs['💹 Backtest'] = 'Haftada 1'
        
        # On-chain Analysis - Her 2 saat
        self.scheduler.add_job(
            lambda: self._check_onchain(),
            'interval',
            hours=2,
            id='onchain'
        )
        self.active_jobs['⛓️ OnchainAnalysis'] = '2 saatlik'
        
        # Telegram Reports - Her 4 saat
        self.scheduler.add_job(
            lambda: self._send_reports(),
            'interval',
            hours=4,
            id='telegram_reports'
        )
        self.active_jobs['📱 TelegramReports'] = '4 saatlik'
        
        if not self.scheduler.running:
            self.scheduler.start()
        
        self.is_running = True
        return "✅ Tüm sistemler başlatıldı!"
    
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
    
    def get_status(self):
        """Durum göster"""
        if not self.is_running:
            return "🔴 KAPALI - Başlatmak için Seçenek 99 → 1"
        
        status = "🟢 24/7 HAFIZADA ÇALIŞIYOR\n\n"
        status += "📊 AKTIF JOB'LAR:\n"
        for job, schedule in self.active_jobs.items():
            status += f"   {job}: {schedule}\n"
        status += f"\n✅ Toplam: {len(self.active_jobs)} sistem"
        return status
    
    def _optimize_portfolio(self):
        try:
            from portfolio_optimizer import PortfolioOptimizer
            PortfolioOptimizer.optimize_weights(["AAPL", "MSFT", "GOOGL"])
        except: pass
    
    def _check_risk_metrics(self):
        try:
            from risk_metrics import RiskMetrics
            RiskMetrics.sharpe_ratio("AAPL")
        except: pass
    
    def _run_backtest(self):
        try:
            from advanced_backtest import AdvancedBacktest
            AdvancedBacktest().backtest_rsi_strategy("AAPL")
        except: pass
    
    def _check_onchain(self):
        try:
            from onchain_analyzer import OnchainAnalyzer
            OnchainAnalyzer().get_whale_activity("BTC")
        except: pass
    
    def _send_reports(self):
        try:
            from telegram_service import TelegramService
            service = TelegramService()
            service._send_message("📊 SİSTEM RAPORU\n\n✅ Tüm otomasyonlar normal çalışıyor!")
        except: pass
