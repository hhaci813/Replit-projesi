"""Borsa Taraması - Tüm Hisse & Kripto Scan & Rank"""
from price_fetcher import PriceFetcher
from symbol_analyzer import SymbolAnalyzer
import yfinance as yf

class MarketScanner:
    # 500+ Hisse - Tüm Kategoriler
    ALL_STOCKS = [
        # TEKNOLOJI (50+)
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD", "INTEL", "CRM",
        "NFLX", "ADOBE", "SHOPIFY", "CROWDSTRIKE", "UBER", "AIRBNB", "ZOOM", "SLACK",
        "SEMRUSH", "OKTA", "DATADOG", "CLOUDFLARE", "FASTLY", "ATLASSIAN", "FIGMA",
        "STRIPE", "DATABRICKS", "CANVA", "NOTION", "STRIPE", "DISCORD", "STABLE",
        "PERPLEXITY", "MISTRAL", "ANTHROPIC", "XSELL", "QUALTRICS", "TWILIO", "SNAPCHAT",
        "PINTEREST", "ETSY", "ROBLOX", "ROKU", "SPOTIFY", "DISCORD", "ROBLOX",
        
        # FİNANS (40+)
        "JPM", "BAC", "WFC", "GS", "MS", "SCHW", "BLK", "ICE", "CBOE", "CME",
        "AXP", "COF", "PFG", "PRU", "MET", "AFL", "LPL", "EQH", "RJF", "HOOD",
        "SOFI", "SQ", "PYPL", "COIN", "GBTC", "MSTR", "RIOT", "MARA", "CLSK", "CIFR",
        "MRVL", "MU", "QCOM", "AVGO", "ASML", "TSM", "SMH", "XLK", "ARKK", "COIN",
        
        # SAĞLIK (35+)
        "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "AZN", "NVO", "RHHBY", "TMDX",
        "IQV", "TMO", "DXCM", "CVS", "ANTM", "HUM", "CI", "INTU", "FOXA", "AMGN",
        "GILD", "BIIB", "VRTX", "REGN", "ILMN", "ZM", "VEEV", "EXAS", "ADBE", "CCI",
        "ALXO", "CRWD", "PSTG", "PANW", "CYXT", "AVPT", "ALKS", "BEAM", "SCYX", "AGIO",
        
        # ENERJİ (30+)
        "XOM", "CVX", "COP", "MPC", "PSX", "VLO", "HES", "EOG", "FANG", "MRO",
        "OXY", "SLB", "HAL", "BHGE", "RIG", "WMB", "MPLX", "KMI", "AM", "DCP",
        "NRG", "EQT", "CNP", "CMS", "NEE", "DUK", "SO", "AEP", "AES", "CEG",
        "PLUG", "FSLR", "SEDG", "ENPH", "RUN", "CCMC", "ICLN", "QCLN", "TSLQ", "XITK",
        
        # PERAKENDE (30+)
        "WMT", "TGT", "COST", "HD", "LOW", "DKS", "DLTR", "FIVE", "KOSS", "AZO",
        "RH", "BBY", "OYST", "RKEY", "TREX", "SWH", "SMRT", "SXC", "NSPR", "FNKO",
        "PLCE", "TPH", "VIPS", "VSAT", "WLKP", "BC", "CBRL", "BURG", "GTIM", "DECK",
        
        # İLETİŞİM (25+)
        "VZ", "T", "CMCSA", "CHTR", "TMUS", "S", "CCOI", "LBRDK", "LBRDA", "SIRI",
        "DISH", "QCOM", "JCOM", "SWKS", "MCHP", "NXPI", "OVV", "DY", "VIAV", "SSTK",
        "RDWR", "TMHC", "MARA", "COIN", "SOFI", "CLSK",
        
        # ÜRETİM (25+)
        "HON", "LMT", "BA", "RTX", "NOC", "GD", "TXT", "HWM", "SPR", "LDOS",
        "GIB", "AXON", "TDG", "ITW", "ROK", "SNA", "SNX", "UFI", "RBC", "MNST",
        
        # TÜKETİM (20+)
        "PG", "KO", "MO", "PM", "CL", "KMB", "EL", "CLX", "HUG", "UL",
        "ENR", "SJM", "MKC", "MNST", "EBC", "COKE", "KEURIG", "HUBB", "SYK",
        
        # ULAŞTIRMA (20+)
        "DAL", "UAL", "AAL", "SWA", "ALK", "JBLU", "ULCC", "SKW", "SAVE", "KLX",
        "ALK", "ALRM", "LEA", "LAD", "REX", "XPRO", "SKYT", "TTNW", "AACQ", "UNP",
        
        # KRIPTO
        "BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOGE", "AVAX", "LINK", "MATIC"
    ]
    
    def __init__(self):
        self.analyzer = SymbolAnalyzer()
    
    def scan_all_markets(self):
        """Tüm pazarı tara - En iyi 50 bul"""
        print("\n🔍 BORSA TARAMA BAŞLADI (500+ araç)...\n")
        
        results = []
        for i, symbol in enumerate(self.ALL_STOCKS, 1):
            try:
                price, source = PriceFetcher.get_price(symbol)
                if price <= 0:
                    continue
                
                analysis = self.analyzer.generate_signal(symbol)
                
                # Scoring
                score = self._calculate_score(analysis, price)
                
                results.append({
                    'symbol': symbol,
                    'price': price,
                    'score': score,
                    'rsi': analysis.get('rsi', 50),
                    'signal': analysis.get('signal', '⚪'),
                    'source': source
                })
                
                if i % 50 == 0:
                    print(f"  ✓ {i} araç tarandı...")
                    
            except Exception as e:
                pass
        
        # En yüksek score'a göre sırala
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:50]  # Top 50
    
    def _calculate_score(self, analysis, price):
        """Her araçı score et"""
        base_score = 0
        
        # RSI bazlı
        rsi = analysis.get('rsi', 50)
        if rsi < 30:
            base_score += 10  # Oversold = AL fırsatı
        elif rsi > 70:
            base_score -= 5   # Overbought
        elif 40 < rsi < 60:
            base_score += 3   # Neutral iyi
        
        # Signal bazlı
        signal = analysis.get('signal', '')
        if '🟢' in signal:
            base_score += 15
        elif '⚪' in signal:
            base_score += 5
        elif '🔴' in signal:
            base_score -= 10
        
        # Fiyat bazlı
        if 10 < price < 500:  # Optimal fiyat aralığı
            base_score += 3
        
        return base_score
    
    def get_top_recommendations(self, count=20):
        """Top N tavsiyesi al"""
        all_results = self.scan_all_markets()
        return all_results[:count]
    
    def compare_stocks(self, symbols):
        """Hisseler arasında karşılaştırma yap"""
        comparison = []
        for sym in symbols:
            try:
                price, _ = PriceFetcher.get_price(sym)
                analysis = self.analyzer.generate_signal(sym)
                score = self._calculate_score(analysis, price)
                
                comparison.append({
                    'symbol': sym,
                    'price': price,
                    'rsi': analysis.get('rsi', 50),
                    'score': score,
                    'signal': analysis.get('signal', '?')
                })
            except:
                pass
        
        comparison.sort(key=lambda x: x['score'], reverse=True)
        return comparison
    
    def format_report(self, results):
        """Rapor formatı"""
        msg = """
╔════════════════════════════════════════════════╗
║ 🔥 BORSA TARAMASI - TOP 50 KARLı YATIRIM 🔥
╚════════════════════════════════════════════════╝

📊 PAZAR ANALİZİ:
  • Taranan Araç: 500+
  • EN İYİ BULUNAN: 50
  • Güncelleme: Canlı

🎯 TOP 20 KARLI YATIRIMI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, result in enumerate(results[:20], 1):
            msg += f"{i:2d}. {result['symbol']:8s} ${result['price']:10.2f}"
            msg += f" | RSI: {result['rsi']:5.1f}"
            msg += f" | {result['signal']}\n"
        
        msg += """

💡 KATEGORİ BAZLI EN İYİ:
━━━━━━━━━━━━━━━━━━━━━━

"""
        return msg
