"""BTCTurk Tüm Kripto'lar - Grafik Market Scanner"""
import requests
import json
from datetime import datetime

class BTCTurkMarketScanner:
    def __init__(self):
        self.api = "https://api.btcturk.com/api/v2"
    
    def get_all_tickers(self):
        """Tüm kripto'ları al"""
        try:
            resp = requests.get(f"{self.api}/ticker", timeout=10)
            if resp.status_code == 200:
                tickers = resp.json()['data']
                return tickers
        except:
            pass
        return []
    
    def analyze_all(self):
        """Tüm kripto'ları analiz et"""
        tickers = self.get_all_tickers()
        
        analyzed = []
        for ticker in tickers:
            try:
                pair = ticker.get('pair', '')
                price = float(ticker.get('last', 0))
                change = float(ticker.get('changePercent', 0))
                high = float(ticker.get('high24h', 0))
                low = float(ticker.get('low24h', 0))
                volume = float(ticker.get('volume', 0))
                
                if "TRY" in pair:
                    symbol = pair.replace("TRY", "")
                    
                    # Kategori
                    if change > 2:
                        category = "STRONG_UP"
                        emoji = "📈📈"
                    elif change > 0.5:
                        category = "UP"
                        emoji = "📈"
                    elif change < -2:
                        category = "STRONG_DOWN"
                        emoji = "📉📉"
                    elif change < -0.5:
                        category = "DOWN"
                        emoji = "📉"
                    else:
                        category = "NEUTRAL"
                        emoji = "➡️"
                    
                    analyzed.append({
                        'symbol': symbol,
                        'price': price,
                        'change': change,
                        'emoji': emoji,
                        'category': category,
                        'high': high,
                        'low': low,
                        'volume': volume
                    })
            except:
                pass
        
        return analyzed
    
    def get_html_dashboard(self):
        """HTML grafik dashboard"""
        data = self.analyze_all()
        
        # Kategoriye göre sırala
        strong_up = sorted([d for d in data if d['category'] == 'STRONG_UP'], key=lambda x: x['change'], reverse=True)
        up = sorted([d for d in data if d['category'] == 'UP'], key=lambda x: x['change'], reverse=True)
        down = sorted([d for d in data if d['category'] == 'DOWN'], key=lambda x: x['change'])
        strong_down = sorted([d for d in data if d['category'] == 'STRONG_DOWN'], key=lambda x: x['change'])
        neutral = sorted([d for d in data if d['category'] == 'NEUTRAL'], key=lambda x: x['change'], reverse=True)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BTCTurk Market Scanner</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ 
            font-family: 'Courier New', monospace; 
            background: #0a0a0a; 
            color: #00ff00; 
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{ color: #00ff00; text-align: center; margin: 20px 0; font-size: 28px; }}
        .time {{ text-align: center; color: #666; margin: 10px 0; }}
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(5, 1fr); 
            gap: 10px; 
            margin: 20px 0;
        }}
        .stat-box {{
            background: #1a1a1a;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #333;
            text-align: center;
        }}
        .stat-box h3 {{ color: #00ff00; margin: 5px 0; }}
        .stat-box .number {{ font-size: 24px; font-weight: bold; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ 
            font-size: 20px; 
            margin: 20px 0 10px 0; 
            padding: 10px;
            border-left: 4px solid;
            background: #1a1a1a;
        }}
        .strong-up {{ border-color: #00ff00; color: #00ff00; }}
        .up {{ border-color: #00dd00; color: #00dd00; }}
        .down {{ border-color: #ff3333; color: #ff3333; }}
        .strong-down {{ border-color: #ff0000; color: #ff0000; }}
        .neutral {{ border-color: #ffaa00; color: #ffaa00; }}
        
        .market-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
            gap: 10px;
        }}
        .market-card {{
            background: #1a1a1a;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #333;
            border-left: 3px solid;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .market-card:hover {{ transform: scale(1.02); }}
        .market-card .symbol {{ font-size: 16px; font-weight: bold; }}
        .market-card .price {{ font-size: 14px; margin: 5px 0; }}
        .market-card .change {{ font-size: 18px; font-weight: bold; }}
        
        .card-strong-up {{ border-color: #00ff00; }}
        .card-up {{ border-color: #00dd00; }}
        .card-down {{ border-color: #ff3333; }}
        .card-strong-down {{ border-color: #ff0000; }}
        .card-neutral {{ border-color: #ffaa00; }}
        
        .chart-container {{ background: #1a1a1a; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #333; }}
        .chart-container h2 {{ color: #00ff00; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 BTCTurk Market Scanner</h1>
        <div class="time">Canlı Veri - {datetime.now().strftime('%H:%M:%S')}</div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>📈 Yükselen</h3>
                <div class="number" style="color: #00ff00;">{len(strong_up) + len(up)}</div>
            </div>
            <div class="stat-box">
                <h3>📉 Düşen</h3>
                <div class="number" style="color: #ff0000;">{len(down) + len(strong_down)}</div>
            </div>
            <div class="stat-box">
                <h3>➡️ Yatay</h3>
                <div class="number" style="color: #ffaa00;">{len(neutral)}</div>
            </div>
            <div class="stat-box">
                <h3>🔥 En Yükselen</h3>
                <div class="number" style="color: #00ff00;">
                    {strong_up[0]['symbol'] if strong_up else 'N/A'}
                </div>
                <div style="color: #00ff00; font-size: 12px;">
                    {f"+{strong_up[0]['change']:.2f}%" if strong_up else ''}
                </div>
            </div>
            <div class="stat-box">
                <h3>❄️ En Düşen</h3>
                <div class="number" style="color: #ff0000;">
                    {strong_down[0]['symbol'] if strong_down else 'N/A'}
                </div>
                <div style="color: #ff0000; font-size: 12px;">
                    {f"{strong_down[0]['change']:.2f}%" if strong_down else ''}
                </div>
            </div>
        </div>
        
        <!-- STRONG UP -->
        {f'<div class="section"><div class="section-title strong-up">📈📈 GÜÇLÜ YÜKSELENLER (+2% üzeri)</div><div class="market-grid">' if strong_up else ''}
        {"".join(f'''<div class="market-card card-strong-up">
            <div class="symbol">{c["symbol"]}</div>
            <div class="price">₺{c["price"]:,.0f}</div>
            <div class="change" style="color: #00ff00;">+{c["change"]:.2f}%</div>
        </div>''' for c in strong_up)}
        {f'</div></div>' if strong_up else ''}
        
        <!-- UP -->
        {f'<div class="section"><div class="section-title up">📈 YÜKSELENLER (+0.5% ile +2%)</div><div class="market-grid">' if up else ''}
        {"".join(f'''<div class="market-card card-up">
            <div class="symbol">{c["symbol"]}</div>
            <div class="price">₺{c["price"]:,.0f}</div>
            <div class="change" style="color: #00dd00;">+{c["change"]:.2f}%</div>
        </div>''' for c in up)}
        {f'</div></div>' if up else ''}
        
        <!-- DOWN -->
        {f'<div class="section"><div class="section-title down">📉 DÜŞENLER (-0.5% ile -2%)</div><div class="market-grid">' if down else ''}
        {"".join(f'''<div class="market-card card-down">
            <div class="symbol">{c["symbol"]}</div>
            <div class="price">₺{c["price"]:,.0f}</div>
            <div class="change" style="color: #ff3333;">{c["change"]:.2f}%</div>
        </div>''' for c in down)}
        {f'</div></div>' if down else ''}
        
        <!-- STRONG DOWN -->
        {f'<div class="section"><div class="section-title strong-down">📉📉 GÜÇLÜ DÜŞENLER (-2% altı)</div><div class="market-grid">' if strong_down else ''}
        {"".join(f'''<div class="market-card card-strong-down">
            <div class="symbol">{c["symbol"]}</div>
            <div class="price">₺{c["price"]:,.0f}</div>
            <div class="change" style="color: #ff0000;">{c["change"]:.2f}%</div>
        </div>''' for c in strong_down)}
        {f'</div></div>' if strong_down else ''}
        
        <!-- NEUTRAL -->
        {f'<div class="section"><div class="section-title neutral">➡️ YATAY (-0.5% ile +0.5%)</div><div class="market-grid">' if neutral else ''}
        {"".join(f'''<div class="market-card card-neutral">
            <div class="symbol">{c["symbol"]}</div>
            <div class="price">₺{c["price"]:,.0f}</div>
            <div class="change" style="color: #ffaa00;">{c["change"]:+.2f}%</div>
        </div>''' for c in neutral)}
        {f'</div></div>' if neutral else ''}
        
        <!-- CHART -->
        <div class="chart-container">
            <h2>📊 Grafik - Yükselen vs Düşen</h2>
            <div id="chart" style="width: 100%; height: 400px;"></div>
            <script>
                const data = [{{
                    x: ['Yükselen', 'Düşen', 'Yatay'],
                    y: [{len(strong_up) + len(up)}, {len(down) + len(strong_down)}, {len(neutral)}],
                    type: 'bar',
                    marker: {{
                        color: ['#00ff00', '#ff0000', '#ffaa00']
                    }}
                }}];
                const layout = {{
                    title: 'Market Durumu',
                    plot_bgcolor: '#1a1a1a',
                    paper_bgcolor: '#0a0a0a',
                    font: {{ color: '#00ff00' }},
                    xaxis: {{ gridcolor: '#333' }},
                    yaxis: {{ gridcolor: '#333' }}
                }};
                Plotly.newPlot('chart', data, layout);
            </script>
        </div>
    </div>
</body>
</html>"""
        return html

# Test
if __name__ == "__main__":
    scanner = BTCTurkMarketScanner()
    data = scanner.analyze_all()
    print(f"✅ {len(data)} kripto tarandı")
    print(f"📈 Yükselen: {len([d for d in data if d['change'] > 0])}")
    print(f"📉 Düşen: {len([d for d in data if d['change'] < 0])}")
