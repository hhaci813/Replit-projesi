"""Flask App - Dashboard + /btc API Integration"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
from dashboard_btc_widget import get_btc_widget_data

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Dashboard
@app.route('/', methods=['GET'])
def dashboard():
    """Main dashboard"""
    try:
        widget = get_btc_widget_data()
        return render_template('dashboard.html', btc_widget=widget)
    except:
        return '''
        <html><body style="background: #1a1a1a; color: white; font-family: Arial">
        <h1>📊 AKILLI YATIRIM ASİSTANI</h1>
        <h2>🔥 Kesin AL Önerileri</h2>
        <p>Sistem hazırlanıyor...</p>
        <a href="/api/btc/analysis">API Test →</a>
        </body></html>
        '''

# API - /btc Analysis
@app.route('/api/btc/analysis', methods=['GET'])
def api_btc():
    """GET /api/btc/analysis"""
    widget = get_btc_widget_data()
    return jsonify(widget)

# API - Telegram Message
@app.route('/api/btc/telegram', methods=['GET'])
def api_telegram_msg():
    """GET /api/btc/telegram"""
    widget = get_btc_widget_data()
    return jsonify({'message': widget['message']})

# API - Send to Telegram
@app.route('/api/btc/send', methods=['POST'])
def api_send_telegram():
    """POST /api/btc/send - Telegram'a gönder"""
    from src.utils.telegram_sender import send_to_telegram
    widget = get_btc_widget_data()
    success = send_to_telegram(widget['message'])
    return jsonify({'sent': success})

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': '1.0'})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 DASHBOARD STARTING")
    print("="*60)
    print("📱 APIs:")
    print("  • GET /api/btc/analysis")
    print("  • GET /api/btc/telegram")
    print("  • POST /api/btc/send")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

