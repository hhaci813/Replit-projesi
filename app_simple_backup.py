from flask import Flask, jsonify
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/')
def home():
    try:
        with open('static/advanced_dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>Hata: {e}</h1>"

@app.route('/api/btcturk-analysis')
def analysis():
    try:
        from btcturk_market_scanner import BTCTurkMarketScanner
        scanner = BTCTurkMarketScanner()
        return jsonify(scanner.get_analysis_json())
    except Exception as e:
        return jsonify({'assets': [], 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
