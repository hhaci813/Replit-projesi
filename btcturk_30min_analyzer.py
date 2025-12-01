"""BTCTurk Her 30 dakika - Grafik Analiz Raporu"""
import requests
import json
from datetime import datetime
import numpy as np

class BTCTurk30MinAnalyzer:
    def __init__(self):
        self.api = "https://api.btcturk.com/api/v2"
        self.pairs = ["BTCTRY", "ETHTRY", "XRPTRY", "ADATRY", "SOLTRY"]
        self.history = {}
    
    def get_ticker_data(self, pair):
        """Ticker veri al"""
        try:
            resp = requests.get(f"{self.api}/ticker?pairSymbol={pair}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()['data'][0]
                return {
                    'pair': pair,
                    'price': float(data.get('last', 0)),
                    'change_24h_pct': float(data.get('changePercent', 0)),
                    'high': float(data.get('high24h', 0)),
                    'low': float(data.get('low24h', 0)),
                    'volume': float(data.get('volume', 0))
                }
        except:
            pass
        return None
    
    def analyze_signal(self, price_change):
        """Sinyal analizi"""
        if price_change > 2:
            return "📈 YÜKSELIYOR - GÜÇLÜ", "🟢"
        elif price_change > 0.5:
            return "📈 YÜKSELIYOR", "🟢"
        elif price_change < -2:
            return "📉 DÜŞÜYOR - GÜÇLÜ", "🔴"
        elif price_change < -0.5:
            return "📉 DÜŞÜYOR", "🔴"
        else:
            return "➡️ YATAY", "⚪"
    
    def generate_html_chart(self):
        """HTML grafik oluştur"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BTCTurk 30 Dakika Analiz</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #00ff00; text-align: center; }
        .header { background: #2a2a2a; padding: 15px; border-radius: 8px; border: 2px solid #00ff00; margin: 10px 0; }
        .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin: 20px 0; }
        .card { 
            background: #2a2a2a; 
            padding: 15px; 
            border-radius: 8px; 
            border-left: 4px solid; 
            text-align: center;
        }
        .up { border-color: #00ff00; }
        .down { border-color: #ff0000; }
        .neutral { border-color: #ffaa00; }
        .price { font-size: 24px; font-weight: bold; margin: 10px 0; }
        .change { font-size: 18px; margin: 5px 0; }
        .signal { font-size: 16px; margin: 10px 0; }
        .up-color { color: #00ff00; }
        .down-color { color: #ff0000; }
        .neutral-color { color: #ffaa00; }
        .chart-container { background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #00ff00; }
        .summary { background: #1a3a1a; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #00ff00; }
        .summary h2 { color: #00ff00; margin: 0 0 10px 0; }
        .summary p { margin: 8px 0; line-height: 1.6; }
        .timestamp { color: #888; font-size: 12px; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 BTCTurk 30 Dakika Analiz</h1>
        <div class="header">
            <h3 style="margin: 0;">Canlı Pazar Durumu - {time}</h3>
        </div>
        
        <div class="grid" id="cards"></div>
        
        <div class="summary">
            <h2>📈 ÖZET</h2>
            <div id="summary-text"></div>
        </div>
        
        <div class="chart-container">
            <h2>📊 24 Saat Grafik</h2>
            <div id="chart" style="width:100%;height:400px;"></div>
        </div>
        
        <div class="timestamp">⏰ {time}</div>
    </div>
    
    <script>
        // Veri yükle
        fetch('/api/btcturk-analysis')
            .then(r => r.json())
            .then(data => {
                // Kartları oluştur
                let html = '';
                data.assets.forEach(asset => {
                    const up = asset.change > 0;
                    const neutral = asset.change > -0.5 && asset.change < 0.5;
                    const className = up ? 'up' : (neutral ? 'neutral' : 'down');
                    const colorClass = up ? 'up-color' : (neutral ? 'neutral-color' : 'down-color');
                    
                    html += `
                        <div class="card ${className}">
                            <div style="font-size: 14px; color: #888;">${asset.symbol}</div>
                            <div class="price" style="color: #00ff00;">${asset.price.toFixed(2)}</div>
                            <div class="change" style="color: ${up ? '#00ff00' : (neutral ? '#ffaa00' : '#ff0000')};">${asset.change > 0 ? '📈' : (neutral ? '➡️' : '📉')} ${asset.change.toFixed(2)}%</div>
                            <div class="signal" style="color: ${up ? '#00ff00' : (neutral ? '#ffaa00' : '#ff0000')};">${asset.signal}</div>
                        </div>
                    `;
                });
                document.getElementById('cards').innerHTML = html;
                
                // Özet
                document.getElementById('summary-text').innerHTML = data.summary;
                
                // Grafik
                if (data.chart_data) {
                    Plotly.newPlot('chart', data.chart_data.data, data.chart_data.layout);
                }
            });
    </script>
</body>
</html>
"""
        return html
    
    def get_analysis_json(self):
        """JSON analiz raporu"""
        assets = []
        summary_items = []
        
        for pair in self.pairs:
            ticker = self.get_ticker_data(pair)
            if ticker:
                symbol = pair.replace("TRY", "")
                change = ticker['change_24h_pct']
                signal_text, color = self.analyze_signal(change)
                
                assets.append({
                    'symbol': symbol,
                    'pair': pair,
                    'price': ticker['price'],
                    'change': change,
                    'signal': signal_text,
                    'color': color,
                    'high': ticker['high'],
                    'low': ticker['low']
                })
                
                # Özet ekle
                if change > 1:
                    summary_items.append(f"✅ {symbol}: {change:+.2f}% 📈 YÜKSELIYOR")
                elif change < -1:
                    summary_items.append(f"⚠️ {symbol}: {change:+.2f}% 📉 DÜŞÜYOR")
        
        # Summary HTML
        summary_html = "<p>"
        for item in summary_items:
            summary_html += f"{item}<br>"
        summary_html += "</p>"
        
        # Grafik data
        chart_data = {
            'data': [{
                'x': [a['symbol'] for a in assets],
                'y': [a['change'] for a in assets],
                'type': 'bar',
                'marker': {
                    'color': ['#00ff00' if a['change'] > 0 else '#ff0000' for a in assets]
                }
            }],
            'layout': {
                'title': '24 Saat Değişim (%)',
                'plot_bgcolor': '#2a2a2a',
                'paper_bgcolor': '#1a1a1a',
                'font': {'color': '#fff'},
                'xaxis': {'gridcolor': '#444'},
                'yaxis': {'gridcolor': '#444'}
            }
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'assets': assets,
            'summary': summary_html,
            'chart_data': chart_data
        }
    
    def get_text_report(self):
        """Metin raporu"""
        analysis = self.get_analysis_json()
        
        report = f"""
📊 BTCTURK 30 DAKİKA ANALİZİ - {datetime.now().strftime('%H:%M:%S')}

"""
        
        rising = [a for a in analysis['assets'] if a['change'] > 0.5]
        falling = [a for a in analysis['assets'] if a['change'] < -0.5]
        neutral = [a for a in analysis['assets'] if -0.5 <= a['change'] <= 0.5]
        
        if rising:
            report += "📈 YÜKSELENLER:\n"
            for a in rising:
                report += f"   ✅ {a['symbol']}: ₺{a['price']:.0f} (+{a['change']:.2f}%)\n"
        
        if falling:
            report += "\n📉 DÜŞENLER:\n"
            for a in falling:
                report += f"   ⚠️ {a['symbol']}: ₺{a['price']:.0f} ({a['change']:.2f}%)\n"
        
        if neutral:
            report += "\n➡️ YATAY:\n"
            for a in neutral:
                report += f"   {a['symbol']}: ₺{a['price']:.0f} ({a['change']:+.2f}%)\n"
        
        report += f"\n⏰ Güncelleme: Her 30 dakika\n✅ Veri: BTCTurk Live API"
        
        return report

# Test
if __name__ == "__main__":
    analyzer = BTCTurk30MinAnalyzer()
    print(analyzer.get_text_report())
