"""
Web Kontrol Paneli ve REST API
Flask-based dashboard with real-time data and API endpoints
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

def get_portfolio_data():
    """Portföy verisi"""
    try:
        from real_trader import BTCTurkTrader
        trader = BTCTurkTrader()
        return trader.get_balance()
    except:
        return {}

def get_signal_stats():
    """Sinyal istatistikleri"""
    try:
        from real_trader import SignalTracker
        tracker = SignalTracker()
        return tracker.get_stats()
    except:
        return {}

def get_market_data():
    """Piyasa verileri"""
    try:
        import requests
        resp = requests.get("https://api.btcturk.com/api/v2/ticker", timeout=10)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            try_pairs = [d for d in data if d['pairNormalized'].endswith('_TRY')]
            return sorted(try_pairs, key=lambda x: float(x.get('volume', 0)), reverse=True)[:20]
        return []
    except:
        return []

def get_strategies():
    """Stratejiler"""
    try:
        from strategy_builder import StrategyBuilder
        builder = StrategyBuilder()
        return builder.list_strategies()
    except:
        return []

def get_backtest_results():
    """Backtest sonuçları"""
    results_file = Path('backtest_results.json')
    if results_file.exists():
        with open(results_file, 'r') as f:
            return json.load(f).get('results', [])[-10:]
    return []

@app.route('/')
def dashboard():
    """Ana dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Sistem durumu"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'modules': {
            'trader': True,
            'binance': True,
            'strategies': True,
            'backtest': True,
            'signals': True
        }
    })

