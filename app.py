from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import subprocess

app = Flask(__name__)
CORS(app)

def verileri_yukle():
    try:
        with open('veriler.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"portfoy": {}, "alerts": []}

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 YAPAY ZEKA YATIRIM ASİSTANI</title>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; }
            body { font-family: Arial; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #00ff00; margin: 20px 0; }
            .dashboard { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
            .card { background: #2a2a2a; padding: 20px; border-radius: 10px; border: 1px solid #00ff00; }
            .portfoy { grid-column: 1 / 3; }
            .metric { text-align: center; }
            button { background: #00ff00; color: #000; padding: 10px; border: none; border-radius: 5px; cursor: pointer; }
            input { background: #333; color: #fff; padding: 10px; margin: 10px 0; border: 1px solid #00ff00; border-radius: 5px; width: 100%; }
            .status { color: #00ff00; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 YAPAY ZEKA YATIRIM ASİSTANI - WEB DASHBOARD</h1>
            
            <div class="dashboard">
                <div class="card portfoy">
                    <h2>💼 Portföy</h2>
                    <div id="portfoy">Yükleniyor...</div>
                </div>
                
                <div class="card metric">
                    <h3>📊 Toplam Değer</h3>
                    <p id="toplam" style="font-size: 24px;">$0</p>
                </div>
                
                <div class="card metric">
                    <h3>📈 Kar/Zarar</h3>
                    <p id="karzarar" style="font-size: 24px; color: #00ff00;">+0%</p>
                </div>
                
                <div class="card" style="grid-column: 1 / 4;">
                    <h2>➕ Yeni Yatırım Ekle</h2>
                    <input type="text" id="sembol" placeholder="Sembol (AAPL)">
                    <input type="number" id="adet" placeholder="Adet">
                    <input type="number" id="maliyet" placeholder="Maliyet">
                    <button onclick="ekle()">Ekle</button>
                    <p id="message" class="status"></p>
                </div>
            </div>
        </div>
        
        <script>
            async function yenile() {
                const res = await fetch('/api/portfoy');
                const data = await res.json();
                
                let html = '<table style="width:100%">';
                html += '<tr><th>Sembol</th><th>Adet</th><th>Maliyet</th></tr>';
                
                for (let sembol in data.portfoy) {
                    const bilgi = data.portfoy[sembol];
                    html += `<tr><td>${sembol}</td><td>${bilgi.adet}</td><td>$${bilgi.maliyet}</td></tr>`;
                }
                html += '</table>';
                
                document.getElementById('portfoy').innerHTML = html;
            }
            
            async function ekle() {
                const sembol = document.getElementById('sembol').value;
                const adet = document.getElementById('adet').value;
                const maliyet = document.getElementById('maliyet').value;
                
                await fetch('/api/ekle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({sembol, adet, maliyet})
                });
                
                document.getElementById('message').textContent = '✅ Eklendi!';
                yenile();
            }
            
            yenile();
            setInterval(yenile, 5000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/portfoy')
def api_portfoy():
    veriler = verileri_yukle()
    return jsonify(veriler)

@app.route('/api/ekle', methods=['POST'])
def api_ekle():
    data = request.json
    veriler = verileri_yukle()
    veriler['portfoy'][data['sembol']] = {'adet': data['adet'], 'maliyet': data['maliyet']}
    
    with open('veriler.json', 'w') as f:
        json.dump(veriler, f)
    
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
