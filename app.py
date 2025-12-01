from flask import Flask, jsonify
app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/')
def home():
    try:
        with open('static/index.html', 'r') as f:
            return f.read()
    except:
        return "<!DOCTYPE html><html><body style='background:#1a1a1a;color:#00ff00'><h1>Dashboard açılıyor...</h1></body></html>"

@app.route('/api/btcturk-analysis')
def analysis():
    try:
        from btcturk_market_scanner import BTCTurkMarketScanner
        scanner = BTCTurkMarketScanner()
        return jsonify(scanner.get_analysis_json())
    except Exception as e:
        return jsonify({'assets': [], 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