@app.route('/api/portfolio')
def api_portfolio():
    """Portföy API"""
    try:
        from real_trader import BTCTurkTrader
        trader = BTCTurkTrader()
        balances = trader.get_balance()
        stats = trader.get_trade_stats()
        return jsonify({
            'success': True,
            'balances': balances,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/market')
def api_market():
    """Piyasa verileri API"""
    try:
        data = get_market_data()
        return jsonify({
            'success': True,
            'count': len(data),
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ticker/<symbol>')
def api_ticker(symbol):
    """Tek coin fiyat API"""
    try:
        import requests
        resp = requests.get(
            f"https://api.btcturk.com/api/v2/ticker?pairSymbol={symbol.upper()}TRY",
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            if data:
                return jsonify({'success': True, 'data': data[0]})
        return jsonify({'success': False, 'error': 'Veri bulunamadı'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/signals')
def api_signals():
    """Sinyal istatistikleri API"""
    try:
        from real_trader import SignalTracker
        tracker = SignalTracker()
        return jsonify({
            'success': True,
            'stats': tracker.get_stats(),
            'recent': tracker.signals.get('signals', [])[-20:]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/strategies')
def api_strategies():
    """Stratejiler API"""
    try:
        from strategy_builder import StrategyBuilder, format_prebuilt_strategies
        builder = StrategyBuilder()
        return jsonify({
            'success': True,
            'user_strategies': builder.list_strategies(),
            'active': builder.list_active_strategies(),
            'prebuilt_count': 5
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/strategies', methods=['POST'])
def api_create_strategy():
    """Strateji oluştur API"""
    try:
        from strategy_builder import StrategyBuilder
        data = request.json
        
        builder = StrategyBuilder()
        result = builder.create_strategy(
            name=data.get('name', 'Yeni Strateji'),
            description=data.get('description', ''),
            buy_conditions=data.get('buy_conditions', []),
            sell_conditions=data.get('sell_conditions', []),
            risk_params=data.get('risk_params')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/strategies/<strategy_id>/activate', methods=['POST'])
def api_activate_strategy(strategy_id):
    """Strateji aktif et API"""
    try:
        from strategy_builder import StrategyBuilder
        builder = StrategyBuilder()
        result = builder.activate_strategy(strategy_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/strategies/<strategy_id>/deactivate', methods=['POST'])
def api_deactivate_strategy(strategy_id):
    """Strateji deaktif et API"""
    try:
        from strategy_builder import StrategyBuilder
        builder = StrategyBuilder()
        result = builder.deactivate_strategy(strategy_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backtest')
def api_backtest_results():
    """Backtest sonuçları API"""
    try:
        results = get_backtest_results()
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backtest/run', methods=['POST'])
def api_run_backtest():
    """Backtest çalıştır API"""
    try:
        from advanced_backtest import AdvancedBacktester
        data = request.json
        
        backtester = AdvancedBacktester()
        result = backtester.run_backtest(
            symbol=data.get('symbol', 'BTC'),
            strategy_name=data.get('strategy', 'RSI'),
            prices=data.get('prices', []),
            trades=data.get('trades', []),
            initial_capital=data.get('initial_capital', 10000)
        )
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trade', methods=['POST'])
def api_trade():
    """Trade API (gerçek işlem)"""
    try:
        from real_trader import BTCTurkTrader
        data = request.json
        
        trader = BTCTurkTrader()
        
        order_type = data.get('order_type', 'market')
        
        if order_type == 'market':
            result = trader.place_market_order(
                symbol=data.get('symbol'),
                side=data.get('side'),
                quantity=data.get('quantity'),
                amount_tl=data.get('amount_tl')
            )
        elif order_type == 'limit':
            result = trader.place_limit_order(
                symbol=data.get('symbol'),
                side=data.get('side'),
                quantity=data.get('quantity'),
                price=data.get('price')
            )
        elif order_type == 'stop':
            result = trader.place_stop_order(
                symbol=data.get('symbol'),
                side=data.get('side'),
                quantity=data.get('quantity'),
                stop_price=data.get('stop_price'),
                limit_price=data.get('limit_price')
            )
        else:
            result = {'success': False, 'error': 'Geçersiz order tipi'}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/orders')
def api_open_orders():
    """Açık orderlar API"""
    try:
        from real_trader import BTCTurkTrader
        trader = BTCTurkTrader()
        orders = trader.get_open_orders()
        return jsonify({'success': True, 'orders': orders})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/orders/<order_id>', methods=['DELETE'])
def api_cancel_order(order_id):
    """Order iptal API"""
    try:
        from real_trader import BTCTurkTrader
        trader = BTCTurkTrader()
        result = trader.cancel_order(order_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/binance/market')
def api_binance_market():
    """Binance piyasa API"""
    try:
        from binance_trader import BinanceTrader
        binance = BinanceTrader()
        gainers = binance.get_top_gainers(10)
        losers = binance.get_top_losers(10)
        return jsonify({
            'success': True,
            'gainers': gainers,
            'losers': losers
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/compare/<symbol>')
def api_compare_prices(symbol):
    """Fiyat karşılaştırma API"""
    try:
        from binance_trader import MultiExchangeAggregator
        aggregator = MultiExchangeAggregator()
        result = aggregator.compare_prices(symbol)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze/<symbol>')
def api_analyze(symbol):
    """Coin analiz API"""
    try:
        from chart_generator import ChartGenerator
        from chart_analyzer import ChartAnalyzer
        import requests
        
        ticker_resp = requests.get(
            f"https://api.btcturk.com/api/v2/ticker?pairSymbol={symbol.upper()}TRY",
            timeout=10
        )
        current_price = 0
        if ticker_resp.status_code == 200:
            data = ticker_resp.json().get('data', [])
            if data:
                current_price = float(data[0].get('last', 0))
        
        chart_gen = ChartGenerator()
        chart_path = chart_gen.create_price_chart(symbol, days=30)
        
        if chart_path:
            analyzer = ChartAnalyzer()
            analysis = analyzer.analyze_chart(chart_path)
            
            import os
            try:
                os.remove(chart_path)
            except:
                pass
            
            return jsonify({
                'success': True,
                'symbol': symbol,
                'current_price': current_price,
                'analysis': analysis
            })
        
        return jsonify({'success': False, 'error': 'Grafik oluşturulamadı'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def create_dashboard_template():
    """Dashboard HTML template oluştur"""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    html = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akıllı Yatırım Asistanı - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff; 
            min-height: 100vh;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #333;
        }
        .header h1 { color: #00d4ff; font-size: 28px; }
        .header p { color: #888; margin-top: 5px; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h3 { color: #00d4ff; margin-bottom: 15px; font-size: 16px; }
        .stat-value { font-size: 28px; font-weight: bold; }
        .stat-label { color: #888; font-size: 12px; margin-top: 5px; }
        .positive { color: #00ff88; }
        .negative { color: #ff4444; }
        .coin-row { 
            display: flex; 
            justify-content: space-between; 
            padding: 10px 0; 
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .coin-name { font-weight: bold; }
        .coin-price { color: #00d4ff; }
        .api-status { 
            display: inline-block; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 12px;
        }
        .status-online { background: #00ff8822; color: #00ff88; }
        .btn {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            font-weight: bold;
            margin: 5px;
        }
        .btn:hover { opacity: 0.9; }
        .btn-sell { background: linear-gradient(135deg, #ff4444, #cc0000); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { color: #888; font-size: 12px; }
        .loading { text-align: center; padding: 40px; color: #888; }
        #market-table { max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Akıllı Yatırım Asistanı</h1>
        <p>Gerçek Zamanlı Kripto Analiz & Trading Dashboard</p>
        <span id="api-status" class="api-status">Yükleniyor...</span>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- Portföy Özeti -->
            <div class="card">
                <h3>💰 PORTFÖY</h3>
                <div id="portfolio-content" class="loading">Yükleniyor...</div>
            </div>
            
            <!-- Sinyal Performansı -->
            <div class="card">
                <h3>📊 SİNYAL PERFORMANSI</h3>
                <div id="signals-content" class="loading">Yükleniyor...</div>
            </div>
            
            <!-- Stratejiler -->
            <div class="card">
                <h3>🎯 AKTİF STRATEJİLER</h3>
                <div id="strategies-content" class="loading">Yükleniyor...</div>
            </div>
            
            <!-- Hızlı Trade -->
            <div class="card">
                <h3>⚡ HIZLI TRADE</h3>
                <div style="margin-top: 10px;">
                    <input type="text" id="trade-symbol" placeholder="Sembol (BTC)" 
                           style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #333; background: #1a1a2e; color: #fff; margin-bottom: 10px;">
                    <input type="number" id="trade-amount" placeholder="TL Miktarı" 
                           style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #333; background: #1a1a2e; color: #fff; margin-bottom: 10px;">
                    <button class="btn" onclick="executeTrade('buy')">🟢 AL</button>
                    <button class="btn btn-sell" onclick="executeTrade('sell')">🔴 SAT</button>
                </div>
            </div>
        </div>
        
        <!-- Piyasa Tablosu -->
        <div class="card" style="margin-top: 20px;">
            <h3>📈 CANLI PİYASA (BTCTurk)</h3>
            <div id="market-table">
                <table>
                    <thead>
                        <tr>
                            <th>Sembol</th>
                            <th>Fiyat (TL)</th>
                            <th>24s Değişim</th>
                            <th>Hacim</th>
                            <th>İşlem</th>
                        </tr>
                    </thead>
                    <tbody id="market-body">
                        <tr><td colspan="5" class="loading">Yükleniyor...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = '';
        
        async function fetchData(endpoint) {
            try {
                const resp = await fetch(API_BASE + endpoint);
                return await resp.json();
            } catch (e) {
                console.error('API Error:', e);
                return { success: false, error: e.message };
            }
        }
        
        async function updateStatus() {
            const data = await fetchData('/api/status');
            const el = document.getElementById('api-status');
            if (data.status === 'online') {
                el.textContent = '🟢 Sistem Aktif';
                el.className = 'api-status status-online';
            } else {
                el.textContent = '🔴 Bağlantı Hatası';
            }
        }
        
        async function updatePortfolio() {
            const data = await fetchData('/api/portfolio');
            const el = document.getElementById('portfolio-content');
            
            if (data.success && data.balances) {
                let html = '';
                let total = 0;
                
                for (const [asset, balance] of Object.entries(data.balances)) {
                    if (balance.total > 0.0001) {
                        html += `<div class="coin-row">
                            <span class="coin-name">${asset}</span>
                            <span>${balance.total.toFixed(6)}</span>
                        </div>`;
                    }
                }
                
                if (data.stats) {
                    html += `<div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #333;">
                        <div class="stat-label">Toplam İşlem: ${data.stats.total_trades || 0}</div>
                        <div class="stat-label">Net P&L: ₺${(data.stats.net_pnl || 0).toFixed(2)}</div>
                    </div>`;
                }
                
                el.innerHTML = html || '<p style="color: #888;">Bakiye bulunamadı</p>';
            } else {
                el.innerHTML = '<p style="color: #888;">API anahtarı gerekli</p>';
            }
        }
        
        async function updateSignals() {
            const data = await fetchData('/api/signals');
            const el = document.getElementById('signals-content');
            
            if (data.success && data.stats) {
                const s = data.stats;
                el.innerHTML = `
                    <div class="stat-value ${s.win_rate > 50 ? 'positive' : 'negative'}">%${s.win_rate.toFixed(1)}</div>
                    <div class="stat-label">Başarı Oranı</div>
                    <div style="margin-top: 15px;">
                        <span>✅ ${s.wins} Kazanç</span> | 
                        <span>❌ ${s.losses} Kayıp</span>
                    </div>
                    <div class="stat-label">Toplam: ${s.total_signals} sinyal | Aktif: ${s.active}</div>
                `;
            } else {
                el.innerHTML = '<p style="color: #888;">Veri yok</p>';
            }
        }
        
        async function updateStrategies() {
            const data = await fetchData('/api/strategies');
            const el = document.getElementById('strategies-content');
            
            if (data.success) {
                const active = data.active || [];
                if (active.length > 0) {
                    let html = '';
                    for (const strat of active) {
                        html += `<div class="coin-row">
                            <span>🟢 ${strat.name}</span>
                            <span class="positive">Aktif</span>
                        </div>`;
                    }
                    el.innerHTML = html;
                } else {
                    el.innerHTML = '<p style="color: #888;">Aktif strateji yok</p>';
                }
            } else {
                el.innerHTML = '<p style="color: #888;">Yükleniyor...</p>';
            }
        }
        
        async function updateMarket() {
            const data = await fetchData('/api/market');
            const tbody = document.getElementById('market-body');
            
            if (data.success && data.data) {
                let html = '';
                for (const coin of data.data.slice(0, 15)) {
                    const symbol = coin.pairNormalized.replace('_TRY', '');
                    const price = parseFloat(coin.last).toLocaleString('tr-TR', {minimumFractionDigits: 2});
                    const change = parseFloat(coin.dailyPercent);
                    const changeClass = change >= 0 ? 'positive' : 'negative';
                    const changeSign = change >= 0 ? '+' : '';
                    const volume = (parseFloat(coin.volume) / 1000000).toFixed(2);
                    
                    html += `<tr>
                        <td><strong>${symbol}</strong></td>
                        <td class="coin-price">₺${price}</td>
                        <td class="${changeClass}">${changeSign}${change.toFixed(2)}%</td>
                        <td>${volume}M</td>
                        <td>
                            <button class="btn" style="padding: 5px 10px; font-size: 12px;" onclick="quickAnalyze('${symbol}')">📊</button>
                        </td>
                    </tr>`;
                }
                tbody.innerHTML = html;
            } else {
                tbody.innerHTML = '<tr><td colspan="5">Veri alınamadı</td></tr>';
            }
        }
        
        async function executeTrade(side) {
            const symbol = document.getElementById('trade-symbol').value.toUpperCase() || 'BTC';
            const amount = parseFloat(document.getElementById('trade-amount').value) || 0;
            
            if (amount <= 0) {
                alert('Lütfen geçerli bir miktar girin');
                return;
            }
            
            if (!confirm(`${symbol} için ₺${amount} ${side === 'buy' ? 'ALIM' : 'SATIM'} yapılsın mı?`)) {
                return;
            }
            
            const resp = await fetch('/api/trade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    symbol: symbol,
                    side: side,
                    amount_tl: amount,
                    order_type: 'market'
                })
            });
            
            const data = await resp.json();
            
            if (data.success) {
                alert('✅ İşlem başarılı!');
                updatePortfolio();
            } else {
                alert('❌ Hata: ' + (data.error || 'Bilinmeyen hata'));
            }
        }
        
        async function quickAnalyze(symbol) {
            alert(`${symbol} analiz ediliyor...`);
            const data = await fetchData(`/api/analyze/${symbol}`);
            if (data.success) {
                alert(`${symbol} Skoru: ${data.analysis?.score || 'N/A'}/10`);
            }
        }
        
        // İlk yükleme
        updateStatus();
        updatePortfolio();
        updateSignals();
        updateStrategies();
        updateMarket();
        
        // Otomatik güncelleme
        setInterval(updateMarket, 30000);
        setInterval(updateSignals, 60000);
    </script>
</body>
</html>'''
    
    with open(templates_dir / 'dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)


create_dashboard_template()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
