"""Evrensel Portföy Motoru - 100+ Yatırım Aracı Analizi & Tavsiye"""
from price_fetcher import PriceFetcher
from symbol_analyzer import SymbolAnalyzer
import json

class UniversalPortfolioEngine:
    # 100+ Yatırım Aracı
    ALL_SYMBOLS = {
        "KRIPTO": ["BTC", "ETH", "XRPTRY", "BNB", "SOL", "ADA", "XRP", "DOGE", "AVAX", "LINK"],
        "TEKNOLOJI": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD", "INTEL", "CRM"],
        "FINANS": ["JPM", "BAC", "WFC", "GS", "MS", "SCHW", "BLK", "ICE", "CBOE", "CME"],
        "SAĞLIK": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "AZN", "NVO", "RHHBY", "TMDX"],
        "ENERJİ": ["XOM", "CVX", "COP", "MPC", "PSX", "VLO", "HES", "EOG", "FANG", "MRO"],
        "PERAKENDE": ["WMT", "TGT", "COST", "HD", "LOW", "DKS", "DLTR", "FIVE", "KOSS", "AZO"],
        "İLETİŞİM": ["VZ", "T", "CMCSA", "CHTR", "TMUS", "S", "CCOI", "LBRDK", "LBRDA", "SIRI"],
        "İNŞAAT": ["HON", "LMT", "BA", "RTX", "NOC", "GD", "TXT", "HWM", "SPR", "LDOS"],
        "TÜKETİM": ["PG", "KO", "MO", "PM", "CL", "KMB", "EL", "CLX", "HUG", "UL"],
        "ULAŞTIRMA": ["DAL", "UAL", "AAL", "SWA", "ALK", "JBLU", "ULCC", "SKW", "SAVE", "KLX"]
    }
    
    def __init__(self):
        self.analyzer = SymbolAnalyzer()
    
    def analyze_all_symbols(self):
        """Tüm 100+ symbolu analiz et"""
        results = {}
        for category, symbols in self.ALL_SYMBOLS.items():
            results[category] = {}
            for sym in symbols:
                try:
                    result = self.analyzer.generate_signal(sym)
                    price, source = PriceFetcher.get_price(sym)
                    
                    results[category][sym] = {
                        'signal': result.get('signal', '?'),
                        'price': price,
                        'rsi': result.get('rsi', 50),
                        'ma20': result.get('ma20', 0),
                        'score': result.get('score', 0)
                    }
                except:
                    pass
        return results
    
    def recommend_portfolio(self, budget):
        """Bütçeye göre portföy öner"""
        results = self.analyze_all_symbols()
        
        # AL sinyali olanları bul
        buy_signals = []
        for category, symbols in results.items():
            for sym, data in symbols.items():
                if "🟢" in data['signal']:
                    buy_signals.append({
                        'symbol': sym,
                        'category': category,
                        'score': data['score'],
                        'price': data['price'],
                        'rsi': data['rsi']
                    })
        
        # Score'a göre sırala
        buy_signals.sort(key=lambda x: x['score'], reverse=True)
        
        # Top 10 al
        top_symbols = buy_signals[:10]
        
        if not top_symbols:
            return self._default_portfolio(budget)
        
        # Equal weight
        per_symbol = budget / len(top_symbols) if top_symbols else budget
        
        portfolio = {
            'symbols': [],
            'total_budget': budget,
            'allocations': [],
            'expected_roi': 0,
            'risk_level': 'ORTA'
        }
        
        for i, sym_data in enumerate(top_symbols):
            allocation = per_symbol
            shares = int(allocation / sym_data['price']) if sym_data['price'] > 0 else 0
            
            portfolio['symbols'].append(sym_data['symbol'])
            portfolio['allocations'].append({
                'symbol': sym_data['symbol'],
                'amount': allocation,
                'shares': shares,
                'price': sym_data['price'],
                'category': sym_data['category'],
                'score': sym_data['score'],
                'roi_estimate': 12  # 12% yıllık
            })
            portfolio['expected_roi'] += 12 / len(top_symbols)
        
        return portfolio
    
    def _default_portfolio(self, budget):
        """Sinyal yoksa dengeli portföy sun"""
        return {
            'symbols': ['BTC', 'AAPL', 'MSFT', 'GOOGL', 'JPM', 'JNJ'],
            'total_budget': budget,
            'allocations': [
                {'symbol': 'BTC', 'amount': budget * 0.15, 'shares': 0, 'roi_estimate': 25},
                {'symbol': 'AAPL', 'amount': budget * 0.2, 'shares': 0, 'roi_estimate': 12},
                {'symbol': 'MSFT', 'amount': budget * 0.2, 'shares': 0, 'roi_estimate': 10},
                {'symbol': 'GOOGL', 'amount': budget * 0.15, 'shares': 0, 'roi_estimate': 10},
                {'symbol': 'JPM', 'amount': budget * 0.15, 'shares': 0, 'roi_estimate': 8},
                {'symbol': 'JNJ', 'amount': budget * 0.15, 'shares': 0, 'roi_estimate': 6},
            ],
            'expected_roi': 12,
            'risk_level': 'DÜŞÜK'
        }
    
    def calculate_projection(self, portfolio, months=12):
        """Kazanç projeksiyonu yap"""
        total = portfolio['total_budget']
        roi = portfolio['expected_roi']
        
        monthly_rate = (1 + roi/100) ** (1/12) - 1
        
        projections = []
        for month in range(0, months + 1):
            value = total * ((1 + monthly_rate) ** month)
            profit = value - total
            projections.append({
                'month': month,
                'value': value,
                'profit': profit,
                'roi_percent': (profit / total) * 100
            })
        
        return projections

if __name__ == "__main__":
    engine = UniversalPortfolioEngine()
    
    # Test
    portfolio = engine.recommend_portfolio(budget=10000)
    print(json.dumps(portfolio, indent=2, default=str))
